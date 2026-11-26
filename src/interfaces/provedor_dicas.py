from abc import ABC, abstractmethod

from models.carta import Carta


class ProvedorDicas(ABC):
    @abstractmethod
    def gerar_dica(self, mao: list[Carta]) -> str:
        pass
