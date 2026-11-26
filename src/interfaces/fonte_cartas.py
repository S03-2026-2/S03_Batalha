from abc import ABC, abstractmethod

from models.carta import Carta


class FonteCartas(ABC):
    @abstractmethod
    def cartas_do_jogador(self, id_jogador: str, id_partida: str) -> list[Carta]:
        pass
