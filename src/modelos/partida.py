from __future__ import annotations
from jogador import Jogador


class Partida:
    def __init__(self, jogadores: list[Jogador] | None = None) -> None:
        self._jogadores: list[Jogador] = jogadores or []
        self._vitorias: dict[str, int] = {}
        self._turno: int = 0

    def registrar_vitoria(self, jogador: Jogador) -> None:
        pass

    def terminou(self) -> bool:
        pass

    def vencedor(self) -> Jogador:
        pass
