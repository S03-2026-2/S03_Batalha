from dataclasses import dataclass


@dataclass(frozen=True)
class LadoRodada:
    id_jogador: str
    id_carta: str
    pokemon: str
    movimento: str
    forca: float


@dataclass(frozen=True)
class ResultadoRodada:
    numero: int
    lado1: LadoRodada
    lado2: LadoRodada
    probabilidade_jogador1: float
    sorteio: float
    id_vencedor: str
    id_perdedor: str

    def para_dict(self) -> dict:
        def lado(l: LadoRodada) -> dict:
            return {
                "idJogador": l.id_jogador,
                "idCarta": l.id_carta,
                "pokemon": l.pokemon,
                "movimento": l.movimento,
                "forca": round(l.forca, 2),
            }

        return {
            "rodada": self.numero,
            "jogadas": [lado(self.lado1), lado(self.lado2)],
            "probabilidadeJogador1": round(self.probabilidade_jogador1, 4),
            "sorteio": round(self.sorteio, 4),
            "idVencedor": self.id_vencedor,
            "idPerdedor": self.id_perdedor,
        }
