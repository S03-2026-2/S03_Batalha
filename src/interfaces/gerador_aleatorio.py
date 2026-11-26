from abc import ABC, abstractmethod


class GeradorAleatorio(ABC):
    """Abstração do sorteio (RNF04): nos testes injetamos valores fixos."""

    @abstractmethod
    def proximo(self) -> float:
        """Número em [0, 1)."""
