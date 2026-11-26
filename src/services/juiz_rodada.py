from interfaces.gerador_aleatorio import GeradorAleatorio
from models.jogada import Jogada
from models.resultado_rodada import LadoRodada, ResultadoRodada
from services.calculadora_dano import CalculadoraDano


class JuizRodada:
    """RN04 – decide a rodada por sorteio ponderado: P(J1) = S1 / (S1 + S2)."""

    def __init__(self, calculadora: CalculadoraDano, gerador: GeradorAleatorio) -> None:
        self._calculadora = calculadora
        self._gerador = gerador

    def probabilidade(self, forca1: float, forca2: float) -> float:
        total = forca1 + forca2
        return 0.5 if total <= 0 else forca1 / total

    def resolver(self, numero: int, jogada1: Jogada, jogada2: Jogada) -> ResultadoRodada:
        p1, p2 = jogada1.carta.pokemon, jogada2.carta.pokemon
        forca1 = self._calculadora.calcular(jogada1.movimento, p1, p2)
        forca2 = self._calculadora.calcular(jogada2.movimento, p2, p1)
        prob1 = self.probabilidade(forca1, forca2)
        sorteio = self._gerador.proximo()

        vencedora, perdedora = (jogada1, jogada2) if sorteio < prob1 else (jogada2, jogada1)
        return ResultadoRodada(
            numero=numero,
            lado1=LadoRodada(jogada1.jogador.id, jogada1.carta.id, p1.nome, jogada1.movimento.nome, forca1),
            lado2=LadoRodada(jogada2.jogador.id, jogada2.carta.id, p2.nome, jogada2.movimento.nome, forca2),
            probabilidade_jogador1=prob1,
            sorteio=sorteio,
            id_vencedor=vencedora.jogador.id,
            id_perdedor=perdedora.jogador.id,
        )
