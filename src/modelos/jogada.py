from carta import Carta
from jogador import Jogador
from movimento import Movimento

class Jogada:

    def __init__(self, jogador: Jogador, carta: Carta, movimento: Movimento):
        self.jogador = jogador
        self.carta = carta
        self.movimento = movimento



