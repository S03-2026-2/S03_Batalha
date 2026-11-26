from abc import ABC, abstractmethod

from models.partida import Partida


class IniciadorPartida(ABC):
    """Porta usada pela Gestão de Partidas (ISP)."""

    @abstractmethod
    def iniciar_partida(self, id_partida: str, id_jogador1: str, id_jogador2: str,
                        callback_url: str | None = None) -> Partida:
        pass
