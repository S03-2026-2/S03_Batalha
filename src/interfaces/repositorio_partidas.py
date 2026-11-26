from abc import ABC, abstractmethod

from models.partida import Partida


class RepositorioPartidas(ABC):
    @abstractmethod
    def salvar(self, partida: Partida) -> None:
        pass

    @abstractmethod
    def buscar(self, id_partida: str) -> Partida | None:
        pass
