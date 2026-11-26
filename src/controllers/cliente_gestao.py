import logging
import os
import time

import requests

from interfaces.notificador_partidas import NotificadorPartidas
from interfaces.solicitador_pareamento import SolicitadorPareamento
from models.partida import Partida

log = logging.getLogger(__name__)


class ClienteGestao(SolicitadorPareamento, NotificadorPartidas):
    """Adapter do gerenciador-de-partidas (fila e resultado)."""

    def __init__(self, base_url: str | None = None, tentativas: int = 3, espera_s: float = 1.0) -> None:
        self._base = (base_url or os.getenv("GESTAO_API_URL", "http://localhost:3000")).rstrip("/")
        self._tentativas = tentativas
        self._espera_s = espera_s

    def solicitar_pareamento(self, id_jogador: str) -> None:
        resp = requests.post(f"{self._base}/partidas/fila", json={"idJogador": id_jogador}, timeout=10)
        resp.raise_for_status()

    @staticmethod
    def montar_corpo(partida: Partida) -> dict:
        vencedor, perdedor = partida.resultado()
        j1, j2 = partida.jogadores
        return {
            "idPartida": partida.id,
            "idVencedor": vencedor.id,
            "idPerdedor": perdedor.id,
            # O gerenciador guarda a pontuação por posição (jogador 1 e jogador 2).
            "pontuacaoJogador1": partida.pontuacao(j1.id),
            "pontuacaoJogador2": partida.pontuacao(j2.id),
            "detalhes": partida.detalhes(),
        }

    def notificar_resultado(self, partida: Partida) -> None:
        # O gerenciador manda callbackUrl (POST /partidas/resultado); sem ela, usa a rota com id.
        url = partida.callback_url or f"{self._base}/partidas/{partida.id}/resultado"
        corpo = self.montar_corpo(partida)

        ultimo_erro: Exception | None = None
        for tentativa in range(1, self._tentativas + 1):
            try:
                resp = requests.post(url, json=corpo, timeout=10)
                resp.raise_for_status()
                return
            except requests.RequestException as e:
                ultimo_erro = e
                log.warning("Falha ao enviar resultado (%s/%s): %s", tentativa, self._tentativas, e)
                if tentativa < self._tentativas:
                    time.sleep(self._espera_s * tentativa)
        raise ultimo_erro
