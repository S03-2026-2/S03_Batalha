from modelos.carta import Carta
from interfaces.fonte_cartas import FonteCartas
from modelos.jogador import Jogador


class ClienteDistribuicao(FonteCartas):
    def cartas_do_jogador(self, jogador: Jogador) -> list[Carta]:
        pass
