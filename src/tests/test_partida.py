import pytest

from models.erros import JogadaInvalida
from models.jogador import Jogador
from models.partida import Partida, StatusPartida
from models.resultado_rodada import LadoRodada, ResultadoRodada
from tests.fakes import carta


def nova_partida(mao1=("squirtle", "pikachu", "bulbasaur", "eevee", "abra"),
                 mao2=("charmander", "geodude", "pidgey", "machop", "gastly")) -> Partida:
    p = Partida([Jogador("ana"), Jogador("bia")], "p1")
    p.iniciar({"ana": [carta(n, "ana") for n in mao1], "bia": [carta(n, "bia") for n in mao2]})
    return p


def vitoria(p: Partida, id_vencedor: str) -> None:
    j1, j2 = p.jogadas_da_rodada()
    vencedor, perdedor = (j1, j2) if j1.jogador.id == id_vencedor else (j2, j1)
    lado = lambda j: LadoRodada(j.jogador.id, j.carta.id, j.carta.pokemon.nome, j.movimento.nome, 1.0)
    p.registrar_vitoria(ResultadoRodada(p.turno, lado(j1), lado(j2), 0.5, 0.1,
                                        vencedor.jogador.id, perdedor.jogador.id))


def test_comeca_na_rodada_1_com_jogador1_escolhendo():
    p = nova_partida()
    assert p.status == StatusPartida.EM_ANDAMENTO
    assert p.turno == 1
    assert p.jogador_da_vez().id == "ana"


def test_revezamento_rodada_par_comeca_o_jogador2():
    p = nova_partida()
    p.registrar_jogada("ana", "ana:7", "water-gun")
    assert p.jogador_da_vez().id == "bia"
    p.registrar_jogada("bia", "bia:4", "ember")
    vitoria(p, "ana")
    assert p.turno == 2
    assert p.jogador_da_vez().id == "bia"


def test_nao_pode_jogar_fora_da_vez():
    p = nova_partida()
    with pytest.raises(JogadaInvalida, match="escolhe primeiro"):
        p.registrar_jogada("bia", "bia:4", "ember")


def test_carta_que_nao_esta_na_mao_e_rejeitada():
    p = nova_partida()
    with pytest.raises(JogadaInvalida, match="não está na sua mão"):
        p.registrar_jogada("ana", "bia:4", "ember")


def test_movimento_que_o_pokemon_nao_conhece_e_rejeitado():
    p = nova_partida()
    with pytest.raises(JogadaInvalida, match="não conhece"):
        p.registrar_jogada("ana", "ana:7", "flamethrower")


def test_vencedor_permanece_em_campo_e_perdedor_perde_a_carta():
    p = nova_partida()
    p.registrar_jogada("ana", "ana:7", "water-gun")
    p.registrar_jogada("bia", "bia:4", "ember")
    vitoria(p, "ana")

    assert p.carta_em_campo("ana").id == "ana:7"
    assert p.carta_em_campo("bia") is None
    assert p.jogador("bia").selecionar_carta("bia:4") is None
    assert len(p.jogador("bia").cartas) == 4
    assert p.pontuacao("ana") == 1


def test_vencedor_nao_pode_trocar_de_carta():
    p = nova_partida()
    p.registrar_jogada("ana", "ana:7", "water-gun")
    p.registrar_jogada("bia", "bia:4", "ember")
    vitoria(p, "ana")
    p.registrar_jogada("bia", "bia:74", "rock-throw")
    with pytest.raises(JogadaInvalida, match="permanece em campo"):
        p.registrar_jogada("ana", "ana:25", "thunderbolt")
    jogada = p.registrar_jogada("ana", None, "bubble-beam")  # só escolhe o golpe
    assert jogada.carta.id == "ana:7"


def test_cinco_rodadas_e_fim_de_partida():
    p = nova_partida()
    vencedores = ["ana", "bia", "ana", "bia", "ana"]
    for vencedor in vencedores:
        for jogador in p.ordem_da_rodada():
            em_campo = p.carta_em_campo(jogador.id)
            c = em_campo or jogador.cartas[0]
            p.registrar_jogada(jogador.id, c.id, c.pokemon.movimentos[0].nome)
        vitoria(p, vencedor)

    assert p.terminou()
    assert p.vencedor().id == "ana"
    assert p.perdedor().id == "bia"
    assert p.pontuacao("ana") + p.pontuacao("bia") == 5
    assert p.detalhes() == "Vitória de ana por 3 a 2 após 5 rodadas."
    with pytest.raises(JogadaInvalida):
        p.registrar_jogada("ana", None, "water-gun")


def test_partida_acaba_cedo_se_perdedor_fica_sem_cartas():
    p = nova_partida(mao1=("squirtle", "pikachu"), mao2=("charmander",))
    p.registrar_jogada("ana", "ana:7", "water-gun")
    p.registrar_jogada("bia", "bia:4", "ember")
    vitoria(p, "ana")
    assert p.terminou()
    assert p.vencedor().id == "ana"


def test_jogadores_iguais_nao_formam_partida():
    with pytest.raises(ValueError):
        Partida([Jogador("ana"), Jogador("ana")], "p2")
