from modelos.movimento import Movimento
from interfaces.modificador_dano import ModificadorDano
from modelos.pokemon import Pokemon

FRAQUEZAS_POR_TIPO: dict[str, set[str]] = {
    "fire": {"grass", "ice", "bug", "steel"},
    "water": {"fire", "ground", "rock"},
    "electric": {"water", "flying"},
    "grass": {"water", "ground", "rock"},
    "ice": {"grass", "ground", "flying", "dragon"},
    "fighting": {"normal", "ice", "rock", "dark", "steel"},
    "poison": {"grass", "fairy"},
    "ground": {"fire", "electric", "poison", "rock", "steel"},
    "flying": {"grass", "fighting", "bug"},
    "psychic": {"fighting", "poison"},
    "bug": {"grass", "psychic", "dark"},
    "rock": {"fire", "ice", "flying", "bug"},
    "ghost": {"psychic", "ghost"},
    "dragon": {"dragon"},
    "dark": {"psychic", "ghost"},
    "steel": {"ice", "rock", "fairy"},
    "fairy": {"fighting", "dragon", "dark"}
}

class VantagemElemento(ModificadorDano):
    def aplicar(self, movimento: Movimento, defensor: Pokemon) -> float:
        bonus = sum(10 for t in defensor.tipos if t in FRAQUEZAS_POR_TIPO.get(movimento.tipo, set()))

        return bonus
