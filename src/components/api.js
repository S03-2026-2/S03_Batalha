  // Funções compartilhadas pelas duas telas.
const { GESTAO_URL, BATALHA_URL, INTERVALO_MS } = window.CONFIG;


const esperar = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Chama o gerenciador e devolve { status, ok, corpo }.
// Só lança erro quando não consegue falar com o servidor.
async function chamarGestao(caminho, opcoes) {
  let resposta;
  try {
    resposta = await fetch(GESTAO_URL + caminho, opcoes);
  } catch {
    throw new Error(`Sem resposta do gerenciador em ${GESTAO_URL}. Confira se ele está rodando.`);
  }
  let corpo = null;
  try {
    corpo = await resposta.json();
  } catch {
    // resposta sem JSON
  }
  return { status: resposta.status, ok: resposta.ok, corpo };
}

// Partidas do jogador, da mais recente para a mais antiga.
async function historico(idJogador) {
  const r = await chamarGestao(`/jogadores/${encodeURIComponent(idJogador)}/partidas`);
  if (!r.ok) throw new Error(r.corpo?.erro || "Não foi possível consultar as partidas.");
  return r.corpo;
}

const adversarioDe = (partida, idJogador) =>
  partida.idJogador1 === idJogador ? partida.idJogador2 : partida.idJogador1;

const urlDaArena = (idPartida, idJogador) =>
  `batalha.html?partida=${encodeURIComponent(idPartida)}&jogador=${encodeURIComponent(idJogador)}`;

// Chama o sistema de batalhas (S03_Batalha). Devolve { status, ok, corpo }.
async function chamarBatalha(caminho, opcoes) {
  let resposta;
  try {
    resposta = await fetch(BATALHA_URL + caminho, opcoes);
  } catch {
    throw new Error(`Sem resposta da batalha em ${BATALHA_URL}. Confira se ela está rodando (python app.py).`);
  }
  let corpo = null;
  try {
    corpo = await resposta.json();
  } catch {
    // resposta sem JSON
  }
  return { status: resposta.status, ok: resposta.ok, corpo };
}

const postJson = (corpo) => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(corpo),
});
