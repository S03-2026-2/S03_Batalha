from abc import ABC, abstractmethod

from modelos.jogador import Jogador


class SolicitadorPareamento(ABC):
    @abstractmethod
    def solicitar_pareamento(self, jogador: Jogador) -> None:
        pass
