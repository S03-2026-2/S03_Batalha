from abc import ABC, abstractmethod

from models.jogador import Jogador


class IniciadorPartida(ABC):
    @abstractmethod
    def iniciar_partida(self, jogadores: list[Jogador]) -> None:
        pass
