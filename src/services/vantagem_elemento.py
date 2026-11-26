from interfaces.modificador_dano import ModificadorDano
from models.movimento import Movimento
from models.pokemon import Pokemon

SUPER_EFETIVO = 2.0
POUCO_EFETIVO = 0.5
NEUTRO = 1.0

# Tipo do golpe -> tipos do defensor que recebem dano dobrado.
SUPER_EFETIVO_CONTRA: dict[str, set[str]] = {
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
    "fairy": {"fighting", "dragon", "dark"},
}

# Tipo do golpe -> tipos do defensor que recebem metade do dano.
# As imunidades do jogo original (ex.: normal -> ghost) também entram aqui como 0.5x,
# porque a força precisa ser > 0 para o sorteio ponderado (RN04).
POUCO_EFETIVO_CONTRA: dict[str, set[str]] = {
    "normal": {"rock", "steel", "ghost"},
    "fire": {"fire", "water", "rock", "dragon"},
    "water": {"water", "grass", "dragon"},
    "electric": {"electric", "grass", "dragon", "ground"},
    "grass": {"fire", "grass", "poison", "flying", "bug", "dragon", "steel"},
    "ice": {"fire", "water", "ice", "steel"},
    "fighting": {"poison", "flying", "psychic", "bug", "fairy", "ghost"},
    "poison": {"poison", "ground", "rock", "ghost", "steel"},
    "ground": {"grass", "bug", "flying"},
    "flying": {"electric", "rock", "steel"},
    "psychic": {"psychic", "steel", "dark"},
    "bug": {"fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"},
    "rock": {"fighting", "ground", "steel"},
    "ghost": {"dark", "normal"},
    "dragon": {"steel", "fairy"},
    "dark": {"fighting", "dark", "fairy"},
    "steel": {"fire", "water", "electric", "steel"},
    "fairy": {"fire", "poison", "steel"},
}


class VantagemElemento(ModificadorDano):
    """RN03 – Modificador 1: compara o tipo do golpe com cada tipo do defensor.

    Defensor com dois tipos multiplica os dois fatores (ex.: elétrico contra água/voador = 4x).
    """

    def fator(self, tipo_golpe: str, tipos_defensor: list[str]) -> float:
        fator = NEUTRO
        for tipo in tipos_defensor:
            if tipo in SUPER_EFETIVO_CONTRA.get(tipo_golpe, set()):
                fator *= SUPER_EFETIVO
            elif tipo in POUCO_EFETIVO_CONTRA.get(tipo_golpe, set()):
                fator *= POUCO_EFETIVO
        return fator

    def aplicar(self, dano: float, movimento: Movimento, atacante: Pokemon, defensor: Pokemon) -> float:
        return dano * self.fator(movimento.tipo, defensor.tipos)
