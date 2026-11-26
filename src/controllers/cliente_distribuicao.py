import logging
import random

import requests

from interfaces.fonte_cartas import FonteCartas
from interfaces.provedor_pokemon import ProvedorPokemon
from models.carta import Carta

log = logging.getLogger(__name__)

TAMANHO_MAO = 5


class ClienteDistribuicao(FonteCartas):
    """Adapter do serviço Distribuicao_de_Cartas.

    GET {base}/jogadores/{id}/cartas devolve [{carta_id, pokemon_id, nome_pokemon, ...}].
    Os atributos de combate (tipos, velocidade, golpes) vêm do ProvedorPokemon.
    """

    def __init__(self, base_url: str, provedor: ProvedorPokemon, tamanho_mao: int = TAMANHO_MAO,
                 timeout: float = 10) -> None:
        self._base = base_url.rstrip("/")
        self._provedor = provedor
        self._tamanho_mao = tamanho_mao
        self._timeout = timeout

    def cartas_do_jogador(self, id_jogador: str, id_partida: str) -> list[Carta]:
        resposta = requests.get(f"{self._base}/jogadores/{id_jogador}/cartas", timeout=self._timeout)
        resposta.raise_for_status()
        colecao = resposta.json()

        # Se o jogador tiver mais de 5 cartas, sorteia 5 (sempre as mesmas para a mesma partida).
        sorteio = random.Random(f"{id_partida}|{id_jogador}")
        if len(colecao) > self._tamanho_mao:
            colecao = sorteio.sample(colecao, self._tamanho_mao)

        cartas = []
        for item in colecao:
            pokemon = self._provedor.buscar(item["pokemon_id"])
            if pokemon is not None:
                cartas.append(Carta(item["carta_id"], pokemon))
        return cartas
