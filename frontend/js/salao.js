// salão: busca as lâmpadas, faz elas subirem pela tela e conta o tempo até cada uma abrir

const SALOES = {
  asiatico: "Asiático",
  medieval: "Medieval",
  cyberpunk: "Cyberpunk",
  espaco: "Espaço",
  estacoes: "Estações",
};

const MAX_LAMPADAS_NA_TELA = 14;
let lampadasAtuais = [];
let timerCronometro = null;
let salaoCarregado = null;

// "3d 05h", "02:14:37", "42:09" ou "00:00" quando já abriu
function formatarTempo(ms) {
  if (ms <= 0) return "00:00";
  const s = Math.floor(ms / 1000);
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  const seg = s % 60;
  const dois = (n) => String(n).padStart(2, "0");

  if (d > 0) return d + "d " + dois(h) + "h";
  if (h > 0) return dois(h) + ":" + dois(m) + ":" + dois(seg);
  return dois(m) + ":" + dois(seg);
}

// texto mais "humano" pro aviso e pro leitor de tela
function tempoPorExtenso(ms) {
  const min = Math.ceil(ms / 60000);
  if (min < 60) return min + (min === 1 ? " minuto" : " minutos");
  const h = Math.round(min / 60);
  if (h < 24) return h + (h === 1 ? " hora" : " horas");
  const d = Math.round(h / 24);
  return d + (d === 1 ? " dia" : " dias");
}

// embaralha (Fisher-Yates) pra ordem das colunas não ficar sempre igual
function embaralhar(lista) {
  const copia = lista.slice();
  for (let i = copia.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copia[i], copia[j]] = [copia[j], copia[i]];
  }
  return copia;
}

function desenharLampadas(lista) {
  const ceu = document.getElementById("salao-ceu");
  ceu.innerHTML = "";

  const celular = innerWidth < 700;
  const colunas = celular ? 3 : 6;
  const escolhidas = embaralhar(lista).slice(0, MAX_LAMPADAS_NA_TELA);

  escolhidas.forEach((lampada, i) => {
    // espalha em colunas e distribui os atrasos, pra não subirem todas juntas
    const coluna = i % colunas;
    const largura = 100 / colunas;
    const x = largura * coluna + largura / 2 + sortear(-largura / 4, largura / 4);
    const dur = sortear(55, 80);
    const atraso = -((i / escolhidas.length) * dur + sortear(0, 6));
    const longe = Math.random() < 0.35;

    const el = document.createElement("button");
    el.className = "lampada";
    el.type = "button";
    el.dataset.id = lampada.id;
    el.dataset.abre = new Date(lampada.open_at).getTime();
    el.style.setProperty("--x", Math.min(92, Math.max(8, x)) + "%");
    el.style.setProperty("--y", sortear(10, 75) + "%");
    el.style.setProperty("--dur", dur + "s");
    el.style.setProperty("--atraso", atraso + "s");
    el.style.setProperty("--balanco", sortear(5, 8) + "s");
    el.style.setProperty("--escala", longe ? 0.72 : 1);
    if (longe) el.style.opacity = 0.8;

    el.innerHTML = `
      <span class="lampada__corpo">
        <img class="lampada__img lanterna-tema" src="${imagemLanterna()}" alt="">
        <span class="lampada__tempo"></span>
      </span>`;

    el.addEventListener("click", () => clicarLampada(lampada, el));
    ceu.appendChild(el);
  });

  atualizarCronometros();
}

// roda 1x por segundo pra todas as lâmpadas da tela
function atualizarCronometros() {
  const agora = Date.now();
  document.querySelectorAll(".lampada").forEach((el) => {
    const falta = Number(el.dataset.abre) - agora;
    const pronta = falta <= 0;
    el.querySelector(".lampada__tempo").textContent = formatarTempo(falta);

    el.classList.toggle("pronta", pronta);

    el.setAttribute("aria-label", pronta
      ? "Lâmpada aberta, clique pra ler"
      : "Lâmpada fechada, abre em " + tempoPorExtenso(falta));
  });
}

async function clicarLampada(lampada, el) {
  const falta = Number(el.dataset.abre) - Date.now();
  if (falta > 0) {
    mostrarAviso("Essa lâmpada ainda tá fechada. Abre em " + tempoPorExtenso(falta) + ".");
    return;
  }

  // se abriu enquanto a pessoa tava na página, a lista não tem o texto ainda: busca de novo
  // (e guarda na própria lâmpada, pra próxima vez já ter)
  if (!lampada.content) {
    try {
      Object.assign(lampada, await api.lampada(lampada.id));
    } catch (e) {
      mostrarAviso("Não deu pra abrir essa lâmpada agora.");
      return;
    }
  }

  abrirLeitura(lampada);
}

// lâmpada denunciada some do salão na hora
function tirarDoSalao(lampada) {
  lampadasAtuais = lampadasAtuais.filter((l) => l.id !== lampada.id);
  const el = document.querySelector('.lampada[data-id="' + lampada.id + '"]');
  if (el) el.remove();
}

// ---------- "i" do Como funciona ----------
// abre no clique; fecha clicando de novo, clicando no pop, clicando fora ou depois de 15 segundos
let timerInfo = null;

function definirInfo(aberto) {
  const pop = document.getElementById("info-pop");
  const btn = document.getElementById("info-btn");
  pop.hidden = !aberto;
  btn.setAttribute("aria-expanded", String(aberto));
  clearTimeout(timerInfo);
  if (aberto) timerInfo = setTimeout(() => definirInfo(false), 15000);
}

function iniciarSalao() {
  document.addEventListener("denunciou", (e) => tirarDoSalao(e.detail));
}

function iniciarInfo() {
  const btn = document.getElementById("info-btn");
  const pop = document.getElementById("info-pop");

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    definirInfo(pop.hidden);
  });
  pop.addEventListener("click", (e) => {
    e.stopPropagation();
    definirInfo(false);
  });
  document.addEventListener("click", () => { if (!pop.hidden) definirInfo(false); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !pop.hidden) definirInfo(false); });
}

async function abrirSalao(salao) {
  document.getElementById("salao-nome").textContent = SALOES[salao];
  tocarMusicaDoSalao(salao);

  if (salaoCarregado === salao && lampadasAtuais.length) return;
  salaoCarregado = salao;

  const info = document.getElementById("salao-info");
  info.textContent = "carregando lâmpadas…";

  let lista;
  let total;
  try {
    // as duas juntas; se só o stats falhar, conta pela lista mesmo
    const [resposta, stats] = await Promise.all([api.lampadas(salao), api.stats().catch(() => null)]);
    lista = resposta;
    total = stats ? stats.capsules_per_hall[salao] : lista.length;
  } catch (e) {
    // back fora do ar: não inventa lâmpada, só avisa e deixa tentar de novo depois
    salaoCarregado = null;
    lampadasAtuais = [];
    document.getElementById("salao-ceu").innerHTML = "";
    info.textContent = "Não deu pra conectar com o servidor. Tenta recarregar a página.";
    return;
  }

  lampadasAtuais = lista;
  info.textContent = lista.length
    ? total + (total === 1 ? " lâmpada subindo agora" : " lâmpadas subindo agora")
    : "Nenhuma lâmpada ainda. Que tal criar a primeira?";

  desenharLampadas(lista);

  if (!timerCronometro) timerCronometro = setInterval(atualizarCronometros, 1000);
}
