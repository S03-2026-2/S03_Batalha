import random

from models.carta import Carta
from interfaces.fonte_cartas import FonteCartas
from models.jogador import Jogador
from controllers.poke_api_provider import PokeApiProvider


class ClienteDistribuicao(FonteCartas):
    def cartas_do_jogador(self, jogador: Jogador) -> list[Carta]:
        self._cartas: list[Carta] = []
        pokeapi = PokeApiProvider()
        for i in range(5):
            pokemon = pokeapi.buscar(random.randint(1, 151))
            carta = Carta(pokemon)
            self._cartas.append(carta)

        return self._cartas
