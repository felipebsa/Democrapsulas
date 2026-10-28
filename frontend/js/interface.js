// partes da interface: tema, som, menus da navbar, avisos e o modal de entrar/criar conta

// ---------- aviso (toast) ----------
let timerAviso;
function mostrarAviso(texto) {
  const aviso = document.getElementById("aviso");
  aviso.textContent = texto;
  aviso.classList.add("visivel");
  clearTimeout(timerAviso);
  timerAviso = setTimeout(() => aviso.classList.remove("visivel"), 3200);
}

// mensagem de erro embaixo de um formulário, marcando o campo com problema
function erroNoForm(idForm, idErro, texto, campo) {
  document.getElementById(idErro).textContent = texto;
  document.querySelectorAll("#" + idForm + " .campo").forEach((c) => c.classList.remove("invalido"));
  if (campo) { campo.classList.add("invalido"); campo.focus(); }
}

// ---------- tema ----------
function aplicarTema(claro) {
  document.documentElement.classList.toggle("claro", claro);
  gravarStorage("tema", claro ? "claro" : "escuro");

  const btn = document.getElementById("btn-tema");
  btn.querySelector("use").setAttribute("href", claro ? "#i-lua" : "#i-sol");
  btn.setAttribute("aria-label", claro ? "Mudar pro modo escuro" : "Mudar pro modo claro");

  atualizarLanternas();
}

// ---------- som ----------
const som = {
  ligado: lerStorage("som") !== "desligado",
  destravado: false,  // o navegador só deixa tocar depois de um clique (por isso existe a tela de entrada)
  audio: new Audio(),
  salao: null,
};
som.audio.loop = true;
som.audio.volume = 0.5;

function aplicarSom() {
  const btn = document.getElementById("btn-som");
  btn.querySelector("use").setAttribute("href", som.ligado ? "#i-som" : "#i-mudo");
  btn.setAttribute("aria-label", som.ligado ? "Desligar som" : "Ligar som");
  btn.setAttribute("aria-pressed", String(som.ligado));
  gravarStorage("som", som.ligado ? "ligado" : "desligado");

  if (som.ligado && som.destravado && som.audio.src) som.audio.play().catch(() => {});
  else som.audio.pause();
}

// depois do primeiro clique o navegador guarda que a pessoa interagiu com a página,
// então dali pra frente o play() funciona (mesmo a música chegando depois)
function destravarAudio() {
  som.destravado = true;
  aplicarSom();
}

// pega a música da semana do salão (vencedora da votação). Se não tiver, fica em silêncio.
async function tocarMusicaDoSalao(salao) {
  if (som.salao === salao) return;
  som.salao = salao;
  try {
    const faixa = await api.musica(salao);
    if (!faixa.song) { som.audio.removeAttribute("src"); som.audio.pause(); return; }
    som.audio.src = faixa.song.file;
    aplicarSom();
  } catch (e) {
    som.salao = null;  // back fora do ar: deixa tentar de novo na próxima vez
    som.audio.pause();
  }
}

// ---------- dropdowns e menu do celular ----------
function fecharDropdowns(menos) {
  document.querySelectorAll(".dropdown.aberto").forEach((d) => {
    if (d === menos) return;
    d.classList.remove("aberto");
    d.querySelector("[aria-expanded]").setAttribute("aria-expanded", "false");
  });
}

function ligarDropdown(idDropdown, idBotao) {
  const dropdown = document.getElementById(idDropdown);
  const botao = document.getElementById(idBotao);

  botao.addEventListener("click", (e) => {
    e.stopPropagation();
    const abrir = !dropdown.classList.contains("aberto");
    fecharDropdowns(dropdown);
    dropdown.classList.toggle("aberto", abrir);
    botao.setAttribute("aria-expanded", String(abrir));
  });
}

function definirMenuCelular(aberto) {
  document.getElementById("navbar").classList.toggle("aberta", aberto);
  const btn = document.getElementById("btn-menu");
  btn.setAttribute("aria-expanded", String(aberto));
  btn.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
  btn.querySelector("use").setAttribute("href", aberto ? "#i-x" : "#i-menu");
}

// ---------- usuário logado ----------
let usuario = null;

function mostrarUsuario() {
  document.getElementById("btn-entrar").hidden = !!usuario;
  document.getElementById("menu-usuario").hidden = !usuario;
  document.getElementById("nome-usuario").textContent = usuario ? usuario.name : "";
}

function deslogar() {
  salvarToken(null);
  usuario = null;
  mostrarUsuario();
}

async function carregarUsuario() {
  usuario = null;
  if (pegarToken()) {
    try { usuario = await api.eu(); }
    catch (e) { if (e.status === 401) salvarToken(null); }  // token vencido ou inválido
  }
  mostrarUsuario();
}

function sair() {
  deslogar();
  fecharDropdowns();
  mostrarAviso("Você saiu da conta.");
}

// ---------- modal entrar / criar conta ----------
const APELIDO_VALIDO = /^[A-Za-z0-9_]{3,20}$/;
let abaAtual = "entrar";
let focoAntesDoModal = null;

function trocarAba(aba) {
  abaAtual = aba;
  document.querySelectorAll(".aba").forEach((b) => {
    const ativa = b.dataset.aba === aba;
    b.classList.toggle("ativa", ativa);
    b.setAttribute("aria-selected", String(ativa));
  });

  const criando = aba === "criar";
  document.getElementById("auth-titulo").textContent = criando ? "Criar conta" : "Bem-vindo de volta";
  document.getElementById("auth-sub").textContent = criando
    ? "Só um apelido e uma senha. Sem e-mail."
    : "Entre pra guardar suas mensagens nas lâmpadas.";
  document.getElementById("auth-enviar").textContent = criando ? "Criar conta" : "Entrar";
  document.getElementById("campo-senha").autocomplete = criando ? "new-password" : "current-password";
  mostrarErro("");
}

function mostrarErro(texto, campo) {
  erroNoForm("form-auth", "auth-erro", texto, campo);
}

function abrirModal(id) {
  focoAntesDoModal = document.activeElement;
  const modal = document.getElementById(id);
  modal.hidden = false;
  // foca no primeiro campo; se não tiver campo (modal de ler), foca na própria caixa
  const primeiro = modal.querySelector("input") || modal.querySelector(".modal");
  primeiro.focus();
}

function fecharModal(id) {
  document.getElementById(id).hidden = true;
  if (focoAntesDoModal) focoAntesDoModal.focus();
}

function abrirLogin(aba = "entrar") {
  trocarAba(aba);
  abrirModal("modal-auth");
}

async function enviarAuth(e) {
  e.preventDefault();
  const campoApelido = document.getElementById("campo-apelido");
  const campoSenha = document.getElementById("campo-senha");
  const apelido = campoApelido.value.trim();
  const senha = campoSenha.value;

  if (!APELIDO_VALIDO.test(apelido)) return mostrarErro("O apelido precisa ter de 3 a 20 caracteres: letras, números e _", campoApelido);
  if (senha.length < 6) return mostrarErro("A senha precisa ter pelo menos 6 caracteres.", campoSenha);

  const botao = document.getElementById("auth-enviar");
  botao.disabled = true;
  mostrarErro("");

  try {
    if (abaAtual === "criar") await api.cadastrar(apelido, senha);
    const resposta = await api.login(apelido, senha);  // depois do cadastro já entra direto
    salvarToken(resposta.access_token);
    await carregarUsuario();
    fecharModal("modal-auth");
    document.getElementById("form-auth").reset();
    document.dispatchEvent(new CustomEvent("logou"));
    mostrarAviso(abaAtual === "criar" ? "Conta criada! Bem-vindo, " + apelido + "." : "Oi de novo, " + apelido + "!");
  } catch (erro) {
    if (erro.status === 409) mostrarErro("Esse apelido já existe.", campoApelido);
    else if (erro.status === 401) mostrarErro("Apelido ou senha errados.", campoSenha);
    else if (erro.status === 422) mostrarErro("Confere o apelido e a senha.");
    else mostrarErro("Não deu pra falar com o servidor. Tenta de novo daqui a pouco.");
  } finally {
    botao.disabled = false;
  }
}

// modal só fecha pelo fundo se o mouse foi apertado E solto no fundo (mesma ideia do Nippon)
function ligarFecharPeloFundo(modal, fechar) {
  let apertouNoFundo = false;
  modal.addEventListener("pointerdown", (e) => { apertouNoFundo = e.target === modal; });
  modal.addEventListener("click", (e) => {
    if (e.target === modal && apertouNoFundo) fechar();
  });
}

function iniciarInterface() {
  aplicarTema(document.documentElement.classList.contains("claro"));
  aplicarSom();

  document.getElementById("btn-tema").addEventListener("click", () => {
    aplicarTema(!document.documentElement.classList.contains("claro"));
  });

  document.getElementById("btn-som").addEventListener("click", () => {
    som.ligado = !som.ligado;
    som.destravado = true;  // foi um clique, então já pode tocar
    aplicarSom();
  });

  ligarDropdown("dropdown-saloes", "btn-saloes");
  ligarDropdown("menu-usuario", "btn-usuario");
  document.addEventListener("click", () => fecharDropdowns());

  document.getElementById("btn-menu").addEventListener("click", () => {
    definirMenuCelular(!document.getElementById("navbar").classList.contains("aberta"));
  });
  window.matchMedia("(min-width: 901px)").addEventListener("change", () => definirMenuCelular(false));

  // login
  document.getElementById("btn-entrar").addEventListener("click", () => abrirLogin());
  document.getElementById("btn-sair").addEventListener("click", sair);
  document.querySelectorAll(".aba").forEach((b) => b.addEventListener("click", () => trocarAba(b.dataset.aba)));
  document.getElementById("form-auth").addEventListener("submit", enviarAuth);
  document.getElementById("auth-fechar").addEventListener("click", () => fecharModal("modal-auth"));

  const modalAuth = document.getElementById("modal-auth");
  const modalLer = document.getElementById("modal-ler");
  ligarFecharPeloFundo(modalAuth, () => fecharModal("modal-auth"));
  ligarFecharPeloFundo(modalLer, () => fecharModal("modal-ler"));
  modalLer.querySelector("[data-fechar]").addEventListener("click", () => fecharModal("modal-ler"));

  document.addEventListener("keydown", (e) => {
    // com modal aberto, o Tab fica rodando só dentro dele
    if (e.key === "Tab") {
      const aberto = [modalAuth, modalLer].find((m) => !m.hidden);
      if (!aberto) return;
      const focaveis = [...aberto.querySelectorAll("button, input, a[href]")].filter((el) => !el.disabled && el.offsetParent);
      const primeiro = focaveis[0];
      const ultimo = focaveis[focaveis.length - 1];
      if (e.shiftKey && (document.activeElement === primeiro || !aberto.contains(document.activeElement))) { e.preventDefault(); ultimo.focus(); }
      else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primeiro.focus(); }
      return;
    }
    if (e.key !== "Escape") return;
    if (!modalAuth.hidden) fecharModal("modal-auth");
    else if (!modalLer.hidden) fecharModal("modal-ler");
    else { fecharDropdowns(); definirMenuCelular(false); }
  });

  carregarUsuario();
}
