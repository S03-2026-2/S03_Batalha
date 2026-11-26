from abc import ABC, abstractmethod

from models.movimento import Movimento


class ModificadorDano(ABC):
    @abstractmethod
    def aplicar(self, movimento: Movimento) -> float:
        pass
