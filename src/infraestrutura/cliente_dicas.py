from modelos.carta import Carta
from interfaces.provedor_dicas import ProvedorDicas


class ClienteDicas(ProvedorDicas):
    def gerar_dica(self, mao: list[Carta]) -> str:
        pass
