from models.carta import Carta
from models.erros import JogadaInvalida
from models.jogada import Jogada
from models.jogador import Jogador
from models.resultado_rodada import ResultadoRodada

TOTAL_RODADAS = 5


class StatusPartida:
    PREPARANDO = "PREPARANDO"      # buscando as cartas dos jogadores
    EM_ANDAMENTO = "EM_ANDAMENTO"
    FINALIZADA = "FINALIZADA"
    ERRO = "ERRO"


class Partida:
    """Guarda o estado das 5 rodadas: turno, placar, quem está em campo e quem escolhe primeiro.

    Não calcula força nem sorteia nada: isso é do ServicoBatalha/JuizRodada (SRP).
    """

    def __init__(self, jogadores: list[Jogador], id_partida: str, callback_url: str | None = None) -> None:
        if len(jogadores) != 2:
            raise ValueError("Uma partida precisa de exatamente 2 jogadores.")
        if jogadores[0].id == jogadores[1].id:
            raise ValueError("Os dois jogadores precisam ser diferentes.")

        self._id = str(id_partida)
        self._jogadores = list(jogadores)
        self.callback_url = callback_url
        self._turno = 1
        self._vitorias: dict[str, int] = {j.id: 0 for j in jogadores}
        self._em_campo: dict[str, Carta | None] = {j.id: None for j in jogadores}
        self._pendentes: dict[str, Jogada] = {}
        self._historico: list[ResultadoRodada] = []
        self._status = StatusPartida.PREPARANDO
        self._erro: str | None = None
        self._versao = 0
        self.notificacao: str | None = None  # resultado do envio à Gestão de Partidas

    # ---- leitura ----------------------------------------------------------
    @property
    def id(self) -> str:
        return self._id

    @property
    def jogadores(self) -> tuple[Jogador, Jogador]:
        return self._jogadores[0], self._jogadores[1]

    @property
    def turno(self) -> int:
        return self._turno

    @property
    def status(self) -> str:
        return self._status

    @property
    def erro(self) -> str | None:
        return self._erro

    @property
    def versao(self) -> int:
        """Muda sempre que o estado muda (o frontend só redesenha quando ela muda)."""
        return self._versao

    @property
    def historico(self) -> list[ResultadoRodada]:
        return list(self._historico)

    def jogador(self, id_jogador: str) -> Jogador | None:
        return next((j for j in self._jogadores if j.id == str(id_jogador)), None)

    def adversario(self, id_jogador: str) -> Jogador:
        return self._jogadores[1] if self._jogadores[0].id == str(id_jogador) else self._jogadores[0]

    def carta_em_campo(self, id_jogador: str) -> Carta | None:
        return self._em_campo.get(str(id_jogador))

    def jogada_pendente(self, id_jogador: str) -> Jogada | None:
        return self._pendentes.get(str(id_jogador))

    def ja_jogou(self, id_jogador: str) -> bool:
        return str(id_jogador) in self._pendentes

    def ordem_da_rodada(self) -> tuple[Jogador, Jogador]:
        """Revezamento (RN01): rodadas ímpares começa o jogador 1, pares o jogador 2."""
        j1, j2 = self.jogadores
        return (j1, j2) if self._turno % 2 == 1 else (j2, j1)

    def jogador_da_vez(self) -> Jogador | None:
        if self._status != StatusPartida.EM_ANDAMENTO:
            return None
        return next((j for j in self.ordem_da_rodada() if j.id not in self._pendentes), None)

    def pontuacao(self, id_jogador: str) -> int:
        return self._vitorias.get(str(id_jogador), 0)

    def terminou(self) -> bool:
        return self._status == StatusPartida.FINALIZADA

    def vencedor(self) -> Jogador | None:
        if not self.terminou():
            return None
        j1, j2 = self.jogadores
        if self.pontuacao(j1.id) != self.pontuacao(j2.id):
            return j1 if self.pontuacao(j1.id) > self.pontuacao(j2.id) else j2
        # Empate só acontece se a partida acabou cedo por falta de cartas:
        # vence quem ainda tem carta.
        return j1 if j1.tem_cartas() else j2

    def perdedor(self) -> Jogador | None:
        vencedor = self.vencedor()
        return None if vencedor is None else self.adversario(vencedor.id)

    def resultado(self) -> tuple[Jogador, Jogador]:
        return self.vencedor(), self.perdedor()

    def detalhes(self) -> str:
        vencedor, perdedor = self.resultado()
        if vencedor is None:
            return f"Rodada {self._turno} de {TOTAL_RODADAS} em andamento."
        rodadas = len(self._historico)
        return (
            f"Vitória de {vencedor.id} por {self.pontuacao(vencedor.id)} a "
            f"{self.pontuacao(perdedor.id)} após {rodadas} rodadas."
        )

    # ---- mudanças de estado -------------------------------------------------
    def iniciar(self, maos: dict[str, list[Carta]]) -> None:
        for jogador in self._jogadores:
            jogador.cartas = maos.get(jogador.id, [])
            if not jogador.tem_cartas():
                raise ValueError(f"O jogador {jogador.id} não tem cartas para batalhar.")
        self._status = StatusPartida.EM_ANDAMENTO
        self._versao += 1

    def falhar(self, mensagem: str) -> None:
        self._status = StatusPartida.ERRO
        self._erro = mensagem
        self._versao += 1

    def registrar_jogada(self, id_jogador: str, id_carta: str | None, nome_movimento: str) -> Jogada:
        if self._status != StatusPartida.EM_ANDAMENTO:
            raise JogadaInvalida("A partida não está em andamento.")
        jogador = self.jogador(id_jogador)
        if jogador is None:
            raise JogadaInvalida("Este jogador não pertence à partida.")
        if self.ja_jogou(jogador.id):
            raise JogadaInvalida("Você já jogou nesta rodada. Aguarde o adversário.")
        da_vez = self.jogador_da_vez()
        if da_vez is not None and da_vez.id != jogador.id:
            raise JogadaInvalida(f"Nesta rodada quem escolhe primeiro é {da_vez.id}.")

        em_campo = self._em_campo[jogador.id]
        if em_campo is not None:
            # RN02: o vencedor da rodada anterior continua com o mesmo Pokémon.
            if id_carta and str(id_carta) != em_campo.id:
                raise JogadaInvalida("Seu Pokémon venceu a rodada anterior e permanece em campo; escolha só o movimento.")
            carta = em_campo
        else:
            if not id_carta:
                raise JogadaInvalida("Escolha uma carta da sua mão.")
            carta = jogador.selecionar_carta(id_carta)
            if carta is None:
                raise JogadaInvalida("Essa carta não está na sua mão.")

        movimento = carta.obter_movimento(nome_movimento)
        if movimento is None:
            raise JogadaInvalida(f"{carta.pokemon.nome} não conhece o movimento {nome_movimento}.")

        jogada = Jogada(jogador, carta, movimento)
        self._pendentes[jogador.id] = jogada
        self._versao += 1
        return jogada

    def rodada_completa(self) -> bool:
        return len(self._pendentes) == 2

    def jogadas_da_rodada(self) -> tuple[Jogada, Jogada]:
        """Jogadas na ordem (jogador1, jogador2), independente de quem escolheu primeiro."""
        j1, j2 = self.jogadores
        return self._pendentes[j1.id], self._pendentes[j2.id]

    def registrar_vitoria(self, resultado: ResultadoRodada) -> None:
        vencedor = self.jogador(resultado.id_vencedor)
        perdedor = self.jogador(resultado.id_perdedor)
        carta_vencedora = self._pendentes[vencedor.id].carta
        carta_perdedora = self._pendentes[perdedor.id].carta

        self._vitorias[vencedor.id] += 1
        self._em_campo[vencedor.id] = carta_vencedora   # vencedor permanece em campo
        self._em_campo[perdedor.id] = None
        perdedor.remover_carta(carta_perdedora.id)      # carta derrotada é eliminada
        self._historico.append(resultado)
        self._pendentes.clear()
        self._turno += 1

        if self._turno > TOTAL_RODADAS or not perdedor.tem_cartas():
            self._turno = min(self._turno, TOTAL_RODADAS)
            self._status = StatusPartida.FINALIZADA
        self._versao += 1
