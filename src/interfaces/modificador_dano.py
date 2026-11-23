from abc import ABC, abstractmethod

from modelos.movimento import Movimento


class ModificadorDano(ABC):
    @abstractmethod
    def aplicar(self, movimento: Movimento) -> float:
        pass
