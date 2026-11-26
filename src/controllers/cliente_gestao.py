from models.jogador import Jogador
from models.partida import Partida
from interfaces.notificador_partidas import NotificadorPartidas
from interfaces.solicitador_pareamento import SolicitadorPareamento
import os, requests, logging, time


log = logging.getLogger(__name__)

class ClienteGestao(SolicitadorPareamento, NotificadorPartidas):

    def __init__(self, base_url: str | None = None, tentativas: int = 3, espera_s: float = 1.0):
        self._base = (base_url or os.getenv("GESTAO_API_URL", "http://localhost:3000")).rstrip("/")
        self._tentativas = tentativas
        self._espera_s = espera_s

    def solicitar_pareamento(self, id_jogador: str) -> None:
        resp = requests.post(
            f"{self._base}/partidas/fila",
            json={"idJogador": id_jogador},
            timeout=10,
        )
        resp.raise_for_status()

    def notificar_resultado(self, partida: Partida) -> None:
        if not partida.callback_url:
            raise ValueError("Partida sem callback_url: nao ha para onde enviar o resultado.")

        vencedor, perdedor = partida.resultado()
        corpo = {
            "idPartida": partida.id,
            "idVencedor": vencedor.id,
            "idPerdedor": perdedor.id,
            "pontuacaoJogador1": partida.pontuacao(vencedor),
            "pontuacaoJogador2": partida.pontuacao(perdedor),
            "detalhes": partida.detalhes(),
        }

        ultimo_erro: Exception | None = None
        for tentativa in range(1, self._tentativas + 1):
            try:
                resp = requests.post(partida.callback_url, json=corpo, timeout=10)
                resp.raise_for_status()
                return
            except requests.RequestException as e:
                ultimo_erro = e
                log.warning("Falha ao enviar resultado (%s/%s): %s", tentativa, self._tentativas, e)
                if tentativa < self._tentativas:
                    time.sleep(self._espera_s * tentativa)
        raise ultimo_erro
