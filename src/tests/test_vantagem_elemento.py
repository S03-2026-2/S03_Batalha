import pytest

from services.vantagem_elemento import VantagemElemento
from tests.fakes import PROVEDOR

vantagem = VantagemElemento()


@pytest.mark.parametrize("golpe, defensor, esperado", [
    ("water", ["fire"], 2.0),          # super efetivo
    ("fire", ["water"], 0.5),          # pouco efetivo
    ("normal", ["normal"], 1.0),       # neutro
    ("electric", ["water", "flying"], 4.0),  # dois tipos fracos
    ("water", ["rock", "ground"], 4.0),
    ("grass", ["water", "dragon"], 1.0),     # 2.0 x 0.5
    ("normal", ["ghost"], 0.5),        # imunidade vira 0.5 para a força nunca ser 0
    ("ground", ["flying"], 0.5),
])
def test_fator_por_tipo(golpe, defensor, esperado):
    assert vantagem.fator(golpe, defensor) == esperado


def test_aplicar_multiplica_o_dano_acumulado():
    squirtle, charmander = PROVEDOR.buscar("squirtle"), PROVEDOR.buscar("charmander")
    water_gun = squirtle.movimento("water-gun")
    assert vantagem.aplicar(40, water_gun, squirtle, charmander) == 80
