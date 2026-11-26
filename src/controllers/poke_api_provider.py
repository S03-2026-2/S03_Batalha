import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

from interfaces.provedor_pokemon import ProvedorPokemon
from models.movimento import Movimento
from models.pokemon import Pokemon

log = logging.getLogger(__name__)

URL_BASE = "https://pokeapi.co/api/v2"
GOLPES_ANALISADOS = 25
GOLPES_POR_POKEMON = 4
GOLPE_RESERVA = Movimento("struggle", "normal", 50)


class PokeApiProvider(ProvedorPokemon):
    """Adapter: traduz o JSON da PokéAPI para o nosso modelo (Pokemon/Movimento)."""

    # Golpes se repetem muito entre Pokémon: o cache é compartilhado por todas as instâncias.
    _cache_golpes: dict[str, dict | None] = {}
    _lock_cache = threading.Lock()

    def __init__(self, url_base: str = URL_BASE, timeout: float = 10, sessao: requests.Session | None = None) -> None:
        self._url_base = url_base.rstrip("/")
        self._timeout = timeout
        self._sessao = sessao or requests.Session()

    def buscar(self, identificador: str | int) -> Pokemon | None:
        resposta = self._sessao.get(
            f"{self._url_base}/pokemon/{str(identificador).lower().strip()}", timeout=self._timeout
        )
        if resposta.status_code == 404:
            return None
        resposta.raise_for_status()
        dados = resposta.json()

        return Pokemon(
            id=dados["id"],
            nome=dados["name"],
            tipos=[t["type"]["name"] for t in dados["types"]],
            velocidade=self._extrair_stat(dados["stats"], "speed"),
            movimentos=self._selecionar_moves(dados["moves"]),
            sprite=self._extrair_sprite(dados.get("sprites") or {}),
        )

    def buscar_sprite(self, identificador: str | int) -> str | None:
        pokemon = self.buscar(identificador)
        return pokemon.sprite if pokemon else None

    def _buscar_detalhes_golpe(self, url: str) -> dict | None:
        with self._lock_cache:
            if url in self._cache_golpes:
                return self._cache_golpes[url]
        try:
            resposta = self._sessao.get(url, timeout=self._timeout)
            if not resposta.ok:
                return None
            dados = resposta.json()
            detalhes = {
                "nome": dados["name"],
                "tipo": dados["type"]["name"],
                "categoria": (dados.get("damage_class") or {}).get("name"),
                "poder": dados.get("power"),
            }
        except (requests.RequestException, KeyError, ValueError):
            log.warning("Não foi possível ler o golpe %s", url)
            return None
        with self._lock_cache:
            self._cache_golpes[url] = detalhes
        return detalhes

    def _selecionar_moves(self, moves_raw: list[dict]) -> list[Movimento]:
        """Até 4 golpes com dano, preferindo os mais fortes e de tipos diferentes.

        Pokémon como Ditto ou Magikarp quase não têm golpe com dano: nesse caso
        sobra o golpe reserva (struggle, 50), em vez de quebrar a partida.
        """
        urls = [m["move"]["url"] for m in moves_raw[:GOLPES_ANALISADOS]]
        with ThreadPoolExecutor(max_workers=8) as pool:
            detalhes = list(pool.map(self._buscar_detalhes_golpe, urls))

        candidatos = sorted(
            (d for d in detalhes if d and d["poder"]),
            key=lambda d: d["poder"],
            reverse=True,
        )
        escolhidos: list[dict] = []
        tipos_vistos: set[str] = set()
        for golpe in candidatos:  # primeiro: um golpe forte de cada tipo
            if golpe["tipo"] not in tipos_vistos:
                escolhidos.append(golpe)
                tipos_vistos.add(golpe["tipo"])
        for golpe in candidatos:  # depois completa com os que sobraram
            if golpe not in escolhidos:
                escolhidos.append(golpe)
        escolhidos = escolhidos[:GOLPES_POR_POKEMON]

        if not escolhidos:
            return [GOLPE_RESERVA]
        return [Movimento(g["nome"], g["tipo"], g["poder"]) for g in escolhidos]

    @staticmethod
    def _extrair_stat(stats_raw: list[dict], nome: str) -> int:
        for item in stats_raw:
            if item["stat"]["name"] == nome:
                return item["base_stat"]
        return 0

    @staticmethod
    def _extrair_sprite(sprites: dict) -> str | None:
        arte = ((sprites.get("other") or {}).get("official-artwork") or {}).get("front_default")
        return arte or sprites.get("front_default")
