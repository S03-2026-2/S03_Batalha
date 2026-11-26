from fastapi.testclient import TestClient

from app import criar_app
from tests.fakes import GeradorFixo, MaosFixas, criar_servico


def cliente():
    servico, gestao = criar_servico(
        GeradorFixo(0.0, 0.0, 0.0),
        MaosFixas({"ana": ["squirtle", "pikachu", "eevee"], "bia": ["charmander", "geodude", "pidgey"]}),
    )
    return TestClient(criar_app(servico)), gestao


def test_fluxo_completo_pela_api():
    api, gestao = cliente()
    r = api.post("/batalhas", json={"idPartida": "p1", "idJogador1": "ana", "idJogador2": "bia",
                                    "callbackUrl": "http://localhost:3000/partidas/resultado"})
    assert r.status_code == 201
    assert r.json()["turno"] == 1

    estado = api.get("/batalhas/p1", params={"jogador": "ana"}).json()
    assert estado["status"] == "EM_ANDAMENTO"
    assert estado["suaVez"] is True
    assert len(estado["voce"]["mao"]) == 3

    r = api.post("/batalhas/p1/jogadas", json={"idJogador": "ana", "idCarta": "ana:7", "nomeMovimento": "water-gun"})
    assert r.status_code == 200
    assert r.json()["resultadoRodada"] is None

    r = api.post("/batalhas/p1/jogadas", json={"idJogador": "bia", "idCarta": "bia:4", "nomeMovimento": "ember"})
    assert r.json()["resultadoRodada"]["idVencedor"] == "ana"
    assert r.json()["estado"]["cartaEmCampo"]["ana"]["id"] == "ana:7"

    # bia perde as 3 cartas -> partida acaba na 3ª rodada
    api.post("/batalhas/p1/jogadas", json={"idJogador": "bia", "idCarta": "bia:74", "nomeMovimento": "tackle"})
    api.post("/batalhas/p1/jogadas", json={"idJogador": "ana", "nomeMovimento": "water-gun"})
    api.post("/batalhas/p1/jogadas", json={"idJogador": "ana", "nomeMovimento": "water-gun"})
    api.post("/batalhas/p1/jogadas", json={"idJogador": "bia", "idCarta": "bia:16", "nomeMovimento": "gust"})

    final = api.get("/batalhas/p1").json()
    assert final["terminou"] is True
    assert final["idVencedor"] == "ana"
    assert len(gestao.notificadas) == 1


def test_erros_de_regra_viram_4xx():
    api, _ = cliente()
    assert api.get("/batalhas/nada").status_code == 404
    api.post("/batalhas", json={"idPartida": "p1", "idJogador1": "ana", "idJogador2": "bia"})
    r = api.post("/batalhas/p1/jogadas", json={"idJogador": "bia", "idCarta": "bia:4", "nomeMovimento": "ember"})
    assert r.status_code == 409
    assert "escolhe primeiro" in r.json()["erro"]
    assert api.post("/batalhas", json={"idPartida": "p2", "idJogador1": "ana", "idJogador2": "ana"}).status_code == 400


def test_dica_e_analise():
    api, _ = cliente()
    api.post("/batalhas", json={"idPartida": "p1", "idJogador1": "ana", "idJogador2": "bia"})
    assert api.post("/batalhas/p1/dica", json={"idJogador": "ana"}).json()["dica"].startswith("Use ")
    assert api.get("/batalhas/p1/cartas/ana:25").json()["pokemon"]["nome"] == "pikachu"
