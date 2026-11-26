import logging
import threading
from interfaces.acoes_jogador import AcoesJogador
from interfaces.iniciador_partida import IniciadorPartida
from models import partida
from services.calculadora_dano import CalculadoraDano
from models.carta import Carta
from models.jogada import Jogada
from models.jogador import Jogador
from models.movimento import Movimento
from models.partida import Partida
from controllers.poke_api_provider import PokeApiProvider
from controllers.cliente_dicas import ClienteDicas
from controllers.cliente_distribuicao import ClienteDistribuicao
from controllers.cliente_gestao import ClienteGestao

log = logging.getLogger(__name__)

class ServicoBatalha(IniciadorPartida, AcoesJogador):
    def __init__(self) -> None:
        self._pokemons = PokeApiProvider()
        self._cartas = ClienteDistribuicao()
        self._dicas = ClienteDicas()
        self._gestao = ClienteGestao()
        self._calculadora = CalculadoraDano()
        self._lock = threading.Lock()
        self._partidas: list[Partida] = None

    def solicitar_batalha(self, id_jogador: str) -> None:
        self._gestao.solicitar_pareamento(id_jogador)

    def iniciar_partida(
        self,
        jogadores: list[Jogador],
        id_partida: str | None = None,
        callback_url: str | None = None,
        ) -> None:
        self._partida = Partida(jogadores, id_partida, callback_url)
        if id_partida:
            with self._lock:
                if id_partida in self._partidas:
                    return
                self._partidas[id_partida] = self._partida

        try:
            for j in jogadores:
                cartas = self._cartas_jogador(j)
                j.cartas = cartas

            self._executar_batalha()
            self._gestao.notificar_resultado(self._partida)
        except Exception as e:
            log.exception("Falha na partida %s", id_partida)

    def partida(self, id_partida: str) -> Partida | None:
        return self._partidas.get(id_partida)

    def _cartas_jogador(self, jogador: Jogador):
        return self._cartas.cartas_do_jogador(jogador)

    def _executar_batalha(self) -> None:
        pass

    def escolher_carta(self, carta: Carta) -> None:
        pass

    def analisar_carta(self, carta: Carta) -> None:
        pass

    def escolher_movimento(self, movimento: Movimento) -> None:
        pass

    def solicitar_dica(self) -> None:
        pass

    def processar_rodada(self, a: Jogada, b: Jogada) -> None:
        pass

    def verificar_vencedor(self) -> None:
        pass
