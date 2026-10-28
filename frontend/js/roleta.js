// roleta: uma faixa de lanternas gira e freia numa delas, que abre uma mensagem sorteada

const LARGURA_CELULA = 132;   // tem que bater com .roleta__celula no CSS
const CELULAS = 44;
const ALVO = 36;              // a lanterna onde a faixa para
const DURACAO_GIRO = 4200;

let girando = false;
let lampadaDaRoleta = null;  // a que tá aberta no resultado, pra sumir se for denunciada

function montarFaixa() {
  const faixa = document.getElementById("roleta-faixa");
  faixa.innerHTML = "";
  for (let i = 0; i < CELULAS; i++) {
    const celula = document.createElement("div");
    celula.className = "roleta__celula";
    const img = document.createElement("img");
    img.src = imagemLanterna(lanternaAleatoria());
    img.alt = "";
    // tamanhos levemente diferentes pra não parecer carimbo
    img.style.setProperty("--escala", (0.82 + Math.random() * 0.22).toFixed(2));
    celula.appendChild(img);
    faixa.appendChild(celula);
  }
}

// deslocamento pra deixar a célula "indice" no meio da janela
function posicaoDaCelula(indice, sorteio = 0) {
  const janela = document.getElementById("roleta-janela").clientWidth;
  return -(indice * LARGURA_CELULA + LARGURA_CELULA / 2 - janela / 2 + sorteio);
}

// devolve a lâmpada, "nenhuma" (404: nenhuma abriu ainda) ou "erro" (back fora do ar)
async function buscarSorteio() {
  try {
    return await api.sortear();
  } catch (erro) {
    return erro.status === 404 ? "nenhuma" : "erro";
  }
}

function mostrarResultado(lampada) {
  const caixa = document.getElementById("roleta-resultado");
  const info = document.getElementById("roleta-info");
  const titulo = document.getElementById("roleta-titulo");
  const texto = document.getElementById("roleta-texto");
  const acoes = document.getElementById("roleta-acoes");
  lampadaDaRoleta = typeof lampada === "object" ? lampada : null;
  acoes.hidden = !lampadaDaRoleta;

  if (lampada === "nenhuma") {
    info.textContent = "Ainda não";
    titulo.textContent = "Nenhuma lâmpada abriu ainda";
    texto.textContent = "Assim que o cronômetro de alguma zerar, ela entra na roleta. Que tal criar uma?";
  } else if (lampada === "erro") {
    info.textContent = "Sem conexão";
    titulo.textContent = "Não deu pra falar com o servidor";
    texto.textContent = "Confere se o back tá ligado e gira de novo.";
  } else {
    const dias = Math.floor((Date.now() - new Date(lampada.open_at).getTime()) / 86400000);
    const quando = dias <= 0 ? "abriu hoje" : dias === 1 ? "abriu ontem" : "abriu há " + dias + " dias";
    info.textContent = (lampada.author ? "por " + lampada.author + " · " : "") + quando;
    titulo.textContent = lampada.title || "Sem título";
    texto.textContent = lampada.content || "";
    montarAcoes(acoes, lampada);
  }

  caixa.hidden = false;
  caixa.classList.remove("revelar");
  void caixa.offsetWidth;  // reinicia a animação
  caixa.classList.add("revelar");
}

async function girar() {
  if (girando) return;
  girando = true;

  const botao = document.getElementById("btn-girar");
  const faixa = document.getElementById("roleta-faixa");
  const janela = document.getElementById("roleta-janela");
  botao.disabled = true;
  botao.textContent = "Girando…";
  document.getElementById("roleta-resultado").hidden = true;
  janela.classList.remove("parou");

  // volta pro começo sem animação e monta lanternas novas
  montarFaixa();
  faixa.style.transition = "none";
  faixa.style.transform = "translateX(" + posicaoDaCelula(2) + "px)";
  void faixa.offsetWidth;

  const pedido = buscarSorteio();  // já pede enquanto gira
  // a célula onde a faixa para vira a lanterna da sorteada, bem antes de aparecer na janela
  pedido.then((lampada) => {
    if (typeof lampada === "object") faixa.children[ALVO].firstChild.src = imagemLanterna(lampada.lantern);
  });

  const sobra = (Math.random() - 0.5) * LARGURA_CELULA * 0.5;  // para um pouquinho fora do centro, mais natural
  const tempo = reduzirMovimento.matches ? 0 : DURACAO_GIRO;
  faixa.style.transition = "transform " + tempo + "ms cubic-bezier(.12, .7, .14, 1)";
  faixa.style.transform = "translateX(" + posicaoDaCelula(ALVO, sobra) + "px)";

  const [lampada] = await Promise.all([pedido, new Promise((r) => setTimeout(r, tempo))]);

  // ajusta pro centro certinho e acende a escolhida
  faixa.style.transition = "transform 350ms ease-out";
  faixa.style.transform = "translateX(" + posicaoDaCelula(ALVO) + "px)";
  faixa.children[ALVO].classList.add(typeof lampada === "object" ? "escolhida" : "apagada");
  janela.classList.add("parou");

  setTimeout(() => {
    mostrarResultado(lampada);
    botao.disabled = false;
    botao.textContent = "Girar de novo";
    girando = false;
  }, reduzirMovimento.matches ? 0 : 450);
}

function abrirRoleta() {
  if (girando) return;
  if (!document.getElementById("roleta-faixa").children.length) {
    montarFaixa();
  }
  const faixa = document.getElementById("roleta-faixa");
  faixa.style.transition = "none";
  faixa.style.transform = "translateX(" + posicaoDaCelula(document.getElementById("roleta-resultado").hidden ? 2 : ALVO) + "px)";
}

function iniciarRoleta() {
  document.getElementById("btn-girar").addEventListener("click", girar);
  document.addEventListener("denunciou", (e) => {
    if (lampadaDaRoleta && lampadaDaRoleta.id === e.detail.id) document.getElementById("roleta-resultado").hidden = true;
  });
  window.addEventListener("resize", () => {
    if (!document.getElementById("pagina-roleta").hidden && !girando) abrirRoleta();
  });
}
