from abc import ABC, abstractmethod

from modelos.pokemon import Pokemon


class ProvedorPokemon(ABC):
    @abstractmethod
    def buscar(self, nome: str) -> Pokemon:
        pass
