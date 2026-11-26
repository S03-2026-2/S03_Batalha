import threading

from interfaces.repositorio_partidas import RepositorioPartidas
from models.partida import Partida


class RepositorioPartidasMemoria(RepositorioPartidas):
    """Repository em memória. Trocar por banco = nova classe, sem mexer no ServicoBatalha."""

    def __init__(self) -> None:
        self._partidas: dict[str, Partida] = {}
        self._lock = threading.Lock()

    def salvar(self, partida: Partida) -> None:
        with self._lock:
            self._partidas[partida.id] = partida

    def buscar(self, id_partida: str) -> Partida | None:
        with self._lock:
            return self._partidas.get(str(id_partida))
