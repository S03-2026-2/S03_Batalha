from modelos.movimento import Movimento
from interfaces.modificador_dano import ModificadorDano
from modelos.pokemon import Pokemon


class BonusVelocidade(ModificadorDano):
    def aplicar(self, movimento: Movimento, atacante: Pokemon, bonus: float = 0.1) -> float:
        return bonus * atacante.velocidade
