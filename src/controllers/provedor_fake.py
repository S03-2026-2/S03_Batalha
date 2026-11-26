from models.pokemon import Pokemon
from interfaces.provedor_pokemon import ProvedorPokemon


class ProvedorFake(ProvedorPokemon):
    def buscar(self, nome: str) -> Pokemon:
        pass
