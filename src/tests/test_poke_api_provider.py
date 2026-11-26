import pytest
import requests

from controllers.poke_api_provider import PokeApiProvider

def test_poke_api_provider_buscar():
    api_provider = PokeApiProvider()

    p = api_provider.buscar("25")

    assert p.nome == "pikachu"
    assert p.id == 25
    assert p.velocidade == 90

def test_poke_api_provider_detalhes():
    api_provider = PokeApiProvider()

    resultado = api_provider._buscar_detalhes_golpe('https://pokeapi.co/api/v2/move/87/')
    detalhes = {
        "nome": "thunder",
        "tipo": "electric",
        "categoria": "special",
        "poder": 110
    }

    assert detalhes == resultado

def test_poke_api_buscar_sprite():
    api_provider = PokeApiProvider()

    sprite = api_provider.buscar_sprite(25)

    assert sprite == 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png'

def test_poke_api_selecionar_pokemons():
    api_provider = PokeApiProvider()
    resposta = requests.get("https://pokeapi.co/api/v2/pokemon/25", timeout=10)

    resposta.raise_for_status()
    dados = resposta.json()

    movimentos = list(api_provider._selecionar_moves(dados["moves"]))

    assert movimentos[0].nome == 'mega-kick'
    assert movimentos[1].nome == 'thunder'
    assert movimentos[2].nome == 'surf'
    assert movimentos[3].nome == 'submission'

def test_poke_api_extrair_dados():
    api_provider = PokeApiProvider()
    resposta = requests.get("https://pokeapi.co/api/v2/pokemon/25", timeout=10)

    resposta.raise_for_status()
    dados = resposta.json()

    speed = api_provider._extrair_stat(dados["stats"])

    assert speed == 90