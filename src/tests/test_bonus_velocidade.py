import pytest
from infraestrutura.poke_api_provider import PokeApiProvider
from servicos.bonus_velocidade import BonusVelocidade
api_provider = PokeApiProvider()

def criar_dados(id1):
    return api_provider.buscar(id1)

def test_bonus_velocidade():
    bonus = BonusVelocidade()
    pokemon = criar_dados(25)

    moves = pokemon.movimentos
    dano = bonus.aplicar(moves[0], pokemon)

    assert dano == 9