from interfaces.acoes_jogador import AcoesJogador
from calculadora_dano import CalculadoraDano
from modelos.carta import Carta
from interfaces.fonte_cartas import FonteCartas
from interfaces.iniciador_partida import IniciadorPartida
from modelos.jogada import Jogada
from modelos.jogador import Jogador
from modelos.movimento import Movimento
from interfaces.notificador_partidas import NotificadorPartidas
from modelos.partida import Partida
from interfaces.provedor_dicas import ProvedorDicas
from interfaces.provedor_pokemon import ProvedorPokemon
from interfaces.solicitador_pareamento import SolicitadorPareamento


class ServicoBatalha(IniciadorPartida, AcoesJogador):
    def __init__(
        self,
        pokemons: ProvedorPokemon,
        cartas: FonteCartas,
        dicas: ProvedorDicas,
        pareamento: SolicitadorPareamento,
        notificador: NotificadorPartidas,
    ) -> None:
        self._pokemons: ProvedorPokemon = pokemons
        self._cartas: FonteCartas = cartas
        self._dicas: ProvedorDicas = dicas
        self._pareamento: SolicitadorPareamento = pareamento
        self._notificador: NotificadorPartidas = notificador
        self._calculadora: CalculadoraDano = CalculadoraDano()  # composição
        self._partida: Partida = Partida()  # composição

    def solicitar_batalha(self) -> None:
        pass

    def iniciar_partida(self, jogadores: list[Jogador]) -> None:
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
