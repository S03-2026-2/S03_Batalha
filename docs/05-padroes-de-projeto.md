# 05 – Padrões de Projeto no Código (`S03_Batalha`)

Este documento mostra onde cada padrão e cada princípio SOLID aparece no código, com o arquivo e o trecho que vale mostrar na apresentação.

---

## 1. Visão geral das camadas

```mermaid
flowchart TB
    subgraph Apresentacao["Apresentação"]
        APP["app.py (FastAPI)"]
        VISAO["visao_partida.py"]
        TELAS["components/*.html"]
    end
    subgraph Aplicacao["Aplicação"]
        SB["ServicoBatalha (Facade)"]
        JR["JuizRodada"]
        CD["CalculadoraDano"]
        MOD["VantagemElemento / BonusVelocidade (Strategy)"]
        DL["DicaLocal (Strategy)"]
    end
    subgraph Dominio["Domínio (models/)"]
        P["Partida"] --- J["Jogador"] --- C["Carta"] --- PK["Pokemon"] --- M["Movimento"]
    end
    subgraph Portas["Interfaces (interfaces/)"]
        I["ProvedorPokemon, FonteCartas, ProvedorDicas,<br/>SolicitadorPareamento, NotificadorPartidas,<br/>RepositorioPartidas, GeradorAleatorio, ModificadorDano"]
    end
    subgraph Infra["Adaptadores (controllers/)"]
        A["PokeApiProvider, ClienteDistribuicao,<br/>ClienteGestao, ClienteDicas (Adapter)"]
        D["ProvedorPokemonComCache, FonteCartasComReserva (Decorator)"]
        R["RepositorioPartidasMemoria (Repository)"]
    end
    COMP["composicao.py (Composition Root)"]

    TELAS -- HTTP --> APP --> SB
    SB --> JR --> CD --> MOD
    SB --> P
    SB --> I
    A -. implementa .-> I
    D -. implementa .-> I
    R -. implementa .-> I
    COMP -- monta --> SB
```

A regra das dependências: `models/` não importa nada de fora; `services/` só conhece `models/` e `interfaces/`; só o `composicao.py` conhece as classes concretas de `controllers/`.

---

## 2. Padrões de projeto

### 2.1 Strategy: regras de dano intercambiáveis
**Onde:** `interfaces/modificador_dano.py`, `services/vantagem_elemento.py`, `services/bonus_velocidade.py`, `services/calculadora_dano.py`

`CalculadoraDano` recebe uma lista de `ModificadorDano` e aplica um depois do outro. Ela não sabe quais regras existem.

```python
class CalculadoraDano:
    def __init__(self, modificadores: list[ModificadorDano], dano_padrao: float = 50):
        self._modificadores = list(modificadores)

    def calcular(self, movimento, atacante, defensor) -> float:
        dano = float(movimento.dano or self._dano_padrao)
        for modificador in self._modificadores:
            dano = modificador.aplicar(dano, movimento, atacante, defensor)
        return dano
```

O mesmo padrão aparece em `ProvedorDicas` (dica do serviço externo ou `DicaLocal`) e em `GeradorAleatorio` (aleatório de verdade ou valores fixos no teste).

**Prova no teste:** `tests/test_calculadora_dano.py::test_nova_regra_entra_sem_alterar_a_calculadora` cria uma regra de clima no próprio teste e ela funciona sem mudar nenhuma linha da calculadora.

### 2.2 Facade: um ponto de entrada para os casos de uso
**Onde:** `services/servico_batalha.py`

A API (`app.py`) só chama `ServicoBatalha`. Por trás dele estão `Partida`, `JuizRodada`, `FonteCartas`, `ProvedorDicas`, `NotificadorPartidas` e `RepositorioPartidas`. Cada método da fachada é um caso de uso: `solicitar_batalha` (UC01), `iniciar_partida` (UC02/UC03), `jogar` (UC04/UC07), `analisar_carta` (UC05), `solicitar_dica` (UC06) e `verificar_vencedor` (UC08).

### 2.3 Adapter: conversa com os outros grupos e com a PokéAPI
**Onde:** `controllers/poke_api_provider.py`, `controllers/cliente_distribuicao.py`, `controllers/cliente_gestao.py`, `controllers/cliente_dicas.py`

Cada cliente traduz o formato externo para o nosso modelo e vice-versa:

| Adapter | Serviço externo | Tradução |
| :--- | :--- | :--- |
| `PokeApiProvider` | PokéAPI | JSON de `/pokemon/{id}` e `/move/{id}` vira `Pokemon` e `Movimento` |
| `ClienteDistribuicao` | `Distribuicao_de_Cartas` (Python/Flask) | `[{carta_id, pokemon_id, ...}]` vira `list[Carta]` |
| `ClienteGestao` | `gerenciador-de-partidas` (Node/Express) | `Partida` vira `{idPartida, idVencedor, idPerdedor, pontuacaoJogador1, pontuacaoJogador2, detalhes}` |
| `ClienteDicas` | `Recomendacao-de-cartas` (C#/.NET) | `Partida` vira `{jogador: {campo, mao, hp}, oponente: {...}}` com token Bearer |

### 2.4 Decorator: cache e plano B sem mexer nas classes originais
**Onde:** `controllers/provedor_cache.py`, `controllers/fonte_cartas_local.py`

`ProvedorPokemonComCache` implementa `ProvedorPokemon` e envolve outro `ProvedorPokemon`, guardando o que já foi buscado. `FonteCartasComReserva` implementa `FonteCartas` e, se a Distribuição de Cartas cair, usa a mão sorteada localmente.

```python
provedor = ProvedorPokemonComCache(PokeApiProvider())
fonte = FonteCartasComReserva(ClienteDistribuicao(url, provedor), FonteCartasLocal(provedor))
```

### 2.5 Repository: onde as partidas ficam guardadas
**Onde:** `interfaces/repositorio_partidas.py`, `controllers/repositorio_memoria.py`

Hoje as partidas ficam em memória. Para usar banco de dados basta outra classe que implemente `RepositorioPartidas`; o `ServicoBatalha` não muda.

### 2.6 Injeção de Dependência e Composition Root
**Onde:** `composicao.py`

É o único arquivo que dá `new` (instancia) nas classes concretas. Ele lê as variáveis de ambiente e decide, por exemplo, se usa a PokéAPI ou o catálogo offline, e se usa a Distribuição de Cartas ou a mão local.

### 2.7 Test Doubles (Fakes)
**Onde:** `controllers/provedor_fake.py`, `tests/fakes.py`

`ProvedorFake`, `GestaoFake`, `MaosFixas` e `GeradorFixo` implementam as mesmas interfaces das classes reais. Com eles, os 43 testes rodam sem internet e o sorteio fica previsível.

---

## 3. SOLID no código

| Princípio | Onde ver | Como aparece |
| :--- | :--- | :--- |
| **SRP** | `Partida`, `JuizRodada`, `CalculadoraDano` | `Partida` só guarda o estado (turno, placar, campo, revezamento). `CalculadoraDano` só calcula força. `JuizRodada` só faz o sorteio ponderado. |
| **OCP** | `CalculadoraDano` + `ModificadorDano` | Regra nova de dano é classe nova, sem alterar a calculadora (ver teste do clima). |
| **LSP** | `PokeApiProvider` × `ProvedorFake` × `ProvedorPokemonComCache` | Os três entram no mesmo lugar e o resto do sistema não percebe a diferença. |
| **ISP** | `IniciadorPartida`, `AcoesJogador`, `SolicitadorPareamento`, `NotificadorPartidas` | A Gestão de Partidas usa só `IniciadorPartida`; o jogador usa só `AcoesJogador`. |
| **DIP** | construtor do `ServicoBatalha` | Recebe só interfaces. Quem escolhe as classes concretas é o `composicao.py`. |

---

## 4. Regras de negócio e onde foram implementadas

| Regra | Arquivo | Teste que prova |
| :--- | :--- | :--- |
| RN01 Revezamento (ímpar começa J1, par começa J2) | `Partida.ordem_da_rodada` | `test_partida.py::test_revezamento_rodada_par_comeca_o_jogador2` |
| RN02 Vencedor fica em campo, perdedor perde a carta | `Partida.registrar_vitoria` / `registrar_jogada` | `test_vencedor_permanece_em_campo_e_perdedor_perde_a_carta`, `test_vencedor_nao_pode_trocar_de_carta` |
| RN03 Força = dano base × vantagem de tipo × bônus de velocidade | `CalculadoraDano`, `VantagemElemento`, `BonusVelocidade` | `test_calculadora_dano.py::test_exemplo_da_documentacao_rn04` (Squirtle 80 × Charmander 23) |
| RN04 Sorteio ponderado `P(J1) = S1 / (S1 + S2)` | `JuizRodada.resolver` | `test_servico_batalha.py::test_sorteio_ponderado_decide_a_rodada` |
| RN05 Vence quem ganhar mais das 5 rodadas | `Partida.vencedor` | `test_cinco_rodadas_e_fim_de_partida` |

Detalhe da RN03: defensor com dois tipos multiplica os dois fatores (elétrico contra água/voador = 4x). As imunidades do jogo original (ex.: normal contra fantasma) contam como 0.5x, porque a força precisa ser maior que zero para o sorteio.

---

## 5. Roteiro de demonstração

1. `python app.py` dentro de `src/` (sobe em `http://localhost:3001`) e `python -m http.server 5371` dentro de `src/components/`.
2. Abrir `http://localhost:5371`. Com o gerenciador rodando (`USE_MOCK_BATALHA=false`), os dois jogadores entram na fila. Sem ele: digitar um ID, abrir "Sem o gerenciador? Criar a partida direto na batalha", digitar o ID do adversário e criar.
3. Abrir o link do adversário em outra aba. Cada aba é um jogador.
4. Jogar: clicar na carta, clicar no golpe. A faixa de cima mostra força, chance e sorteio de cada rodada.
5. Mostrar `pytest` passando e o teste do clima (OCP).
