from interfaces.modificador_dano import ModificadorDano
from models.movimento import Movimento
from models.pokemon import Pokemon


class BonusVelocidade(ModificadorDano):
    """RN03 – Modificador 2: +15% se o atacante for mais rápido que o defensor."""

    def __init__(self, bonus: float = 1.15) -> None:
        self._bonus = bonus

    def aplicar(self, dano: float, movimento: Movimento, atacante: Pokemon, defensor: Pokemon) -> float:
        if (atacante.velocidade or 0) > (defensor.velocidade or 0):
            return dano * self._bonus
        return dano
