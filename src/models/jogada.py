from models.carta import Carta
from models.jogador import Jogador
from models.movimento import Movimento


class Jogada:

    def __init__(self, jogador: Jogador, carta: Carta, movimento: Movimento) -> None:
        self.jogador = jogador
        self.carta = carta
        self.movimento = movimento
