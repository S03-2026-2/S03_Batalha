import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from composicao import criar_servico
from models.erros import ErroBatalha, JogadaInvalida, PartidaNaoEncontrada
from services.servico_batalha import ServicoBatalha
from visao_partida import estado

logging.basicConfig(level=logging.INFO)


class SolicitacaoBatalha(BaseModel):
    idJogador: str


class IniciarBatalha(BaseModel):
    idPartida: str
    idJogador1: str
    idJogador2: str
    callbackUrl: str | None = None


class NovaJogada(BaseModel):
    idJogador: str
    idCarta: str | None = None   # opcional quando o Pokémon do jogador permaneceu em campo
    nomeMovimento: str


class PedidoDica(BaseModel):
    idJogador: str


def criar_app(servico: ServicoBatalha) -> FastAPI:
    app = FastAPI(title="S03_Batalha", description="Sistema de Batalha Pokémon")
    # As telas em src/components rodam em outra origem (arquivo local ou outro servidor).
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.exception_handler(ErroBatalha)
    def erro_de_regra(_: Request, erro: ErroBatalha):
        codigo = 404 if isinstance(erro, PartidaNaoEncontrada) else 409 if isinstance(erro, JogadaInvalida) else 400
        return JSONResponse(status_code=codigo, content={"erro": str(erro)})

    @app.post("/batalhas/solicitar", status_code=202)
    def solicitar(req: SolicitacaoBatalha):
        try:
            servico.solicitar_batalha(req.idJogador)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Gerenciador indisponível: {e}")
        return {"mensagem": "Solicitação de batalha enviada para a Gestão de Partidas."}

    @app.post("/batalhas", status_code=201)
    def iniciar(req: IniciarBatalha):
        if req.idJogador1 == req.idJogador2:
            raise HTTPException(status_code=400, detail="Os dois jogadores precisam ser diferentes.")
        partida = servico.iniciar_partida(req.idPartida, req.idJogador1, req.idJogador2, req.callbackUrl)
        return estado(partida)

    @app.get("/batalhas/{id_partida}")
    def consultar(id_partida: str, jogador: str | None = None):
        return estado(servico.partida(id_partida), jogador)

    @app.get("/batalhas/{id_partida}/cartas/{id_carta}")
    def analisar(id_partida: str, id_carta: str):
        return servico.analisar_carta(id_partida, id_carta).para_dict()

    @app.post("/batalhas/{id_partida}/jogadas")
    def jogar(id_partida: str, req: NovaJogada):
        resultado = servico.jogar(id_partida, req.idJogador, req.idCarta, req.nomeMovimento)
        partida = servico.partida(id_partida)
        return {
            "mensagem": "Rodada processada." if resultado else "Jogada registrada. Aguardando o adversário.",
            "resultadoRodada": resultado.para_dict() if resultado else None,
            "estado": estado(partida, req.idJogador),
        }

    @app.post("/batalhas/{id_partida}/dica")
    def dica(id_partida: str, req: PedidoDica):
        return {"dica": servico.solicitar_dica(id_partida, req.idJogador)}

    return app


app = criar_app(criar_servico())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "3001")))
