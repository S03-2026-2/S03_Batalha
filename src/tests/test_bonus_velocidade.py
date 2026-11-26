import pytest

from services.bonus_velocidade import BonusVelocidade
from tests.fakes import PROVEDOR

bonus = BonusVelocidade()
pikachu, squirtle = PROVEDOR.buscar("pikachu"), PROVEDOR.buscar("squirtle")


def test_mais_rapido_ganha_15_por_cento():
    assert bonus.aplicar(100, pikachu.movimentos[0], pikachu, squirtle) == pytest.approx(115)


def test_mais_lento_nao_ganha_bonus():
    assert bonus.aplicar(100, squirtle.movimentos[0], squirtle, pikachu) == 100


def test_empate_de_velocidade_nao_ganha_bonus():
    assert bonus.aplicar(100, pikachu.movimentos[0], pikachu, pikachu) == 100
