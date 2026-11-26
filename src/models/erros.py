class ErroBatalha(Exception):
    """Erro de regra de negócio da batalha (vira 4xx na API)."""


class PartidaNaoEncontrada(ErroBatalha):
    pass


class JogadaInvalida(ErroBatalha):
    pass
