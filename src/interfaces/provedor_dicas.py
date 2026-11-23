from abc import ABC, abstractmethod

from modelos.carta import Carta


class ProvedorDicas(ABC):
    @abstractmethod
    def gerar_dica(self, mao: list[Carta]) -> str:
        pass
