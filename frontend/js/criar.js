// página Criar Lâmpada: formulário, prévia com o cronômetro e envio pro POST /capsules

const criar = {
  abreEm: 0,             // horário (ms) em que a lâmpada vai abrir
  lanterna: lanternaAleatoria(),
  esperandoLogin: false, // clicou em soltar sem estar logado
  enviando: false,
};

function textoQuandoAbre(ms) {
  const data = new Date(ms);
  const hoje = new Date();
  const amanha = new Date(); amanha.setDate(hoje.getDate() + 1);
  const hora = data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

  if (data.toDateString() === hoje.toDateString()) return "abre hoje às " + hora;
  if (data.toDateString() === amanha.toDateString()) return "abre amanhã às " + hora;
  return "abre em " + data.toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" }) + " às " + hora;
}

function atualizarPrevia() {
  const falta = criar.abreEm - Date.now();
  document.getElementById("criar-tempo").textContent = formatarTempo(falta);
  document.getElementById("criar-abre").textContent = falta > 0 ? textoQuandoAbre(criar.abreEm) : "escolhe daqui quanto tempo ela abre";
}

// setinhas da prévia: anda pelas lanternas e dá a volta nas pontas
function trocarLanterna(passo) {
  criar.lanterna = (criar.lanterna - 1 + passo + LANTERNAS.length) % LANTERNAS.length + 1;
  document.getElementById("criar-lanterna").src = imagemLanterna(criar.lanterna);
  document.getElementById("criar-lanterna-num").textContent = criar.lanterna + " / " + LANTERNAS.length;
}

// junta dias + horas + minutos (sem limite máximo) e calcula quando abre a partir de agora
function lerTempo() {
  const numero = (id) => {
    const v = Math.floor(Number(document.getElementById(id).value));
    return Number.isFinite(v) && v > 0 ? v : 0;
  };
  const segundos = numero("criar-dias") * 86400 + numero("criar-horas") * 3600 + numero("criar-minutos") * 60;
  criar.abreEm = segundos > 0 ? Date.now() + segundos * 1000 : 0;
  atualizarPrevia();
  return segundos;
}

// o limite vem do maxlength do HTML
function atualizarContagem(campo, idContagem) {
  document.getElementById(idContagem).textContent = campo.value.length + "/" + campo.maxLength;
}

// rascunho fica salvo no navegador pra não perder o texto se sair da página
function salvarRascunho() {
  gravarStorage("rascunho", JSON.stringify({
    titulo: document.getElementById("criar-titulo").value,
    texto: document.getElementById("criar-texto").value,
  }));
}

function carregarRascunho() {
  try {
    const r = JSON.parse(lerStorage("rascunho") || "{}");
    if (r.titulo) document.getElementById("criar-titulo").value = r.titulo;
    if (r.texto) document.getElementById("criar-texto").value = r.texto;
  } catch (e) {}
  atualizarContagem(document.getElementById("criar-titulo"), "conta-titulo");
  atualizarContagem(document.getElementById("criar-texto"), "conta-texto");
}

function erroCriar(texto, campo) {
  erroNoForm("form-criar", "criar-erro", texto, campo);
}

// as mensagens do back vêm em inglês, aqui vira algo que a pessoa entende
function mensagemDoErro(erro) {
  const detalhe = (erro.message || "").toLowerCase();
  if (erro.status === 429) {
    const segundos = detalhe.match(/(\d+)\s*seconds/);
    if (segundos) return "Calma! Espera " + segundos[1] + " segundos pra soltar outra lâmpada.";
    return "Você já soltou todas as lâmpadas de hoje. Volta amanhã!";
  }
  if (erro.status === 422 && detalhe.includes("inappropriate")) return "Tem alguma palavra que não pode na mensagem ou no título.";
  if (erro.status === 422 && detalhe.includes("future")) return "O tempo pra abrir precisa ser no futuro.";
  if (erro.status === 422) return "Confere os campos: título até 80 e mensagem até 1000 caracteres.";
  return "Não deu pra falar com o servidor. Tenta de novo daqui a pouco.";
}

async function enviarLampada(e) {
  if (e) e.preventDefault();
  if (criar.enviando) return;

  const campoTitulo = document.getElementById("criar-titulo");
  const campoTexto = document.getElementById("criar-texto");
  const titulo = campoTitulo.value.trim();
  const texto = campoTexto.value.trim();
  const salao = document.getElementById("criar-salao").value;

  if (!titulo) return erroCriar("Dá um título pra sua lâmpada.", campoTitulo);
  if (!texto) return erroCriar("Escreve a mensagem que vai dentro da lâmpada.", campoTexto);
  // recalcula na hora de enviar, pra contar a partir de agora
  if (lerTempo() < 60) return erroCriar("Coloca pelo menos 1 minuto pra ela abrir.", document.getElementById("criar-minutos"));
  erroCriar("");

  if (!usuario) {
    criar.esperandoLogin = true;
    mostrarAviso("Entra na sua conta pra soltar a lâmpada.");
    abrirLogin();
    return;
  }

  const botao = document.getElementById("criar-enviar");
  criar.enviando = true;
  botao.disabled = true;
  botao.textContent = "Soltando…";

  try {
    await api.criarLampada({
      hall: salao,
      title: titulo,
      content: texto,
      lantern: criar.lanterna,
      is_private: false,  // lâmpada privada ainda está em breve
      open_at: new Date(criar.abreEm).toISOString(),
    });
    lampadaCriada();
  } catch (erro) {
    if (erro.status === 401) {
      // token venceu (dura 30 min no back): pede pra entrar de novo e tenta depois
      deslogar();
      criar.esperandoLogin = true;
      abrirLogin();
      erroCriar("Sua sessão expirou. Entra de novo que a lâmpada sai em seguida.");
    } else {
      erroCriar(mensagemDoErro(erro));
    }
  } finally {
    criar.enviando = false;
    botao.disabled = false;
    botao.textContent = "Soltar lâmpada";
  }
}

function lampadaCriada() {
  gravarStorage("rascunho", null);
  salaoCarregado = null;  // força o salão a buscar de novo e mostrar a nova

  document.getElementById("criar-lampada").classList.add("solta");
  document.getElementById("pronto-lanterna").src = imagemLanterna(criar.lanterna);

  setTimeout(() => {
    document.getElementById("pronto-texto").textContent =
      "Ela " + textoQuandoAbre(criar.abreEm) + ". Até lá, só aparece o cronômetro.";
    document.querySelector(".criar").hidden = true;
    document.getElementById("criar-pronto").hidden = false;
    window.scrollTo(0, 0);
  }, reduzirMovimento.matches ? 0 : 1100);
}

function resetarCriar() {
  document.getElementById("form-criar").reset();
  document.getElementById("criar-lampada").classList.remove("solta");
  document.querySelector(".criar").hidden = false;
  document.getElementById("criar-pronto").hidden = true;
  carregarRascunho();
  lerTempo();
  erroCriar("");
}

// chamada pelo roteador toda vez que entra na página
function abrirCriar() {
  if (!document.getElementById("criar-pronto").hidden) return;
  lerTempo();  // o tempo conta a partir de agora
}

function iniciarCriar() {
  const campoTitulo = document.getElementById("criar-titulo");
  const campoTexto = document.getElementById("criar-texto");

  carregarRascunho();
  lerTempo();
  trocarLanterna(0);

  document.getElementById("lanterna-anterior").addEventListener("click", () => trocarLanterna(-1));
  document.getElementById("lanterna-proxima").addEventListener("click", () => trocarLanterna(1));
  campoTitulo.addEventListener("input", () => { atualizarContagem(campoTitulo, "conta-titulo"); salvarRascunho(); });
  campoTexto.addEventListener("input", () => { atualizarContagem(campoTexto, "conta-texto"); salvarRascunho(); });
  document.querySelectorAll("#tempo-livre input").forEach((campo) => campo.addEventListener("input", lerTempo));

  document.getElementById("form-criar").addEventListener("submit", enviarLampada);
  document.getElementById("btn-criar-outra").addEventListener("click", resetarCriar);

  // entrou na conta pelo modal depois de clicar em soltar: solta de uma vez
  document.addEventListener("logou", () => {
    if (!criar.esperandoLogin) return;
    criar.esperandoLogin = false;
    if (!document.getElementById("pagina-criar").hidden) enviarLampada();
  });

  setInterval(() => {
    if (!document.getElementById("pagina-criar").hidden) atualizarPrevia();
  }, 1000);
}
