from models.movimento import Movimento


class Pokemon:

    def __init__(
        self,
        id: int,
        nome: str,
        tipos: list[str],
        velocidade: int,
        movimentos: list[Movimento],
        sprite: str | None = None,
    ) -> None:
        self._id = id
        self._nome = nome
        self._tipos = list(tipos)
        self._velocidade = velocidade
        self._movimentos = list(movimentos)
        self._sprite = sprite

    @property
    def id(self) -> int:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def tipos(self) -> list[str]:
        return list(self._tipos)

    @property
    def velocidade(self) -> int:
        return self._velocidade

    @property
    def movimentos(self) -> list[Movimento]:
        return list(self._movimentos)

    @property
    def sprite(self) -> str | None:
        return self._sprite

    def movimento(self, nome: str) -> Movimento | None:
        return next((m for m in self._movimentos if m.nome == nome), None)

    def para_dict(self) -> dict:
        return {
            "id": self._id,
            "nome": self._nome,
            "tipos": self.tipos,
            "velocidade": self._velocidade,
            "sprite": self._sprite,
            "movimentos": [m.para_dict() for m in self._movimentos],
        }
