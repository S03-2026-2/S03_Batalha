from modelos.jogador import Jogador
from interfaces.notificador_partidas import NotificadorPartidas
from interfaces.solicitador_pareamento import SolicitadorPareamento


class ClienteGestao(SolicitadorPareamento, NotificadorPartidas):
    def solicitar_pareamento(self, jogador: Jogador) -> None:
        pass

    def notificar_resultado(self, vencedor: Jogador, perdedor: Jogador) -> None:
        pass
