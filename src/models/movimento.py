class Movimento:
    """Golpe de um Pokémon. dano_base pode ser None quando a PokéAPI não informa poder."""

    def __init__(self, nome: str, tipo: str, dano_base: int | None) -> None:
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
    def dano(self) -> int | None:
        return self._dano_base

    def para_dict(self) -> dict:
        return {"nome": self._nome, "tipo": self._tipo, "danoBase": self._dano_base}
