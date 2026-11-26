import random

from interfaces.gerador_aleatorio import GeradorAleatorio


class GeradorAleatorioPadrao(GeradorAleatorio):
    def __init__(self, semente: int | None = None) -> None:
        self._random = random.Random(semente)

    def proximo(self) -> float:
        return self._random.random()
