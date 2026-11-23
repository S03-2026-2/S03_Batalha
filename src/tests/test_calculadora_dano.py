import pytest
from infraestrutura.poke_api_provider import PokeApiProvider
from servicos.calculadora_dano import CalculadoraDano
api_provider = PokeApiProvider()

def criar_dados(id1, id2):
    return api_provider.buscar(id1), api_provider.buscar(id2)

def test_bonus_velocidade():
    calculadora = CalculadoraDano()
    p1, p2 = criar_dados(25, 6)

    moves = p1.movimentos
    dano = calculadora.calcular(moves[0], p1, p2)

    assert dano == 129