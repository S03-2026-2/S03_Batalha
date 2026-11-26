"""Dublês de teste: implementam as mesmas interfaces das classes reais (LSP)."""
from controllers.fonte_cartas_local import FonteCartasLocal
from controllers.provedor_fake import ProvedorFake
from controllers.repositorio_memoria import RepositorioPartidasMemoria
from interfaces.fonte_cartas import FonteCartas
from interfaces.gerador_aleatorio import GeradorAleatorio
from interfaces.notificador_partidas import NotificadorPartidas
from interfaces.solicitador_pareamento import SolicitadorPareamento
from models.carta import Carta
from models.partida import Partida
from services.bonus_velocidade import BonusVelocidade
from services.calculadora_dano import CalculadoraDano
from services.dica_local import DicaLocal
from services.juiz_rodada import JuizRodada
from services.servico_batalha import ServicoBatalha
from services.vantagem_elemento import VantagemElemento

PROVEDOR = ProvedorFake()


def carta(nome: str, dono: str = "x") -> Carta:
    pokemon = PROVEDOR.buscar(nome)
    return Carta(f"{dono}:{pokemon.id}", pokemon)


class GeradorFixo(GeradorAleatorio):
    def __init__(self, *valores: float) -> None:
        self._valores = list(valores)

    def proximo(self) -> float:
        return self._valores.pop(0) if self._valores else 0.0


class MaosFixas(FonteCartas):
    def __init__(self, maos: dict[str, list[str]]) -> None:
        self._maos = maos

    def cartas_do_jogador(self, id_jogador: str, id_partida: str) -> list[Carta]:
        return [carta(n, id_jogador) for n in self._maos[id_jogador]]


class GestaoFake(SolicitadorPareamento, NotificadorPartidas):
    def __init__(self) -> None:
        self.fila: list[str] = []
        self.notificadas: list[Partida] = []

    def solicitar_pareamento(self, id_jogador: str) -> None:
        self.fila.append(id_jogador)

    def notificar_resultado(self, partida: Partida) -> None:
        self.notificadas.append(partida)


def calculadora() -> CalculadoraDano:
    return CalculadoraDano([VantagemElemento(), BonusVelocidade()])


def criar_servico(gerador: GeradorAleatorio, fonte: FonteCartas | None = None, gestao: GestaoFake | None = None):
    gestao = gestao or GestaoFake()
    calc = calculadora()
    servico = ServicoBatalha(
        fonte_cartas=fonte or FonteCartasLocal(PROVEDOR, PROVEDOR.ids),
        dicas=DicaLocal(calc),
        pareamento=gestao,
        notificador=gestao,
        juiz=JuizRodada(calc, gerador),
        repositorio=RepositorioPartidasMemoria(),
        executar_em_segundo_plano=lambda tarefa: tarefa(),  # síncrono nos testes
    )
    return servico, gestao
