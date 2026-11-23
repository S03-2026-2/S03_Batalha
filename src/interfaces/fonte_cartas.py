from abc import ABC, abstractmethod

from modelos.carta import Carta
from modelos.jogador import Jogador


class FonteCartas(ABC):
    @abstractmethod
    def cartas_do_jogador(self, jogador: Jogador) -> list[Carta]:
        pass
