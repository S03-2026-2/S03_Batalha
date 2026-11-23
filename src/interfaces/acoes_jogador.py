from abc import ABC, abstractmethod

from modelos.carta import Carta
from modelos.movimento import Movimento


class AcoesJogador(ABC):
    @abstractmethod
    def solicitar_batalha(self) -> None:
        pass

    @abstractmethod
    def escolher_carta(self, carta: Carta) -> None:
        pass

    @abstractmethod
    def analisar_carta(self, carta: Carta) -> None:
        pass

    @abstractmethod
    def escolher_movimento(self, movimento: Movimento) -> None:
        pass

    @abstractmethod
    def solicitar_dica(self) -> None:
        pass
