// conversa com o back-end (FastAPI). Todos os dados vêm daqui, sem dado de exemplo.

// pra apontar pra outro servidor: window.DEMO_API = "https://..." antes deste arquivo, ou ?api=... na URL
const API = (function () {
  const daUrl = new URLSearchParams(location.search).get("api");
  return (window.DEMO_API || daUrl || "http://localhost:8000").replace(/\/$/, "");
})();

// localStorage pode dar erro (aba anônima, site bloqueado), então tudo passa por aqui
function lerStorage(chave) {
  try { return localStorage.getItem(chave); } catch (e) { return null; }
}

// sem valor apaga a chave
function gravarStorage(chave, valor) {
  try {
    if (valor) localStorage.setItem(chave, valor);
    else localStorage.removeItem(chave);
  } catch (e) {}
}

function pegarToken() { return lerStorage("token"); }
function salvarToken(token) { gravarStorage("token", token); }

// erro com o status HTTP junto, pra quem chamou decidir a mensagem
class ErroApi extends Error {
  constructor(status, detalhe) {
    super(detalhe || "Erro " + status);
    this.status = status;
  }
}

// fetch base: põe o token, transforma a resposta em JSON e joga ErroApi se der errado
async function requisicao(caminho, opcoes = {}) {
  const headers = { ...(opcoes.headers || {}) };
  const token = pegarToken();
  if (token) headers.Authorization = "Bearer " + token;

  let corpo = opcoes.body;
  if (corpo && !(corpo instanceof URLSearchParams) && typeof corpo !== "string") {
    headers["Content-Type"] = "application/json";
    corpo = JSON.stringify(corpo);
  }

  const resposta = await fetch(API + caminho, { ...opcoes, headers, body: corpo });

  if (!resposta.ok) {
    let detalhe = "";
    try { detalhe = (await resposta.json()).detail; } catch (e) {}
    throw new ErroApi(resposta.status, typeof detalhe === "string" ? detalhe : "");
  }

  if (resposta.status === 204) return null;
  return resposta.json();
}

const api = {
  stats: () => requisicao("/stats"),

  // o login do FastAPI (OAuth2PasswordRequestForm) espera formulário, não JSON
  login: (apelido, senha) =>
    requisicao("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: apelido, password: senha }),
    }),

  cadastrar: (apelido, senha) =>
    requisicao("/auth/register", { method: "POST", body: { name: apelido, password: senha } }),

  eu: () => requisicao("/auth/me"),

  lampadas: (salao) => requisicao("/capsules?hall=" + encodeURIComponent(salao)),

  lampada: (id) => requisicao("/capsules/" + id),

  criarLampada: (dados) => requisicao("/capsules", { method: "POST", body: dados }),

  // roleta: uma lâmpada pública que já abriu (404 se não tiver nenhuma)
  sortear: (salao) => requisicao("/capsules/random" + (salao ? "?hall=" + encodeURIComponent(salao) : "")),

  musica: (salao) => requisicao("/halls/" + encodeURIComponent(salao) + "/track"),

  // valor 1 (gostei) ou -1 (não gostei); as duas devolvem a lâmpada com o score novo
  votar: (id, valor) => requisicao("/capsules/" + id + "/vote", { method: "PUT", body: { value: valor } }),

  tirarVoto: (id) => requisicao("/capsules/" + id + "/vote", { method: "DELETE" }),

  denunciar: (id) => requisicao("/capsules/" + id + "/report", { method: "POST", body: {} }),

  // só lâmpadas abertas com score positivo, da mais votada pra menos
  ranking: (limite = 20) => requisicao("/ranking?limit=" + limite),
};
