import logging
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel
from models.jogador import Jogador
from services.servico_batalha import ServicoBatalha

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Batalha Pokemon")
servico = ServicoBatalha()

class SolicitacaoBatalha(BaseModel):
    idJogador: str

class IniciarBatalha(BaseModel):
    idPartida: str
    idJogador1: str
    idJogador2: str
    callbackUrl: str

@app.post("/batalhas/solicitar", status_code=202)
def solicitar(req: SolicitacaoBatalha):
    try:
        servico.solicitar_batalha(req.idJogador)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gerenciador indisponivel: {e}")
    return {"mensagem": "Solicitacao enviada ao gerenciador."}


@app.post("/batalhas", status_code=202)
def iniciar(req: IniciarBatalha, tasks: BackgroundTasks):
    jogadores = [Jogador(req.idJogador1),
                 Jogador(req.idJogador2)]
    tasks.add_task(servico.iniciar_partida, jogadores, req.idPartida, req.callbackUrl)
    return {"aceito": True}


@app.get("/batalhas/{id_partida}")
def status(id_partida: str):
    partida = servico.partida(id_partida)
    if partida is None:
        raise HTTPException(status_code=404, detail="Partida desconhecida.")
    return {"idPartida": partida.id, "status": partida.status,
            "detalhes": partida.detalhes, "erro": partida.erro}
