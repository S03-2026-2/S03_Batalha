import logging
import threading
from collections.abc import Callable

from interfaces.acoes_jogador import AcoesJogador
from interfaces.fonte_cartas import FonteCartas
from interfaces.iniciador_partida import IniciadorPartida
from interfaces.notificador_partidas import NotificadorPartidas
from interfaces.provedor_dicas import ProvedorDicas
from interfaces.repositorio_partidas import RepositorioPartidas
from interfaces.solicitador_pareamento import SolicitadorPareamento
from models.carta import Carta
from models.erros import JogadaInvalida, PartidaNaoEncontrada
from models.jogador import Jogador
from models.partida import Partida, StatusPartida
from models.resultado_rodada import ResultadoRodada
from services.juiz_rodada import JuizRodada

log = logging.getLogger(__name__)

Tarefa = Callable[[], None]


def em_thread(tarefa: Tarefa) -> None:
    threading.Thread(target=tarefa, daemon=True).start()


class ServicoBatalha(IniciadorPartida, AcoesJogador):
    """Fachada do módulo: orquestra os casos de uso UC01–UC08.

    Recebe tudo pronto no construtor (DIP): só conhece interfaces e não sabe se do outro
    lado está a API real, um fake de teste ou um fallback.
    """

    def __init__(
        self,
        fonte_cartas: FonteCartas,
        dicas: ProvedorDicas,
        pareamento: SolicitadorPareamento,
        notificador: NotificadorPartidas,
        juiz: JuizRodada,
        repositorio: RepositorioPartidas,
        executar_em_segundo_plano: Callable[[Tarefa], None] = em_thread,
    ) -> None:
        self._cartas = fonte_cartas
        self._dicas = dicas
        self._pareamento = pareamento
        self._notificador = notificador
        self._juiz = juiz
        self._repositorio = repositorio
        self._segundo_plano = executar_em_segundo_plano
        self._lock = threading.RLock()

    # ---- UC01 -----------------------------------------------------------------
    def solicitar_batalha(self, id_jogador: str) -> None:
        self._pareamento.solicitar_pareamento(id_jogador)

    # ---- UC02 + UC03 ------------------------------------------------------------
    def iniciar_partida(self, id_partida: str, id_jogador1: str, id_jogador2: str,
                        callback_url: str | None = None) -> Partida:
        with self._lock:
            existente = self._repositorio.buscar(id_partida)
            if existente is not None:
                return existente  # a Gestão pode reenviar; não duplicamos a partida
            partida = Partida([Jogador(id_jogador1), Jogador(id_jogador2)], id_partida, callback_url)
            self._repositorio.salvar(partida)

        # Buscar cartas na PokéAPI demora; a Gestão recebe a resposta na hora.
        self._segundo_plano(lambda: self._preparar(partida))
        return partida

    def _preparar(self, partida: Partida) -> None:
        try:
            maos = {j.id: self._cartas.cartas_do_jogador(j.id, partida.id) for j in partida.jogadores}
            with self._lock:
                partida.iniciar(maos)
            log.info("Partida %s pronta: %s x %s", partida.id, *[j.id for j in partida.jogadores])
        except Exception as erro:
            log.exception("Falha ao preparar a partida %s", partida.id)
            with self._lock:
                partida.falhar(f"Não foi possível carregar as cartas: {erro}")

    # ---- consultas -------------------------------------------------------------
    def partida(self, id_partida: str) -> Partida:
        partida = self._repositorio.buscar(id_partida)
        if partida is None:
            raise PartidaNaoEncontrada(f"Partida {id_partida} não encontrada.")
        return partida

    # ---- UC05 -----------------------------------------------------------------
    def analisar_carta(self, id_partida: str, id_carta: str) -> Carta:
        partida = self.partida(id_partida)
        for jogador in partida.jogadores:
            carta = jogador.selecionar_carta(id_carta)
            if carta is not None:
                return carta
        raise JogadaInvalida("Carta não encontrada nesta partida.")

    # ---- UC06 -----------------------------------------------------------------
    def solicitar_dica(self, id_partida: str, id_jogador: str) -> str:
        partida = self.partida(id_partida)
        if partida.jogador(id_jogador) is None:
            raise JogadaInvalida("Este jogador não pertence à partida.")
        if partida.status != StatusPartida.EM_ANDAMENTO:
            raise JogadaInvalida("A partida não está em andamento.")
        return self._dicas.gerar_dica(partida, id_jogador)

    # ---- UC04 + UC07 -----------------------------------------------------------
    def jogar(self, id_partida: str, id_jogador: str, id_carta: str | None,
              nome_movimento: str) -> ResultadoRodada | None:
        with self._lock:
            partida = self.partida(id_partida)
            partida.registrar_jogada(id_jogador, id_carta, nome_movimento)
            if not partida.rodada_completa():
                return None
            resultado = self.processar_rodada(partida)

        if partida.terminou():
            self._segundo_plano(lambda: self.verificar_vencedor(partida))
        return resultado

    def processar_rodada(self, partida: Partida) -> ResultadoRodada:
        jogada1, jogada2 = partida.jogadas_da_rodada()
        resultado = self._juiz.resolver(partida.turno, jogada1, jogada2)
        partida.registrar_vitoria(resultado)
        log.info("Partida %s rodada %s: venceu %s", partida.id, resultado.numero, resultado.id_vencedor)
        return resultado

    # ---- UC08 -----------------------------------------------------------------
    def verificar_vencedor(self, partida: Partida) -> None:
        try:
            self._notificador.notificar_resultado(partida)
            partida.notificacao = "ENVIADA"
        except Exception as erro:
            log.exception("Não foi possível notificar a Gestão sobre a partida %s", partida.id)
            partida.notificacao = f"FALHOU: {erro}"
