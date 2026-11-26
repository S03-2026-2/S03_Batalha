import pytest

from interfaces.modificador_dano import ModificadorDano
from models.movimento import Movimento
from services.calculadora_dano import CalculadoraDano
from services.juiz_rodada import JuizRodada
from tests.fakes import PROVEDOR, GeradorFixo, calculadora

squirtle, charmander = PROVEDOR.buscar("squirtle"), PROVEDOR.buscar("charmander")


def test_exemplo_da_documentacao_rn04():
    calc = calculadora()
    s1 = calc.calcular(squirtle.movimento("water-gun"), squirtle, charmander)
    s2 = calc.calcular(charmander.movimento("ember"), charmander, squirtle)
    assert s1 == 80
    assert s2 == pytest.approx(23)
    assert JuizRodada(calc, GeradorFixo()).probabilidade(s1, s2) == pytest.approx(0.7767, abs=1e-4)


def test_golpe_sem_poder_usa_dano_padrao():
    sem_poder = Movimento("splash", "normal", None)
    assert CalculadoraDano([]).calcular(sem_poder, squirtle, charmander) == 50


def test_nova_regra_entra_sem_alterar_a_calculadora():
    class Clima(ModificadorDano):  # OCP: regra nova é só uma classe nova
        def aplicar(self, dano, movimento, atacante, defensor):
            return dano * 1.5 if movimento.tipo == "fire" else dano

    calc = CalculadoraDano([Clima()])
    assert calc.calcular(charmander.movimento("ember"), charmander, squirtle) == 60
