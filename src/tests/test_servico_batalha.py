import pytest

from models.erros import JogadaInvalida, PartidaNaoEncontrada
from models.partida import StatusPartida
from controllers.cliente_gestao import ClienteGestao
from tests.fakes import GeradorFixo, MaosFixas, criar_servico

MAOS = MaosFixas({
    "ana": ["squirtle", "pikachu", "bulbasaur", "eevee", "abra"],
    "bia": ["charmander", "geodude", "pidgey", "machop", "gastly"],
})


def jogar_rodada(servico, id_partida):
    partida = servico.partida(id_partida)
    resultado = None
    for jogador in partida.ordem_da_rodada():
        carta = partida.carta_em_campo(jogador.id) or jogador.cartas[0]
        resultado = servico.jogar(id_partida, jogador.id, carta.id, carta.pokemon.movimentos[0].nome)
    return resultado


def test_iniciar_partida_carrega_as_maos():
    servico, _ = criar_servico(GeradorFixo(), MAOS)
    partida = servico.iniciar_partida("p1", "ana", "bia")
    assert partida.status == StatusPartida.EM_ANDAMENTO
    assert len(partida.jogador("ana").cartas) == 5


def test_iniciar_duas_vezes_nao_duplica():
    servico, _ = criar_servico(GeradorFixo(), MAOS)
    assert servico.iniciar_partida("p1", "ana", "bia") is servico.iniciar_partida("p1", "ana", "bia")


def test_primeira_jogada_espera_o_adversario():
    servico, _ = criar_servico(GeradorFixo(), MAOS)
    servico.iniciar_partida("p1", "ana", "bia")
    assert servico.jogar("p1", "ana", "ana:7", "water-gun") is None


def test_sorteio_ponderado_decide_a_rodada():
    # P(ana) = 80 / (80 + 23) ≈ 0.7767
    servico, _ = criar_servico(GeradorFixo(0.70, 0.80), MAOS)
    servico.iniciar_partida("p1", "ana", "bia")
    servico.jogar("p1", "ana", "ana:7", "water-gun")
    r1 = servico.jogar("p1", "bia", "bia:4", "ember")
    assert r1.probabilidade_jogador1 == pytest.approx(0.7767, abs=1e-4)
    assert r1.id_vencedor == "ana"            # 0.70 < 0.7767

    # Rodada 2: bia escolhe primeiro; squirtle continua em campo.
    servico.jogar("p1", "bia", "bia:74", "rock-throw")
    r2 = servico.jogar("p1", "ana", None, "water-gun")
    assert r2.lado1.pokemon == "squirtle"
    assert r2.lado1.forca == pytest.approx(184)  # 40 x 4 (água vs pedra/terra) x 1.15 (43 > 20)
    assert r2.id_vencedor == "bia"            # 0.80 >= P(ana)


def test_partida_completa_notifica_a_gestao():
    servico, gestao = criar_servico(GeradorFixo(0.0, 0.99, 0.0, 0.99, 0.0), MAOS)
    servico.iniciar_partida("p1", "ana", "bia", "http://gestao/partidas/resultado")
    for _ in range(5):
        jogar_rodada(servico, "p1")

    partida = servico.partida("p1")
    assert partida.terminou()
    assert gestao.notificadas == [partida]
    assert partida.notificacao == "ENVIADA"
    corpo = ClienteGestao.montar_corpo(partida)
    assert corpo == {
        "idPartida": "p1", "idVencedor": "ana", "idPerdedor": "bia",
        "pontuacaoJogador1": 3, "pontuacaoJogador2": 2,
        "detalhes": "Vitória de ana por 3 a 2 após 5 rodadas.",
    }


def test_pontuacao_vai_por_posicao_mesmo_quando_jogador2_vence():
    servico, _ = criar_servico(GeradorFixo(0.99, 0.99, 0.99, 0.0, 0.0), MAOS)
    servico.iniciar_partida("p1", "ana", "bia")
    for _ in range(5):
        jogar_rodada(servico, "p1")
    corpo = ClienteGestao.montar_corpo(servico.partida("p1"))
    assert corpo["idVencedor"] == "bia"
    assert (corpo["pontuacaoJogador1"], corpo["pontuacaoJogador2"]) == (2, 3)


def test_falha_ao_carregar_cartas_marca_erro():
    class FonteQuebrada:
        def cartas_do_jogador(self, id_jogador, id_partida):
            raise ConnectionError("distribuição fora do ar")

    servico, _ = criar_servico(GeradorFixo(), FonteQuebrada())
    partida = servico.iniciar_partida("p1", "ana", "bia")
    assert partida.status == StatusPartida.ERRO
    assert "distribuição fora do ar" in partida.erro


def test_partida_inexistente():
    servico, _ = criar_servico(GeradorFixo())
    with pytest.raises(PartidaNaoEncontrada):
        servico.partida("nao-existe")


def test_dica_local_sugere_vantagem_de_tipo():
    servico, _ = criar_servico(GeradorFixo(0.0), MaosFixas({"ana": ["squirtle", "charmander"], "bia": ["charmander", "eevee"]}))
    servico.iniciar_partida("p1", "ana", "bia")
    servico.jogar("p1", "ana", "ana:4", "ember")
    servico.jogar("p1", "bia", "bia:4", "ember")    # ana vence (sorteio 0.0); charmander de bia sai
    # rodada 2: bia escolhe primeiro; pede dica com a mão restante (eevee)
    dica = servico.solicitar_dica("p1", "bia")
    assert dica.startswith("Use eevee")


def test_solicitar_batalha_vai_para_a_fila_da_gestao():
    servico, gestao = criar_servico(GeradorFixo())
    servico.solicitar_batalha("ana")
    assert gestao.fila == ["ana"]


def test_analisar_carta():
    servico, _ = criar_servico(GeradorFixo(), MAOS)
    servico.iniciar_partida("p1", "ana", "bia")
    assert servico.analisar_carta("p1", "bia:92").pokemon.nome == "gastly"
    with pytest.raises(JogadaInvalida):
        servico.analisar_carta("p1", "zzz")
