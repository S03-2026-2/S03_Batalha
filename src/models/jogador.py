from models.carta import Carta


class Jogador:

    def __init__(self, id: str) -> None:
        self._id = str(id)
        self._cartas: list[Carta] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def cartas(self) -> list[Carta]:
        """Mão atual (cartas ainda vivas, inclusive a que estiver em campo)."""
        return list(self._cartas)

    @cartas.setter
    def cartas(self, cartas: list[Carta]) -> None:
        self._cartas = list(cartas)

    def selecionar_carta(self, id_carta: str) -> Carta | None:
        return next((c for c in self._cartas if c.id == str(id_carta)), None)

    def remover_carta(self, id_carta: str) -> None:
        self._cartas = [c for c in self._cartas if c.id != str(id_carta)]

    def tem_cartas(self) -> bool:
        return bool(self._cartas)
