from modelos.movimento import Movimento
from modelos.pokemon import Pokemon
from interfaces.provedor_pokemon import ProvedorPokemon
import requests

class PokeApiProvider(ProvedorPokemon):

    def __init__(self) -> None:
        self._cache_golpes: dict[str, dict] = {}

    def buscar(self, identificador: str | int) -> Pokemon | None:
        url = f"https://pokeapi.co/api/v2/pokemon/{str(identificador).lower().strip()}"
        resposta = requests.get(url, timeout=10)

        if resposta.status_code == 404:
            print("Pokémon não encontrado.")
            return None

        resposta.raise_for_status()
        dados = resposta.json()

        tipos = [t["type"]["name"] for t in dados["types"]]
        speed = self._extrair_stat(dados["stats"])
        movimentos = list(self._selecionar_moves(dados["moves"]))

        pokemon = Pokemon(dados["id"], dados["name"], tipos, speed, movimentos)

        return pokemon

    def _buscar_detalhes_golpe(self, url: str) -> dict | None:
        if url in self._cache_golpes:
            return self._cache_golpes[url]

        resposta = requests.get(url, timeout=10)
        if not resposta.ok:
            return None

        dados = resposta.json()
        detalhes = {
            "nome": dados["name"],
            "tipo": dados["type"]["name"],
            "categoria": dados["damage_class"]["name"],
            "poder": dados["power"]
        }
        self._cache_golpes[url] = detalhes
        return detalhes

    def _selecionar_moves(self, moves_raw: list[dict]) -> list[Movimento]:
        candidatos: list[dict] = []
        print(moves_raw)
        for entrada in moves_raw[:25]:
            url_golpe = entrada["move"]["url"]

            detalhes = self._buscar_detalhes_golpe(url_golpe)
            if not detalhes:
                continue

            if detalhes["poder"] is None:
                continue

            candidatos.append({
                **detalhes,
                "pontuacao": detalhes["poder"],
            })
        candidatos.sort(key=lambda g: g["pontuacao"], reverse=True)

        escolhidos: list[dict] = []
        nomes_vistos: set[str] = set()
        tipos_vistos: set[str] = set()
        for golpe in candidatos:
            if golpe["nome"] not in nomes_vistos and golpe["tipo"] not in tipos_vistos:
                escolhidos.append(golpe)
                nomes_vistos.add(golpe["nome"])
                tipos_vistos.add(golpe["tipo"])
            if len(escolhidos) == 4:
                break

        m1 = Movimento(escolhidos[0]["nome"], escolhidos[0]["tipo"], escolhidos[0]["poder"])
        m2 = Movimento(escolhidos[1]["nome"], escolhidos[1]["tipo"], escolhidos[1]["poder"])
        m3 = Movimento(escolhidos[2]["nome"], escolhidos[2]["tipo"], escolhidos[2]["poder"])
        m4 = Movimento(escolhidos[3]["nome"], escolhidos[3]["tipo"], escolhidos[3]["poder"])

        return [m1, m2, m3, m4]

    def _extrair_stat(self, stats_raw: list[dict]) -> int | None:
        for item in stats_raw:
            if item["stat"]["name"] == "speed":
                return item["base_stat"]
        return None

    def buscar_sprite(self, identificador: int | str) -> str | None:
        url = f"https://pokeapi.co/api/v2/pokemon/{str(identificador).lower().strip()}"
        resposta = requests.get(url, timeout=10)

        if resposta.status_code == 404:
            print("Pokémon não encontrado.")
            return None

        resposta.raise_for_status()
        dados = resposta.json()

        return dados["sprites"]["front_default"]

