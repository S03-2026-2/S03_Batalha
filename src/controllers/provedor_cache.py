import threading

from interfaces.provedor_pokemon import ProvedorPokemon
from models.pokemon import Pokemon


class ProvedorPokemonComCache(ProvedorPokemon):
    """Decorator: envolve qualquer ProvedorPokemon e guarda o que já foi buscado.

    Quem usa continua vendo só um ProvedorPokemon (LSP); o PokeApiProvider não muda (OCP).
    """

    def __init__(self, provedor: ProvedorPokemon) -> None:
        self._provedor = provedor
        self._cache: dict[str, Pokemon | None] = {}
        self._lock = threading.Lock()

    def buscar(self, identificador: str | int) -> Pokemon | None:
        chave = str(identificador).lower().strip()
        with self._lock:
            if chave in self._cache:
                return self._cache[chave]
        pokemon = self._provedor.buscar(identificador)
        with self._lock:
            self._cache[chave] = pokemon
            if pokemon is not None:  # mesma entrada por número e por nome
                self._cache[str(pokemon.id)] = pokemon
                self._cache[pokemon.nome] = pokemon
        return pokemon
