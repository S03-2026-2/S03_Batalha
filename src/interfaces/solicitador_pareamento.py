from abc import ABC, abstractmethod

from models.jogador import Jogador


class SolicitadorPareamento(ABC):
    @abstractmethod
    def solicitar_pareamento(self, id_jogador: str) -> None:
        pass
