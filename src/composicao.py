"""Composition Root: o único lugar que conhece as classes concretas e monta o ServicoBatalha.

Variáveis de ambiente:
  GESTAO_API_URL         gerenciador-de-partidas            (padrão http://localhost:3000)
  DISTRIBUICAO_API_URL   Distribuicao_de_Cartas             (vazio = sorteia a mão localmente)
  RECOMENDACAO_API_URL   Recomendacao-de-cartas             (padrão http://localhost:5242)
  RECOMENDACAO_TOKEN     token Bearer do serviço de dicas   (vazio = usa só a dica local)
  BATALHA_OFFLINE=1      não acessa a PokéAPI (usa o catálogo fixo do ProvedorFake)
"""
import os

from controllers.cliente_dicas import ClienteDicas
from controllers.cliente_distribuicao import ClienteDistribuicao
from controllers.cliente_gestao import ClienteGestao
from controllers.fonte_cartas_local import FonteCartasComReserva, FonteCartasLocal
from controllers.gerador_aleatorio_padrao import GeradorAleatorioPadrao
from controllers.poke_api_provider import PokeApiProvider
from controllers.provedor_cache import ProvedorPokemonComCache
from controllers.provedor_fake import ProvedorFake
from controllers.repositorio_memoria import RepositorioPartidasMemoria
from interfaces.fonte_cartas import FonteCartas
from interfaces.provedor_pokemon import ProvedorPokemon
from services.bonus_velocidade import BonusVelocidade
from services.calculadora_dano import CalculadoraDano
from services.dica_local import DicaLocal
from services.juiz_rodada import JuizRodada
from services.servico_batalha import ServicoBatalha
from services.vantagem_elemento import VantagemElemento


def criar_calculadora() -> CalculadoraDano:
    # Ordem da RN03: dano base -> vantagem de elemento -> bônus de velocidade.
    return CalculadoraDano([VantagemElemento(), BonusVelocidade()])


def criar_provedor_pokemon(offline: bool) -> ProvedorPokemon:
    return ProvedorFake() if offline else ProvedorPokemonComCache(PokeApiProvider())


def criar_fonte_cartas(provedor: ProvedorPokemon, offline: bool) -> FonteCartas:
    ids = ProvedorFake().ids if offline else None
    local = FonteCartasLocal(provedor, ids)
    url_distribuicao = os.getenv("DISTRIBUICAO_API_URL")
    if not url_distribuicao:
        return local
    return FonteCartasComReserva(ClienteDistribuicao(url_distribuicao, provedor), local)


def criar_servico() -> ServicoBatalha:
    offline = os.getenv("BATALHA_OFFLINE") == "1"
    provedor = criar_provedor_pokemon(offline)
    calculadora = criar_calculadora()
    gestao = ClienteGestao()
    dicas = ClienteDicas(
        os.getenv("RECOMENDACAO_API_URL", "http://localhost:5242"),
        os.getenv("RECOMENDACAO_TOKEN"),
        reserva=DicaLocal(calculadora),
    )
    return ServicoBatalha(
        fonte_cartas=criar_fonte_cartas(provedor, offline),
        dicas=dicas,
        pareamento=gestao,
        notificador=gestao,
        juiz=JuizRodada(calculadora, GeradorAleatorioPadrao()),
        repositorio=RepositorioPartidasMemoria(),
    )
