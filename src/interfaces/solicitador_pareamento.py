from abc import ABC, abstractmethod


class SolicitadorPareamento(ABC):
    @abstractmethod
    def solicitar_pareamento(self, id_jogador: str) -> None:
        pass
