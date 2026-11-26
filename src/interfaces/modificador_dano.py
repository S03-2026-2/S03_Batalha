from abc import ABC, abstractmethod

from models.movimento import Movimento
from models.pokemon import Pokemon


class ModificadorDano(ABC):
    """Regra que ajusta a força de um golpe. Nova regra = nova classe (OCP)."""

    @abstractmethod
    def aplicar(self, dano: float, movimento: Movimento, atacante: Pokemon, defensor: Pokemon) -> float:
        """Recebe o dano acumulado e devolve o dano modificado."""
