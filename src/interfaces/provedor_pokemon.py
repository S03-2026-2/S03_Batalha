from abc import ABC, abstractmethod

from models.pokemon import Pokemon


class ProvedorPokemon(ABC):
    @abstractmethod
    def buscar(self, nome: str) -> Pokemon:
        pass
