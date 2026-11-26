import logging
import random

from interfaces.fonte_cartas import FonteCartas
from interfaces.provedor_pokemon import ProvedorPokemon
from models.carta import Carta

log = logging.getLogger(__name__)


class FonteCartasLocal(FonteCartas):
    """Sorteia uma mão de Pokémon sem depender do serviço de Distribuição.

    A semente é (partida, jogador): recarregar a página ou reiniciar não muda a mão.
    """

    def __init__(self, provedor: ProvedorPokemon, ids_possiveis: list[int] | None = None,
                 tamanho_mao: int = 5) -> None:
        self._provedor = provedor
        self._ids = list(ids_possiveis or range(1, 152))
        self._tamanho_mao = tamanho_mao

    def cartas_do_jogador(self, id_jogador: str, id_partida: str) -> list[Carta]:
        sorteio = random.Random(f"{id_partida}|{id_jogador}")
        candidatos = sorteio.sample(self._ids, len(self._ids))
        cartas: list[Carta] = []
        for id_pokemon in candidatos:
            pokemon = self._provedor.buscar(id_pokemon)
            if pokemon is not None:
                cartas.append(Carta(f"{id_jogador}:{pokemon.id}", pokemon))
            if len(cartas) == self._tamanho_mao:
                break
        return cartas


class FonteCartasComReserva(FonteCartas):
    """Decorator: tenta a fonte principal e, se ela falhar ou vier vazia, usa a reserva."""

    def __init__(self, principal: FonteCartas, reserva: FonteCartas) -> None:
        self._principal = principal
        self._reserva = reserva

    def cartas_do_jogador(self, id_jogador: str, id_partida: str) -> list[Carta]:
        try:
            cartas = self._principal.cartas_do_jogador(id_jogador, id_partida)
            if cartas:
                return cartas
            log.warning("Fonte principal sem cartas para %s; usando a reserva.", id_jogador)
        except Exception as erro:
            log.warning("Fonte principal falhou para %s (%s); usando a reserva.", id_jogador, erro)
        return self._reserva.cartas_do_jogador(id_jogador, id_partida)
