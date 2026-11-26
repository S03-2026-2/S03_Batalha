from interfaces.provedor_dicas import ProvedorDicas
from models.carta import Carta
from models.movimento import Movimento
from models.partida import Partida
from services.calculadora_dano import CalculadoraDano


class DicaLocal(ProvedorDicas):
    """Dica calculada aqui mesmo, com a mesma CalculadoraDano da batalha.

    Usada quando o serviço Recomendacao-de-cartas não está disponível.
    Para cada opção (carta + golpe) estima a chance de vencer contra a melhor resposta do adversário.
    """

    def __init__(self, calculadora: CalculadoraDano) -> None:
        self._calculadora = calculadora

    def _melhor_forca(self, atacante: Carta, defensor: Carta) -> float:
        return max(
            (self._calculadora.calcular(m, atacante.pokemon, defensor.pokemon) for m in atacante.pokemon.movimentos),
            default=1.0,
        )

    def _chance(self, carta: Carta, movimento: Movimento, oponentes: list[Carta]) -> float:
        chances = []
        for oponente in oponentes:
            minha = self._calculadora.calcular(movimento, carta.pokemon, oponente.pokemon)
            dele = self._melhor_forca(oponente, carta)
            chances.append(minha / (minha + dele) if minha + dele > 0 else 0.5)
        return sum(chances) / len(chances) if chances else 0.5

    def gerar_dica(self, partida: Partida, id_jogador: str) -> str:
        jogador = partida.jogador(id_jogador)
        adversario = partida.adversario(id_jogador)
        if jogador is None:
            return "Jogador não pertence à partida."

        em_campo = partida.carta_em_campo(jogador.id)
        minhas = [em_campo] if em_campo else jogador.cartas
        oponente_campo = partida.carta_em_campo(adversario.id)
        oponentes = [oponente_campo] if oponente_campo else adversario.cartas

        opcoes = [(self._chance(c, m, oponentes), c, m) for c in minhas for m in c.pokemon.movimentos]
        if not opcoes:
            return "Não há jogadas disponíveis."
        chance, carta, movimento = max(opcoes, key=lambda o: o[0])

        alvo = f"contra {oponente_campo.pokemon.nome}" if oponente_campo else "contra a mão do adversário"
        return (
            f"Use {carta.pokemon.nome} com {movimento.nome}: "
            f"chance estimada de {chance:.0%} {alvo}."
        )
