from models.movimento import Movimento
from models.pokemon import Pokemon


class Carta:
    """Carta do jogador. É só dado: não faz chamadas HTTP (o sprite já vem no Pokemon)."""

    def __init__(self, id: str, pokemon: Pokemon) -> None:
        self._id = str(id)
        self._pokemon = pokemon

    @property
    def id(self) -> str:
        return self._id

    @property
    def pokemon(self) -> Pokemon:
        return self._pokemon

    @property
    def sprite(self) -> str | None:
        return self._pokemon.sprite

    def obter_movimento(self, nome_movimento: str) -> Movimento | None:
        return self._pokemon.movimento(nome_movimento)

    def para_dict(self) -> dict:
        return {"id": self._id, "pokemon": self._pokemon.para_dict()}
