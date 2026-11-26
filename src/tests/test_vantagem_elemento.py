import pytest
from controllers.poke_api_provider import PokeApiProvider
from services.vantagem_elemento import VantagemElemento
api_provider = PokeApiProvider()

def criar_dados(id1, id2):
    return api_provider.buscar(id1), api_provider.buscar(id2)

def test_bonus_velocidade():
    bonus = VantagemElemento()
    p1, p2 = criar_dados(25, 7)

    moves = p1.movimentos
    dano = bonus.aplicar(moves[1], p2)

    assert dano == 10