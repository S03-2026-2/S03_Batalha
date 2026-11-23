from modelos.pokemon import Pokemon
from infraestrutura.poke_api_provider import PokeApiProvider

provider = PokeApiProvider()

class Carta:

    def __init__(self, id: str, pokemon: Pokemon):
        self._id = id
        self._pokemon = pokemon
        self._sprite = provider.buscar_sprite(pokemon.id)

    @property
    def pokemon(self) -> Pokemon:
        return self._pokemon

    @property
    def sprite(self) -> str:
        return self._sprite
