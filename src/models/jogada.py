from models.carta import Carta
from models.jogador import Jogador
from models.movimento import Movimento

class Jogada:

    def __init__(self, carta: Carta, movimento: Movimento, jogador: Jogador | None = None):
        self.carta = carta
        self.movimento = movimento
        self.jogador = jogador
