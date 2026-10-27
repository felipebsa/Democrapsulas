// efeitos visuais: lâmpadas fantasma, parallax do fundo, luz do mouse e navbar de vidro

const reduzirMovimento = window.matchMedia("(prefers-reduced-motion: reduce)");
const temMouse = window.matchMedia("(hover: hover) and (pointer: fine)");

// imagem da lanterna muda com o tema
function imagemLanterna() {
  return document.documentElement.classList.contains("claro")
    ? "img/lanterna-asiatica-dia.png"
    : "img/lanterna-asiatica.png";
}

function sortear(min, max) {
  return min + Math.random() * (max - min);
}

// ---------- lâmpadas fantasma ----------
// 3 camadas: longe (pequena, borrada, lenta), meio e perto (maior, nítida, mais rápida)
const CAMADAS = [
  { qtd: 4, tam: [24, 36], op: 0.05, blur: 2, dur: [40, 60] },
  { qtd: 4, tam: [44, 60], op: 0.09, blur: 1, dur: [28, 40] },
  { qtd: 3, tam: [70, 90], op: 0.13, blur: 0, dur: [18, 26] },
];

function criarFantasmas() {
  const caixa = document.getElementById("fantasmas");
  caixa.innerHTML = "";

  CAMADAS.forEach((camada) => {
    for (let i = 0; i < camada.qtd; i++) {
      const dur = sortear(camada.dur[0], camada.dur[1]);
      const el = document.createElement("div");
      el.className = "fantasma";
      el.style.setProperty("--x", sortear(2, 96) + "%");
      el.style.setProperty("--y", sortear(10, 85) + "%"); // só usado com movimento reduzido
      el.style.setProperty("--tam", sortear(camada.tam[0], camada.tam[1]) + "px");
      el.style.setProperty("--dur", dur + "s");
      el.style.setProperty("--atraso", -sortear(0, dur) + "s"); // negativo = já começa no meio do caminho
      el.style.setProperty("--balanco", sortear(4, 7) + "s");
      el.style.setProperty("--op", camada.op);
      el.style.setProperty("--blur", camada.blur + "px");

      const img = document.createElement("img");
      img.src = imagemLanterna();
      img.alt = "";
      img.className = "lanterna-tema";
      el.appendChild(img);
      caixa.appendChild(el);
    }
  });
}

// troca todas as lanternas da página quando o tema muda
function atualizarLanternas() {
  const src = imagemLanterna();
  document.querySelectorAll(".lanterna-tema").forEach((img) => { img.src = src; });
}

// ---------- parallax ----------
// o alvo segue o mouse e a posição real vai "andando" até ele (lerp), pra ficar suave
const parallax = { alvoX: 0, alvoY: 0, x: 0, y: 0, rodando: false };

function moverParallax() {
  parallax.x += (parallax.alvoX - parallax.x) * 0.06;
  parallax.y += (parallax.alvoY - parallax.y) * 0.06;

  const raiz = document.documentElement.style;
  raiz.setProperty("--px", parallax.x.toFixed(2) + "px");
  raiz.setProperty("--py", parallax.y.toFixed(2) + "px");
  raiz.setProperty("--px2", (parallax.x * 1.6).toFixed(2) + "px"); // fantasmas de perto mexem mais
  raiz.setProperty("--py2", (parallax.y * 1.6).toFixed(2) + "px");

  const parado = Math.abs(parallax.alvoX - parallax.x) < 0.05 && Math.abs(parallax.alvoY - parallax.y) < 0.05;
  if (parado) parallax.rodando = false;
  else requestAnimationFrame(moverParallax);
}

function ligarParallax() {
  window.addEventListener("pointermove", (e) => {
    if (!temMouse.matches || reduzirMovimento.matches) return;
    // -1 até 1 a partir do centro, vezes 12px, pro lado contrário do mouse
    parallax.alvoX = -((e.clientX / innerWidth) * 2 - 1) * 12;
    parallax.alvoY = -((e.clientY / innerHeight) * 2 - 1) * 12;
    if (!parallax.rodando) {
      parallax.rodando = true;
      requestAnimationFrame(moverParallax);
    }
  }, { passive: true });
}

// ---------- luz do mouse ----------
function ligarLuzDoMouse() {
  if (!temMouse.matches) return;

  const luz = document.createElement("div");
  luz.className = "cursor-luz";
  luz.setAttribute("aria-hidden", "true");
  document.body.appendChild(luz);

  window.addEventListener("pointermove", (e) => {
    luz.style.setProperty("--cx", e.clientX + "px");
    luz.style.setProperty("--cy", e.clientY + "px");
    luz.classList.add("ligada");
  }, { passive: true });

  document.documentElement.addEventListener("pointerleave", () => luz.classList.remove("ligada"));
}

// ---------- navbar vira vidro ao rolar ----------
function atualizarNavbar() {
  document.getElementById("navbar").classList.toggle("rolada", window.scrollY > 24);
}

function ligarNavbarRolagem() {
  window.addEventListener("scroll", atualizarNavbar, { passive: true });
  atualizarNavbar();
}

function iniciarEfeitos() {
  criarFantasmas();
  ligarParallax();
  ligarLuzDoMouse();
  ligarNavbarRolagem();
}
