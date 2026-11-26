from models.jogador import Jogador


class Partida:
    def __init__(
            self,
            jogadores: list[Jogador] | None = None,
            id_partida: str = None,
            callback_url : str = None,
    ) -> None:
        self._jogadores: list[Jogador] = jogadores or []
        self._vitorias: dict[str, int] = {}
        self._turno: int = 0
        self._id_partida: str = id_partida
        self.callback_url: str = callback_url

    @property
    def id_partida(self) -> str:
        return self._id_partida

    @property
    def jogadores(self) -> Jogador:
        return self._jogadores[0], self._jogadores[1]

    def registrar_vitoria(self, jogador: Jogador) -> None:
        pass

    def pontuacao(self) -> int:
        pass

    def terminou(self) -> bool:
        pass

    def resultado(self):
        pass

    def detalhes(self) -> str:
        pass
