from abc import ABC, abstractmethod

from models.carta import Carta
from models.partida import Partida
from models.resultado_rodada import ResultadoRodada


class AcoesJogador(ABC):
    """Porta usada pelos jogadores (ISP)."""

    @abstractmethod
    def solicitar_batalha(self, id_jogador: str) -> None:
        pass

    @abstractmethod
    def analisar_carta(self, id_partida: str, id_carta: str) -> Carta:
        pass

    @abstractmethod
    def jogar(self, id_partida: str, id_jogador: str, id_carta: str | None,
              nome_movimento: str) -> ResultadoRodada | None:
        """Escolhe carta + movimento. Devolve o resultado se a jogada fechou a rodada."""

    @abstractmethod
    def solicitar_dica(self, id_partida: str, id_jogador: str) -> str:
        pass

    @abstractmethod
    def partida(self, id_partida: str) -> Partida:
        pass
