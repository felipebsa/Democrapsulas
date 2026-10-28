// começo de tudo: tela de entrada, contadores e as "rotas" (#/salao/asiatico, #/roleta...)

const PAGINAS = {
  criar: "Criar Lâmpada",
  roleta: "Roleta",
  galeria: "Galeria",
  ranking: "Ranking",
  votacao: "Votação",
  conta: "Minha Conta",
};

// "entrou" vale só pra essa aba (sessionStorage), por isso não usa o lerStorage
function jaEntrou() {
  try { return sessionStorage.getItem("entrou") === "1"; } catch (e) { return false; }
}

function marcarEntrou() {
  try { sessionStorage.setItem("entrou", "1"); } catch (e) {}
}

// ---------- contador animado (0 até o valor em ~1.2s) ----------
function animarNumero(el, valor) {
  const formato = new Intl.NumberFormat("pt-BR");
  if (reduzirMovimento.matches) { el.textContent = formato.format(valor); return; }

  const duracao = 1200;
  const inicio = performance.now();

  function passo(agora) {
    const t = Math.min(1, (agora - inicio) / duracao);
    const suave = 1 - Math.pow(1 - t, 3);  // começa rápido e freia no fim
    el.textContent = formato.format(Math.round(valor * suave));
    if (t < 1) requestAnimationFrame(passo);
  }
  requestAnimationFrame(passo);
}

async function carregarContadores() {
  let stats;
  try {
    stats = await api.stats();
  } catch (e) {
    // back fora do ar: deixa o "—" e avisa
    mostrarAviso("Não deu pra conectar com o servidor.");
    return;
  }
  animarNumero(document.getElementById("stat-criadas"), stats.capsules);
  animarNumero(document.getElementById("stat-abertas"), stats.open_capsules);
}

// ---------- tela de entrada ----------
function iniciarEntrada() {
  const tela = document.getElementById("tela-entrada");

  document.getElementById("btn-iniciar").addEventListener("click", () => {
    destravarAudio();  // precisa ser dentro do clique
    marcarEntrou();

    tela.classList.add("saindo");
    setTimeout(() => { location.hash = "#/salao/asiatico"; }, 500);
  });
}

// ---------- rotas ----------
function mostrar(id) {
  ["tela-entrada", "pagina-salao", "pagina-criar", "pagina-roleta", "pagina-ranking", "pagina-embreve"].forEach((p) => {
    document.getElementById(p).hidden = p !== id;
  });
  document.getElementById("navbar").hidden = id === "tela-entrada";
}

function marcarLinkAtivo(rota, salao) {
  document.querySelectorAll(".nav__links .pilula").forEach((link) => {
    link.classList.toggle("ativa", link.dataset.rota === rota);
  });
  document.querySelectorAll(".dropdown__menu a, .nav__painel a").forEach((link) => {
    const destino = link.getAttribute("href");
    const ativa = destino === "#/" + rota + (salao ? "/" + salao : "");
    link.classList.toggle("ativa", ativa);
    if (ativa) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

function mostrarEmBreve(titulo) {
  document.getElementById("embreve-tag").textContent = titulo;
  mostrar("pagina-embreve");
}

function rotear() {
  const partes = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  const rota = partes[0] || "";

  fecharDropdowns();
  definirMenuCelular(false);
  definirInfo(false);
  window.scrollTo(0, 0);

  // "/" é a tela de entrada, mas quem já clicou em Iniciar nessa aba vai direto pro salão
  if (!rota) {
    if (jaEntrou()) { location.replace("#/salao/asiatico"); return; }
    document.getElementById("tela-entrada").classList.remove("saindo");
    mostrar("tela-entrada");
    carregarContadores();
    document.title = "Democrápsulas";
    return;
  }

  // abriu um link direto sem passar pela entrada: conta como entrou também
  marcarEntrou();
  atualizarNavbar();

  if (rota === "salao") {
    const salao = SALOES[partes[1]] ? partes[1] : "asiatico";
    marcarLinkAtivo("salao", salao);
    document.title = "Salão " + SALOES[salao] + " · Democrápsulas";

    if (salao === "asiatico") {
      mostrar("pagina-salao");
      abrirSalao(salao);
    } else {
      mostrarEmBreve("Salão " + SALOES[salao]);
    }
    return;
  }

  const titulo = PAGINAS[rota];
  if (!titulo) { location.replace("#/salao/asiatico"); return; }
  marcarLinkAtivo(rota);
  document.title = titulo + " · Democrápsulas";

  if (rota === "criar") { mostrar("pagina-criar"); abrirCriar(); return; }
  if (rota === "roleta") { mostrar("pagina-roleta"); abrirRoleta(); return; }
  if (rota === "ranking") { mostrar("pagina-ranking"); abrirRanking(); return; }
  mostrarEmBreve(titulo);
}

// ---------- liga tudo ----------
iniciarEfeitos();
iniciarInterface();
iniciarEntrada();
iniciarInfo();
iniciarSalao();
iniciarAcoes();
iniciarCriar();
iniciarRoleta();
iniciarRanking();
window.addEventListener("hashchange", rotear);
rotear();
