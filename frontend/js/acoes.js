// o que dá pra fazer com uma lâmpada aberta: votar (setas), denunciar e ler no modal

const ESPERA_DENUNCIA = 3;  // segundos até liberar o botão de confirmar
let lampadaDenunciada = null;
let timerDenuncia = null;

// ---------- votos e botão de denunciar ----------
// desenha os botões dentro da caixa e redesenha sozinho depois de cada voto.
// a resposta do back é copiada pro próprio objeto, então quem guardou a lâmpada já fica atualizado
function montarAcoes(caixa, lampada) {
  const meu = lampada.my_vote;
  caixa.innerHTML = `
    <div class="votos" role="group" aria-label="Votos">
      <button class="voto voto--cima${meu === 1 ? " ativo" : ""}" type="button" aria-pressed="${meu === 1}" aria-label="Gostei">
        <svg class="seta" aria-hidden="true"><use href="#i-voto"/></svg>
      </button>
      <button class="voto voto--baixo${meu === -1 ? " ativo" : ""}" type="button" aria-pressed="${meu === -1}" aria-label="Não gostei">
        <svg class="seta" aria-hidden="true"><use href="#i-voto"/></svg>
      </button>
    </div>
    <button class="denunciar" type="button" aria-label="Denunciar lâmpada" title="Denunciar"${lampada.is_mine ? " hidden" : ""}>
      <svg class="bloqueio" aria-hidden="true"><use href="#i-bloqueio"/></svg>
    </button>`;

  caixa.querySelector(".voto--cima").addEventListener("click", () => votar(caixa, lampada, 1));
  caixa.querySelector(".voto--baixo").addEventListener("click", () => votar(caixa, lampada, -1));
  caixa.querySelector(".denunciar").addEventListener("click", () => pedirDenuncia(lampada));
}

// clicar de novo no mesmo voto tira ele
async function votar(caixa, lampada, valor) {
  if (!usuario) {
    mostrarAviso("Entre na sua conta pra votar.");
    abrirLogin();
    return;
  }

  caixa.querySelectorAll(".voto").forEach((b) => { b.disabled = true; });
  try {
    const nova = lampada.my_vote === valor ? await api.tirarVoto(lampada.id) : await api.votar(lampada.id, valor);
    Object.assign(lampada, nova);
    document.dispatchEvent(new CustomEvent("votou", { detail: lampada }));
  } catch (erro) {
    if (erro.status === 401) { deslogar(); abrirLogin(); }
    else if (erro.status === 404) mostrarAviso("Essa lâmpada não existe mais.");
    else mostrarAviso("Não deu pra votar agora. Tenta de novo.");
  }
  montarAcoes(caixa, lampada);
}

// ---------- modal de denúncia ----------
function pedirDenuncia(lampada) {
  if (!usuario) {
    mostrarAviso("Entre na sua conta pra denunciar.");
    abrirLogin();
    return;
  }

  lampadaDenunciada = lampada;
  document.getElementById("denuncia-sub").textContent = "“" + (lampada.title || "Sem título") + "” vai ser revisada. Isso não dá pra desfazer.";
  abrirModal("modal-denuncia");
  document.getElementById("denuncia-cancelar").focus();
  contarDenuncia(ESPERA_DENUNCIA);
}

// o confirmar fica apagado com a contagem na frente e só acende quando zera
function contarDenuncia(falta) {
  const botao = document.getElementById("denuncia-confirmar");
  const contagem = document.getElementById("denuncia-contagem");
  clearTimeout(timerDenuncia);

  botao.disabled = falta > 0;
  botao.classList.toggle("esperando", falta > 0);
  contagem.hidden = falta <= 0;
  contagem.textContent = falta;
  if (falta > 0) timerDenuncia = setTimeout(() => contarDenuncia(falta - 1), 1000);
}

function fecharDenuncia() {
  clearTimeout(timerDenuncia);
  lampadaDenunciada = null;
  fecharModal("modal-denuncia");
}

async function confirmarDenuncia() {
  const lampada = lampadaDenunciada;
  const botao = document.getElementById("denuncia-confirmar");
  if (!lampada || botao.disabled) return;

  botao.disabled = true;
  try {
    await api.denunciar(lampada.id);
    mostrarAviso("Denúncia enviada. Valeu por ajudar!");
  } catch (erro) {
    if (erro.status === 409) mostrarAviso("Você já denunciou essa lâmpada.");
    else if (erro.status === 401) { fecharDenuncia(); deslogar(); abrirLogin(); return; }
    else { mostrarAviso("Não deu pra denunciar agora. Tenta de novo."); botao.disabled = false; return; }
  }

  fecharDenuncia();
  if (!document.getElementById("modal-ler").hidden) fecharModal("modal-ler");
  document.dispatchEvent(new CustomEvent("denunciou", { detail: lampada }));
}

// ---------- modal de ler ----------
function abrirLeitura(lampada) {
  document.getElementById("ler-titulo").textContent = lampada.title || "Sem título";
  const quando = new Date(lampada.open_at).toLocaleDateString("pt-BR");
  document.getElementById("ler-info").textContent = (lampada.author ? "por " + lampada.author + " · " : "") + "aberta em " + quando;
  document.getElementById("ler-texto").textContent = lampada.content || "";
  montarAcoes(document.getElementById("ler-acoes"), lampada);
  abrirModal("modal-ler");
}

function iniciarAcoes() {
  const modal = document.getElementById("modal-denuncia");
  document.getElementById("denuncia-cancelar").addEventListener("click", fecharDenuncia);
  document.getElementById("denuncia-confirmar").addEventListener("click", confirmarDenuncia);
  modal.querySelector("[data-fechar]").addEventListener("click", fecharDenuncia);
  ligarFecharPeloFundo(modal, fecharDenuncia);
}
