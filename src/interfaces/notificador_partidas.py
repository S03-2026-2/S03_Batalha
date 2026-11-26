from abc import ABC, abstractmethod

from models.partida import Partida


class NotificadorPartidas(ABC):
    @abstractmethod
    def notificar_resultado(self, partida: Partida) -> None:
        pass
