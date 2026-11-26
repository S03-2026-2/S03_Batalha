from abc import ABC, abstractmethod

from models.partida import Partida


class ProvedorDicas(ABC):
    @abstractmethod
    def gerar_dica(self, partida: Partida, id_jogador: str) -> str:
        pass
