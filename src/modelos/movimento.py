class Movimento:

    def __init__(self, nome: str, tipo: str, dano_base: int) -> None:
        self._nome = nome
        self._tipo = tipo
        self._dano_base = dano_base

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def dano(self) -> int:
        return self._dano_base