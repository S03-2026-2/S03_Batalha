from abc import ABC, abstractmethod

from models.carta import Carta
from models.jogador import Jogador


class FonteCartas(ABC):
    @abstractmethod
    def cartas_do_jogador(self, jogador: Jogador) -> list[Carta]:
        pass
