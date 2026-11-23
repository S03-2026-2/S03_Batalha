from modelos.movimento import Movimento
from modelos.pokemon import Pokemon
from servicos.vantagem_elemento import VantagemElemento
from servicos.bonus_velocidade import BonusVelocidade

class CalculadoraDano:

    def __init__(self):
        self._bonus = BonusVelocidade()
        self._vantagem = VantagemElemento()

    def calcular(self, movimento: Movimento, atacante: Pokemon, defensor: Pokemon) -> float:
        return (movimento.dano + self._vantagem.aplicar(movimento, defensor) + self._bonus.aplicar(movimento, atacante))
