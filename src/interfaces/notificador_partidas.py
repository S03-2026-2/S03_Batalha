from abc import ABC, abstractmethod

from modelos.jogador import Jogador


class NotificadorPartidas(ABC):
    @abstractmethod
    def notificar_resultado(self, vencedor: Jogador, perdedor: Jogador) -> None:
        pass
