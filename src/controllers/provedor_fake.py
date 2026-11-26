from interfaces.provedor_pokemon import ProvedorPokemon
from models.movimento import Movimento
from models.pokemon import Pokemon

ARTE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"

# id, nome, tipos, velocidade, golpes (nome, tipo, poder)
CATALOGO = [
    (1, "bulbasaur", ["grass", "poison"], 45,
     [("vine-whip", "grass", 45), ("razor-leaf", "grass", 55), ("tackle", "normal", 40), ("sludge-bomb", "poison", 90)]),
    (4, "charmander", ["fire"], 65,
     [("ember", "fire", 40), ("flamethrower", "fire", 90), ("scratch", "normal", 40), ("dragon-breath", "dragon", 60)]),
    (7, "squirtle", ["water"], 43,
     [("water-gun", "water", 40), ("bubble-beam", "water", 65), ("tackle", "normal", 40), ("bite", "dark", 60)]),
    (16, "pidgey", ["normal", "flying"], 56,
     [("gust", "flying", 40), ("wing-attack", "flying", 60), ("quick-attack", "normal", 40)]),
    (25, "pikachu", ["electric"], 90,
     [("thunder-shock", "electric", 40), ("thunderbolt", "electric", 90), ("quick-attack", "normal", 40), ("iron-tail", "steel", 100)]),
    (39, "jigglypuff", ["normal", "fairy"], 20,
     [("pound", "normal", 40), ("disarming-voice", "fairy", 40), ("body-slam", "normal", 85)]),
    (63, "abra", ["psychic"], 90,
     [("confusion", "psychic", 50), ("psybeam", "psychic", 65), ("shadow-ball", "ghost", 80)]),
    (66, "machop", ["fighting"], 35,
     [("karate-chop", "fighting", 50), ("cross-chop", "fighting", 100), ("rock-slide", "rock", 75)]),
    (74, "geodude", ["rock", "ground"], 20,
     [("rock-throw", "rock", 50), ("rock-slide", "rock", 75), ("earthquake", "ground", 100), ("tackle", "normal", 40)]),
    (92, "gastly", ["ghost", "poison"], 80,
     [("lick", "ghost", 30), ("shadow-ball", "ghost", 80), ("sludge-bomb", "poison", 90)]),
    (133, "eevee", ["normal"], 55,
     [("tackle", "normal", 40), ("quick-attack", "normal", 40), ("bite", "dark", 60), ("swift", "normal", 60)]),
    (147, "dratini", ["dragon"], 50,
     [("twister", "dragon", 40), ("dragon-pulse", "dragon", 85), ("aqua-tail", "water", 90)]),
]


class ProvedorFake(ProvedorPokemon):
    """Mesmo contrato do PokeApiProvider, mas com dados fixos em memória (LSP).

    Usado nos testes e no modo offline (BATALHA_OFFLINE=1).
    """

    def __init__(self) -> None:
        self._por_chave: dict[str, Pokemon] = {}
        for id_, nome, tipos, velocidade, golpes in CATALOGO:
            pokemon = Pokemon(id_, nome, tipos, velocidade,
                              [Movimento(*g) for g in golpes], ARTE.format(id_))
            self._por_chave[str(id_)] = pokemon
            self._por_chave[nome] = pokemon

    @property
    def ids(self) -> list[int]:
        return [item[0] for item in CATALOGO]

    def buscar(self, identificador: str | int) -> Pokemon | None:
        return self._por_chave.get(str(identificador).lower().strip())
