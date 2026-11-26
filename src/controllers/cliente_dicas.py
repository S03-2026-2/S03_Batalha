import logging
import uuid

import requests

from interfaces.provedor_dicas import ProvedorDicas
from models.carta import Carta
from models.partida import Partida

log = logging.getLogger(__name__)


class ClienteDicas(ProvedorDicas):
    """Adapter do serviço Recomendacao-de-cartas (POST /api/dica, exige token Bearer).

    Se o serviço não responder, recusar o token ou estourar o limite de dicas,
    devolve a dica da estratégia reserva (DicaLocal).
    """

    def __init__(self, base_url: str, token: str | None, reserva: ProvedorDicas, timeout: float = 5) -> None:
        self._base = base_url.rstrip("/")
        self._token = token
        self._reserva = reserva
        self._timeout = timeout

    @staticmethod
    def _carta(carta: Carta) -> dict:
        try:
            id_carta = str(uuid.UUID(carta.id))
        except ValueError:  # o serviço exige Guid; ids locais viram um uuid estável
            id_carta = str(uuid.uuid5(uuid.NAMESPACE_URL, carta.id))
        return {
            "id": id_carta,
            "nome": carta.pokemon.nome,
            "tipos": carta.pokemon.tipos,
            "movimentos": [m.nome for m in carta.pokemon.movimentos],
        }

    def _lado(self, partida: Partida, id_jogador: str) -> dict:
        jogador = partida.jogador(id_jogador)
        em_campo = partida.carta_em_campo(id_jogador)
        return {
            "campo": [self._carta(em_campo)] if em_campo else [],
            "mao": [self._carta(c) for c in jogador.cartas if c is not em_campo],
            "hp": len(jogador.cartas),
        }

    def gerar_dica(self, partida: Partida, id_jogador: str) -> str:
        if self._token:
            try:
                corpo = {
                    "jogador": self._lado(partida, id_jogador),
                    "oponente": self._lado(partida, partida.adversario(id_jogador).id),
                }
                resp = requests.post(
                    f"{self._base}/api/dica",
                    json=corpo,
                    headers={"Authorization": f"Bearer {self._token}"},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                texto = resp.json().get("texto")
                if texto:
                    return texto
            except (requests.RequestException, ValueError) as erro:
                log.warning("Recomendacao-de-cartas indisponível (%s); usando dica local.", erro)
        return self._reserva.gerar_dica(partida, id_jogador)
