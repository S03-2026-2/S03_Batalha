from modelos.carta import Carta

class Jogador:

    def __init__(self, id: str, nome: str, mao: list[Carta]):
        self._id = id
        self._nome = nome
        self._mao = mao

    @property
    def id(self) -> str:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def mao(self) -> list[Carta]:
        return self._mao
