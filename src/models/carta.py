from models.pokemon import Pokemon
from controllers.poke_api_provider import PokeApiProvider

class Carta:

    def __init__(self, id: str, pokemon: Pokemon):
        self._id = id
        self._pokemon = pokemon
        provider = PokeApiProvider()
        self._sprite = provider.buscar_sprite(pokemon.id)

    @property
    def id(self) -> str:
        return self._id

    @property
    def pokemon(self) -> Pokemon:
        return self._pokemon

    @property
    def sprite(self) -> str:
        return self._sprite
