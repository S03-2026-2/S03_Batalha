"""Monta o JSON da partida do ponto de vista de um jogador (usado pela arena)."""
from models.carta import Carta
from models.partida import Partida


def _carta(carta: Carta | None) -> dict | None:
    return None if carta is None else carta.para_dict()


def _lado(partida: Partida, id_jogador: str, revelar_jogada: bool) -> dict:
    jogador = partida.jogador(id_jogador)
    em_campo = partida.carta_em_campo(id_jogador)
    pendente = partida.jogada_pendente(id_jogador) if revelar_jogada else None
    return {
        "idJogador": jogador.id,
        "pontos": partida.pontuacao(jogador.id),
        "cartaEmCampo": _carta(em_campo),
        # A mão mostrada é a de cartas que podem entrar; a que está em campo aparece no campo.
        "mao": [_carta(c) for c in jogador.cartas if c is not em_campo],
        "jaJogou": partida.ja_jogou(jogador.id),
        # Só o próprio jogador vê o que escolheu; o adversário só sabe que ele já jogou.
        "jogadaPendente": None if pendente is None else {
            "idCarta": pendente.carta.id, "nomeMovimento": pendente.movimento.nome,
        },
    }


def estado(partida: Partida, id_jogador: str | None = None) -> dict:
    j1, j2 = partida.jogadores
    da_vez = partida.jogador_da_vez()
    vencedor, perdedor = partida.resultado()
    corpo = {
        "idPartida": partida.id,
        "versao": partida.versao,
        "status": partida.status,
        "erro": partida.erro,
        "turno": partida.turno,
        "terminou": partida.terminou(),
        "idJogador1": j1.id,
        "idJogador2": j2.id,
        "jogadorDaVez": da_vez.id if da_vez else None,
        "primeiroDaRodada": partida.ordem_da_rodada()[0].id,
        "placar": {j1.id: partida.pontuacao(j1.id), j2.id: partida.pontuacao(j2.id)},
        "cartaEmCampo": {j.id: _carta(partida.carta_em_campo(j.id)) for j in (j1, j2)},
        "rodadas": [r.para_dict() for r in partida.historico],
        "idVencedor": vencedor.id if vencedor else None,
        "idPerdedor": perdedor.id if perdedor else None,
        "detalhes": partida.detalhes(),
        "notificacao": partida.notificacao,
    }
    if id_jogador and partida.jogador(id_jogador) and partida.status != "PREPARANDO":
        corpo["voce"] = _lado(partida, id_jogador, revelar_jogada=True)
        corpo["adversario"] = _lado(partida, partida.adversario(id_jogador).id, revelar_jogada=False)
        corpo["suaVez"] = da_vez is not None and da_vez.id == id_jogador
    return corpo
