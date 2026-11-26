from models.carta import Carta

class Jogador:

    def __init__(self, id):
        self._id = id
        self._cartas: list[Carta] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def cartas(self) -> list[Carta]:
        return self._cartas

    @cartas.setter
    def cartas(self, cartas: list[Carta]) -> None:
        self._cartas = cartas
