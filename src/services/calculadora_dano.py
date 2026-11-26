from interfaces.modificador_dano import ModificadorDano
from models.movimento import Movimento
from models.pokemon import Pokemon

DANO_PADRAO = 50  # golpe sem poder base na PokéAPI


class CalculadoraDano:
    """Calcula a força S de um golpe aplicando, em sequência, todos os modificadores injetados.

    Não conhece nenhuma regra concreta: para criar uma regra nova (clima, STAB...) basta
    escrever outra classe ModificadorDano e passar na lista (OCP + Strategy).
    """

    def __init__(self, modificadores: list[ModificadorDano], dano_padrao: float = DANO_PADRAO) -> None:
        self._modificadores = list(modificadores)
        self._dano_padrao = dano_padrao

    def calcular(self, movimento: Movimento, atacante: Pokemon, defensor: Pokemon) -> float:
        dano = float(movimento.dano or self._dano_padrao)
        for modificador in self._modificadores:
            dano = modificador.aplicar(dano, movimento, atacante, defensor)
        return dano
