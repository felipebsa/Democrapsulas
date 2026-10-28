// ranking: pódio com as 3 lâmpadas mais votadas e o resto (4º ao 20º) numa lista embaixo

const TAMANHO_RANKING = 20;
let lampadasDoRanking = [];
let pedidoRanking = 0;  // se pedir de novo antes da resposta chegar, a resposta velha é ignorada

function textoVotos(score) {
  return score + (score === 1 ? " voto" : " votos");
}

// cria um elemento com classe e texto (sempre textContent, a mensagem é de quem escreveu)
function criarEl(tag, classe, texto) {
  const el = document.createElement(tag);
  if (classe) el.className = classe;
  if (texto !== undefined) el.textContent = texto;
  return el;
}

function montarLugar(lampada, posicao) {
  const lugar = criarEl("button", "podio__lugar podio__lugar--" + posicao);
  lugar.type = "button";
  lugar.setAttribute("aria-label", posicao + "º lugar: " + (lampada.title || "Sem título") + ", " + textoVotos(lampada.score));

  const lanterna = criarEl("span", "podio__lanterna");
  const img = criarEl("img");
  mostrarLanterna(img, lampada.lantern);
  img.alt = "";
  lanterna.append(img, criarEl("span", "podio__titulo", lampada.title || "Sem título"));

  const base = criarEl("span", "podio__base");
  base.append(
    criarEl("span", "podio__pos", posicao),
    criarEl("span", "podio__votos", textoVotos(lampada.score)),
    criarEl("span", "podio__autor", lampada.author ? "por " + lampada.author : ""),
  );

  lugar.append(lanterna, base);
  lugar.addEventListener("click", () => abrirLeitura(lampada));
  return lugar;
}

function montarItem(lampada, posicao) {
  const item = criarEl("li");
  const botao = criarEl("button", "ranking__item");
  botao.type = "button";

  const miolo = criarEl("span", "ranking__miolo");
  miolo.append(
    criarEl("b", "ranking__titulo", lampada.title || "Sem título"),
    criarEl("span", "ranking__previa", lampada.content || ""),
    criarEl("span", "ranking__autor", lampada.author ? "por " + lampada.author : ""),
  );

  botao.append(criarEl("span", "ranking__pos", posicao), miolo, criarEl("span", "ranking__score", textoVotos(lampada.score)));
  botao.addEventListener("click", () => abrirLeitura(lampada));
  item.appendChild(botao);
  return item;
}

function desenharRanking(lista) {
  const podio = document.getElementById("ranking-podio");
  const listaEl = document.getElementById("ranking-lista");
  podio.innerHTML = "";
  listaEl.innerHTML = "";

  lista.slice(0, 3).forEach((lampada, i) => podio.appendChild(montarLugar(lampada, i + 1)));
  lista.slice(3).forEach((lampada, i) => listaEl.appendChild(montarItem(lampada, i + 4)));
  listaEl.hidden = lista.length <= 3;
}

async function abrirRanking() {
  const info = document.getElementById("ranking-info");
  const pedido = ++pedidoRanking;
  if (!lampadasDoRanking.length) info.textContent = "carregando…";

  let lista;
  try {
    lista = await api.ranking(TAMANHO_RANKING);
  } catch (e) {
    if (pedido !== pedidoRanking) return;
    info.textContent = "Não deu pra conectar com o servidor. Tenta recarregar a página.";
    return;
  }
  if (pedido !== pedidoRanking) return;

  lampadasDoRanking = lista;
  // com lâmpada no ranking não precisa de texto, só fala algo quando tá vazio
  info.textContent = lista.length ? "" : "Nenhuma lâmpada com voto ainda. Abre umas na roleta e vota!";  desenharRanking(lista);
}

// voto, denúncia ou login mudam a ordem: busca de novo se a página tá aberta
function atualizarRankingSeAberto() {
  if (!document.getElementById("pagina-ranking").hidden) abrirRanking();
}

function iniciarRanking() {
  ["votou", "denunciou", "logou"].forEach((evento) => document.addEventListener(evento, atualizarRankingSeAberto));
}
