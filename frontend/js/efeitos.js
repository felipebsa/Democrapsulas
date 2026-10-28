// efeitos visuais: lâmpadas fantasma, parallax do fundo, luz do mouse e navbar de vidro

const reduzirMovimento = window.matchMedia("(prefers-reduced-motion: reduce)");
const temMouse = window.matchMedia("(hover: hover) and (pointer: fine)");

// lanternas que dá pra escolher; o número (1 a 17) é o que o back guarda em "lantern"
// luz: cor do brilho em volta, que o CSS usa nos drop-shadow
const LANTERNAS = [
  { arquivo: "01-jade", luz: "#3FD0C0" },
  { arquivo: "02-snow-sakura", luz: "#FFB3C8" },
  { arquivo: "03-purple-moon", luz: "#D06594" },
  { arquivo: "04-autumn-moss", luz: "#F08917" },
  { arquivo: "05-red-oni", luz: "#F3461D" },
  { arquivo: "06-sky-clouds", luz: "#9CC8FF" },
  { arquivo: "07-neon", luz: "#3BAEEA" },
  { arquivo: "08-desert-fabric", luz: "#F17B24" },
  { arquivo: "09-ice-crystal", luz: "#17A4EC" },
  { arquivo: "10-black-orange", luz: "#F39D1B" },
  { arquivo: "11-red-spiral", luz: "#E32F2D" },
  { arquivo: "12-mossy-wood", luz: "#DEC560" },
  { arquivo: "13-ice-blue", luz: "#65AEE4" },
  { arquivo: "14-pink-sakura", luz: "#E34D66" },
  { arquivo: "15-dark-red", luz: "#F11C1D" },
  { arquivo: "16-green-coins", luz: "#ED9740" },
  { arquivo: "17-purple-pink", luz: "#D956BC" },
];

// põe a imagem e a luz de uma lanterna numa <img>
function mostrarLanterna(img, numero) {
  const lanterna = LANTERNAS[numero - 1];
  img.src = "img/lanterns/" + lanterna.arquivo + ".png";
  img.classList.add("lanterna");
  img.style.setProperty("--luz", lanterna.luz);
}

function lanternaAleatoria() {
  return 1 + Math.floor(Math.random() * LANTERNAS.length);
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
      mostrarLanterna(img, lanternaAleatoria());
      img.alt = "";
      el.appendChild(img);
      caixa.appendChild(el);
    }
  });
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
  // lanternas fixas do HTML dizem qual são pelo data-lanterna
  document.querySelectorAll("img[data-lanterna]").forEach((img) => mostrarLanterna(img, Number(img.dataset.lanterna)));
  criarFantasmas();
  ligarParallax();
  ligarLuzDoMouse();
  ligarNavbarRolagem();
}
