from modelos.movimento import Movimento

class Pokemon:

    def __init__(self, id, nome, tipo, velocidade, movimentos):
        self._id = id
        self._nome = nome
        self._tipo = tipo
        self._velocidade = velocidade
        self._movimentos = movimentos

    @property
    def id(self) -> int:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def tipos(self) -> str:
        return self._tipo

    @property
    def velocidade(self) -> int:
        return self._velocidade

    @property
    def movimentos(self) -> list[Movimento]:
        return self._movimentos
