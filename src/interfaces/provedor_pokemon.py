from abc import ABC, abstractmethod

from models.pokemon import Pokemon


class ProvedorPokemon(ABC):
    @abstractmethod
    def buscar(self, identificador: str | int) -> Pokemon | None:
        """Busca por nome ou número da Pokédex. None se não existir."""
