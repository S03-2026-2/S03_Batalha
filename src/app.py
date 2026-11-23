from infraestrutura.poke_api_provider import PokeApiProvider
from modelos.carta import Carta
api_provider = PokeApiProvider()

p = api_provider.buscar("25")
print("Nome: ", p.nome)
print("Tipos: ", p.tipos)
print("Velocidade: ", p.velocidade)
for i in p.movimentos:
    print(f"Nome: {i.nome}; Tipo: {i.tipo}; Dano: {i.dano}")

carta = Carta(0, p)
print(carta.sprite)
