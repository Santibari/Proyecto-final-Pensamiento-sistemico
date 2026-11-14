// Simulación Discord – todo lo que se muestra sale del modelo de Vensim (vía PySD) o de su archivo .mdl.
"use strict";

const PASO = 0.25, ULTIMO = 416;
const $ = (id) => document.getElementById(id);
const num = (v, d = 0) => Number(v ?? 0).toLocaleString("es-CO", { maximumFractionDigits: d, minimumFractionDigits: d });
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

// Datos reales usados en la calibración (para mostrar al lado de lo que da el modelo)
const DATOS = {
  precision: { valor: 55.1, fuente: "DSA 2025, p. 9" },
  apelan: { valor: 15.5, fuente: "informes generales 2022–2023 (mediana)" },
  reversion: { valor: 2.39, fuente: "informes generales Q1 2022 – H1 2024 (mediana)" },
  revision: { valor: 57.34, fuente: "DSA 2024 (mediana de resolución)" },
  recall: { valor: 97.3, fuente: "DSA 2025, p. 9" },
};

const ESCENARIOS = {
  hoy: {
    params: {},
    texto: "<b>Escenario 1.</b> Los parámetros de los informes de Discord, sin cambios. Para reproducirlo en Vensim, simule los dos .mdl tal como están.",
  },
  endurece: {
    params: { "Sensibilidad del filtro IA": 0.99 },
    texto: "<b>Escenario 2 – arquetipo «desplazamiento de la carga».</b> Discord sube la sensibilidad de su IA a 0,99 desde la semana 0 (la solución rápida). " +
      "Observe qué pasa con los bloqueos por error, las apelaciones, la carga y los moderadores (la solución de fondo). En Vensim: <i>Sensibilidad del filtro IA = 0.99</i>.",
  },
  personal: {
    params: null,
    texto: "<b>Escenario 3.</b> Los controles se aplican por igual a los dos modelos. Al soltar un control se vuelve a simular desde la semana 0.",
  },
};

const S = {
  tiempo: [], datos: null, info: {}, controles: [], escenario: "hoy", params: {}, idx: 0, corriendo: false,
  acumulado: 0, vista: "diagrama", modelo: "actual", hover: null, ultimo: performance.now(), fase: 0, maximos: {},
};
const v = (n, m = S.modelo, i = S.idx) => S.datos?.[m]?.[n]?.[i] ?? 0;

// ------------------------------------------------------------------ datos
async function cargarModelos() {
  const [a, m, c] = await Promise.all([fetch("/modelo/actual"), fetch("/modelo/mejora"), fetch("/controles")]);
  S.info.actual = await a.json(); S.info.mejora = await m.json(); S.controles = await c.json();
  const va = S.info.actual.variables, vm = S.info.mejora.variables;
  const extra = Object.keys(vm).filter((n) => !(n in va));
  $("conexionTexto").innerHTML = `
    <ol>
      <li><b>Ecuaciones:</b> PySD traduce <code>${S.info.actual.archivo}</code> (${Object.keys(va).length} variables) y
        <code>${S.info.mejora.archivo}</code> (${Object.keys(vm).length} variables) y los ejecuta sin cambiar nada.</li>
      <li><b>Diagrama:</b> se dibuja con las posiciones guardadas en el .mdl; si mueven algo en Vensim, aquí también se mueve.</li>
      <li><b>Ayudas:</b> la unidad y el comentario de cada variable son los de Vensim.</li>
      <li><b>Cambios:</b> si editan un valor o una ecuación en Vensim y guardan, pulse «Volver a leer los .mdl».</li>
      <li><b>Cuidado:</b> si renombran una variable, la página no la encontrará.</li>
    </ol>
    <p>La mejora agrega: ${extra.join(", ") || "—"}; y cambia <i>Productividad por moderador</i>
      (${va["Productividad por moderador"]?.ecuacion} → ${vm["Productividad por moderador"]?.ecuacion}).</p>`;
  construirControles();
}

async function simular() {
  $("explicaEscenario").innerHTML = ESCENARIOS[S.escenario].texto + " <i>Simulando…</i>";
  const r = await fetch("/comparar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ parametros: S.params }) });
  if (!r.ok) { $("explicaEscenario").textContent = "Error: " + (await r.text()); return; }
  const d = await r.json();
  S.tiempo = d.tiempo; S.datos = { actual: d.actual, mejora: d.mejora };
  S.maximos = {};
  for (const n of Object.keys(d.actual)) {
    S.maximos[n] = Math.max(...d.actual[n].map(Math.abs), ...(d.mejora[n] || [0]).map(Math.abs), 1e-9);
  }
  $("explicaEscenario").innerHTML = ESCENARIOS[S.escenario].texto;
  pintarTodo();
}

function construirControles() {
  const cont = $("controles"); cont.innerHTML = "";
  for (const c of S.controles) {
    const dec = c.paso < 1e-5 ? 7 : c.paso < 0.01 ? 3 : 2;
    const div = document.createElement("div"); div.className = "control";
    div.innerHTML = `<label>${c.nombre} <output>${c.valor.toFixed(dec)}</output>
      <input type="range" min="${c.min}" max="${c.max}" step="${c.paso}" value="${c.valor}"></label>
      <small>${c.comentario}</small>`;
    const inp = div.querySelector("input"), out = div.querySelector("output");
    inp.addEventListener("input", () => (out.textContent = Number(inp.value).toFixed(dec)));
    inp.addEventListener("change", () => { S.params[c.nombre] = Number(inp.value); simular(); });
    cont.appendChild(div);
  }
}

// ------------------------------------------------------------------ escenarios y reproductor
function elegirEscenario(e) {
  S.escenario = e;
  document.querySelectorAll(".escenario").forEach((b) => b.classList.toggle("activo", b.dataset.esc === e));
  $("panelControles").classList.toggle("oculto", e !== "personal");
  if (e === "personal") {
    S.params = Object.fromEntries([...document.querySelectorAll("#controles input")].map((inp, k) => [S.controles[k].nombre, Number(inp.value)]));
  } else S.params = { ...ESCENARIOS[e].params };
  simular();
}
function irA(i) { S.idx = Math.max(0, Math.min(ULTIMO, Math.round(i))); pintarTodo(); }
function play(on) {
  S.corriendo = on ?? !S.corriendo;
  if (S.corriendo && S.idx >= ULTIMO) S.idx = 0;
  $("btnPlay").textContent = S.corriendo ? "❚❚ Pausa" : "▶ Reproducir";
}

// ------------------------------------------------------------------ textos
function etiquetaTipo(com) {
  if (/DATO/.test(com)) return '<span class="etiqueta dato">DATO</span>';
  if (/CALIBRADO/.test(com)) return '<span class="etiqueta calibrado">CALIBRADO</span>';
  if (/SUPUESTO/.test(com)) return '<span class="etiqueta supuesto">SUPUESTO</span>';
  return "";
}
function unidadLegible(u) {
  return (u || "").replace("Dmnl", "sin unidad").replace(/\/Week/g, " por semana").replace("Week", "semanas")
    .replace("piezas/(usuarios*Week)", "piezas por usuario por semana").replace("piezas/(moderadores*Week)", "piezas por moderador por semana")
    .replace("moderadores/(usuarios*Week)", "moderadores por usuario por semana").replace("1/Week", "por semana");
}
function nivelConfianza(c) { return c >= 0.75 ? "alta" : c >= 0.5 ? "media" : c >= 0.25 ? "baja" : "muy baja"; }

function pintarPalabras() {
  const m = S.modelo, nombreM = m === "actual" ? "modelo actual" : "modelo con mejora";
  $("palabrasModelo").textContent = `· ${nombreM}`;
  const U = v("Usuarios activos"), mensajes = U * (v("Contenido nocivo por usuario") + v("Mensajes sanos por usuario"));
  const vp = v("Nocivo bloqueado"), fp = v("Bloqueos por error"), fn = v("Nocivo que se escapa");
  const injustos = vp + fp > 0 ? (100 * fp) / (vp + fp) : 0;
  const apRes = v("Apelaciones resueltas"), acept = v("Apelaciones aceptadas");
  const pend = v("Apelaciones pendientes") + v("Denuncias pendientes");
  const resueltas = apRes + v("Denuncias resueltas");
  const esperaH = resueltas > 0 ? (pend / resueltas) * 168 : 0;
  const carga = v("Carga percibida") * 100, conf = v("Confianza de la comunidad");
  const sens = m === "mejora" ? v("Sensibilidad efectiva del filtro") : v("Sensibilidad del filtro IA");
  const f = [
    `La comunidad tiene <span class="grande">${num(U)}</span> usuarios, que publican unos ${num(mensajes)} mensajes por semana.`,
    `El filtro de IA (sensibilidad ${num(sens, 3)}) bloqueó <b>${num(vp + fp)}</b> mensajes: ${num(vp)} eran nocivos y <b>${num(fp)}</b> eran legítimos.
      → De cada 100 bloqueos, <span class="grande">${num(injustos)}</span> fueron injustos.
      <span class="etiqueta dato">DATO real: ${num(100 - DATOS.precision.valor)} de cada 100 · ${DATOS.precision.fuente}</span>`,
    `Se escaparon <b>${num(fn, 1)}</b> mensajes nocivos que el filtro no detectó; los usuarios denuncian la mitad <span class="etiqueta supuesto">SUPUESTO</span>.`,
    `Se resolvieron ${num(apRes)} apelaciones y se aceptaron ${num(acept, 1)} → de cada 100 apelaciones, <b>${num(apRes > 0 ? (100 * acept) / apRes : 0, 1)}</b> se aceptan.
      <span class="etiqueta dato">DATO real: ${num(DATOS.reversion.valor, 2)} · ${DATOS.reversion.fuente}</span>`,
    `Hay <span class="grande">${num(v("Moderadores activos"), 1)}</span> moderadores. El trabajo que llega equivale al
      <b class="${carga > 100 ? "alerta" : ""}">${num(carga)} %</b> de su capacidad${carga > 100 ? " (están sobrecargados)" : ""}.`,
    `Trabajo pendiente: <b>${num(pend)}</b> casos; espera aproximada <b class="${esperaH > 168 ? "alerta" : ""}">${num(esperaH)} horas</b>.
      <span class="etiqueta dato">DATO real: ${num(DATOS.revision.valor, 0)} h · ${DATOS.revision.fuente}</span>`,
    `Confianza de la comunidad: <span class="grande">${num(conf, 2)}</span> de 1 (${nivelConfianza(conf)}) <span class="etiqueta supuesto">índice SUPUESTO</span>.`,
  ];
  $("frases").innerHTML = f.map((t) => `<li>${t}</li>`).join("");
  const fila = (t, fn, d = 0, suf = "") => `<tr><td>${t}</td><td>${num(fn("actual"), d)}${suf}</td><td>${num(fn("mejora"), d)}${suf}</td></tr>`;
  $("tablaComp").innerHTML =
    fila("Usuarios activos", (mm) => v("Usuarios activos", mm)) +
    fila("Confianza (0–1)", (mm) => v("Confianza de la comunidad", mm), 2) +
    fila("Moderadores activos", (mm) => v("Moderadores activos", mm), 1) +
    fila("Carga de trabajo", (mm) => 100 * v("Carga percibida", mm), 0, " %") +
    fila("Trabajo pendiente", (mm) => v("Apelaciones pendientes", mm) + v("Denuncias pendientes", mm)) +
    fila("Bloqueos injustos de cada 100", (mm) => { const a = v("Nocivo bloqueado", mm), b = v("Bloqueos por error", mm); return a + b ? (100 * b) / (a + b) : 0; }) +
    fila("Nocivo que se escapa / semana", (mm) => v("Nocivo que se escapa", mm), 1);
}

function pintarQueVeo() {
  const t = S.vista === "diagrama" ? `
    <ul>
      <li>Es el <b>mismo diagrama de Vensim</b>, animado con los resultados de la semana elegida.</li>
      <li><b>Cajas = niveles</b> (acumulaciones). El relleno muestra cuánto tienen comparado con su máximo en la simulación.</li>
      <li><b>Tuberías con puntos = flujos</b>: los puntos se mueven más rápido cuando el flujo es mayor. La «válvula» ⧗ regula cada flujo y su valor aparece debajo.</li>
      <li><b>Flechas curvas = relaciones causales</b> con su signo: <b>+</b> se mueven en la misma dirección, <b>−</b> en dirección contraria.</li>
      <li>Las nubes son el exterior del sistema (de dónde vienen o adónde van las cosas).</li>
    </ul>` : `
    <ul>
      <li><b>Ilustración</b> de la misma comunidad del modelo, repartida en 30 edificios iguales.
        <b>Los datos no son por servidor ni por país</b>: los informes de Discord solo dan totales globales y de la UE.</li>
      <li>Altura de los edificios = <i>Usuarios activos</i>. Color = <i>Confianza de la comunidad</i> (verde alta → rojo baja); las ventanas encendidas también indican confianza.</li>
      <li>La <b>torre de moderación</b> tiene un piso por moderador activo y se vuelve roja cuando la carga pasa del 100 %.</li>
      <li>La <b>bodega de casos</b> apila cajas según el trabajo pendiente (escala logarítmica; el número exacto aparece encima).</li>
    </ul>`;
  $("queVeoTexto").innerHTML = t;
  $("opcionesDiagrama").style.visibility = S.vista === "diagrama" ? "visible" : "hidden";
}

// ------------------------------------------------------------------ lienzo común
const lienzo = $("lienzo"), ctx = lienzo.getContext("2d");
function ajustarLienzo() {
  const r = lienzo.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
  lienzo.width = Math.round(r.width * dpr); lienzo.height = Math.round(r.height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { W: r.width, H: r.height };
}
function txt(t, x, y, { color = css("--tinta"), tam = 12, peso = 400, al = "center", base = "middle" } = {}) {
  ctx.fillStyle = color; ctx.font = `${peso} ${tam}px system-ui, sans-serif`; ctx.textAlign = al; ctx.textBaseline = base; ctx.fillText(t, x, y);
}
function mezcla(c1, c2, t) {
  const a = c1.match(/\w\w/g).map((h) => parseInt(h, 16)), b = c2.match(/\w\w/g).map((h) => parseInt(h, 16));
  return `rgb(${a.map((x, k) => Math.round(x + (b[k] - x) * Math.max(0, Math.min(1, t)))).join(",")})`;
}
const colorConfianza = (c) => (c >= 0.5 ? mezcla("eda100", "1baf7a", (c - 0.5) / 0.3) : mezcla("e34948", "eda100", c / 0.5));

// ------------------------------------------------------------------ vista 1: diagrama de Vensim en vivo
let zonas = [];
function dibujarDiagrama(W, H) {
  const info = S.info[S.modelo]; if (!info || !S.datos) return;
  const vars = info.variables, el = info.diagrama.elementos, con = info.diagrama.conexiones;
  const porId = Object.fromEntries(el.map((e) => [e.id, e]));
  const verConst = $("chkConstantes").checked, verFlechas = $("chkFlechas").checked;
  const visible = (e) => e.clase !== "variable" || verConst || vars[e.nombre]?.tipo !== "constante";
  const vis = el.filter(visible);
  const xs = vis.flatMap((e) => [e.x - (e.w || 10), e.x + (e.w || 10)]), ys = vis.flatMap((e) => [e.y - (e.h || 10), e.y + (e.h || 10)]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const esc = Math.min((W - 30) / (x1 - x0), (H - 30) / (y1 - y0));
  const ox = (W - (x1 - x0) * esc) / 2 - x0 * esc, oy = (H - (y1 - y0) * esc) / 2 - y0 * esc;
  const P = (x, y) => [ox + x * esc, oy + y * esc];
  const tam = Math.max(10, Math.min(13, 12 * esc + 3));
  zonas = [];
  ctx.clearRect(0, 0, W, H);
  // flechas causales (curvas, con signo)
  if (verFlechas) {
    for (const c of con) {
      if (c.tuberia) continue;
      const a = porId[c.de], b = porId[c.a];
      if (!a || !b || !visible(a) || !visible(b) || a.clase !== "variable" || b.clase !== "variable") continue;
      const [ax, ay] = P(a.x, a.y), [bx, by] = P(b.x, b.y);
      const [cx, cy] = c.control ? P(...c.control) : [(ax + bx) / 2, (ay + by) / 2];
      const qx = 2 * cx - (ax + bx) / 2, qy = 2 * cy - (ay + by) / 2;  // la curva pasa por el punto de control de Vensim
      const resaltada = S.hover && (S.hover === a.nombre || S.hover === b.nombre);
      ctx.strokeStyle = resaltada ? css("--acento") : "rgba(120,130,145,.35)"; ctx.lineWidth = resaltada ? 1.8 : 1;
      ctx.beginPath(); ctx.moveTo(ax, ay); ctx.quadraticCurveTo(qx, qy, bx, by); ctx.stroke();
      const t = 0.82, px = (1 - t) ** 2 * ax + 2 * (1 - t) * t * qx + t * t * bx, py = (1 - t) ** 2 * ay + 2 * (1 - t) * t * qy + t * t * by;
      const dx = 2 * (1 - t) * (qx - ax) + 2 * t * (bx - qx), dy = 2 * (1 - t) * (qy - ay) + 2 * t * (by - qy), L = Math.hypot(dx, dy) || 1;
      ctx.fillStyle = ctx.strokeStyle; ctx.beginPath();
      ctx.moveTo(px + dx / L * 6, py + dy / L * 6); ctx.lineTo(px - dy / L * 3.5, py + dx / L * 3.5); ctx.lineTo(px + dy / L * 3.5, py - dx / L * 3.5); ctx.fill();
      if (c.signo) txt(c.signo === "+" ? "+" : "−", px - dy / L * 9, py + dx / L * 9, { color: c.signo === "+" ? css("--verde") : css("--rojo"), tam: 13, peso: 700 });
    }
  }
  // tuberías con partículas
  for (const c of con) {
    if (!c.tuberia) continue;
    const valv = porId[c.de], otro = porId[c.a]; if (!valv || !otro) continue;
    const flujo = el.find((e) => e.forma === 40 && Number(e.id) === Number(valv.id) + 1) || el.find((e) => e.forma === 40 && Math.abs(e.x - valv.x) < 5);
    const val = flujo ? v(flujo.nombre) : 0, rel = flujo ? Math.abs(val) / (S.maximos[flujo.nombre] || 1) : 0;
    const [vx, vy] = P(valv.x, valv.y); let [ex, ey] = P(otro.x, otro.y);
    if (otro.clase === "variable") { ex -= Math.sign(ex - vx) * (otro.w || 40) * esc; }
    ctx.strokeStyle = css("--tinta3"); ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(vx, vy); ctx.lineTo(ex, ey); ctx.stroke();
    ctx.strokeStyle = css("--lienzo"); ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(vx, vy); ctx.lineTo(ex, ey); ctx.stroke();
    const desdeValvula = c.sentido === 4;  // 4: la tubería sale de la válvula hacia el destino
    const L = Math.hypot(ex - vx, ey - vy), sep = 16;
    if (rel > 0.002) {
      ctx.fillStyle = flujo.nombre.includes("se van") || flujo.nombre.includes("renuncian") ? css("--rojo") : css("--azul");
      for (let d = (S.fase * (20 + 90 * rel)) % sep; d < L; d += sep) {
        const t = desdeValvula ? d / L : 1 - d / L;
        ctx.beginPath(); ctx.arc(vx + (ex - vx) * t, vy + (ey - vy) * t, 2.2, 0, 7); ctx.fill();
      }
    }
    if (c.sentido === 4) {  // punta de flecha en el destino
      const ux = (ex - vx) / L, uy = (ey - vy) / L;
      ctx.fillStyle = css("--tinta3"); ctx.beginPath(); ctx.moveTo(ex, ey); ctx.lineTo(ex - ux * 10 - uy * 7, ey - uy * 10 + ux * 7); ctx.lineTo(ex - ux * 10 + uy * 7, ey - uy * 10 - ux * 7); ctx.fill();
    }
  }
  // elementos
  for (const e of el) {
    if (!visible(e)) continue;
    const [x, y] = P(e.x, e.y);
    if (e.clase === "nube") {
      ctx.fillStyle = css("--panel"); ctx.strokeStyle = css("--tinta3"); ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.arc(x - 5, y, 6, 0, 7); ctx.arc(x + 4, y - 3, 6, 0, 7); ctx.arc(x + 5, y + 3, 5, 0, 7); ctx.fill(); ctx.stroke();
    } else if (e.clase === "valvula") {
      ctx.fillStyle = css("--tinta2"); ctx.beginPath(); ctx.moveTo(x - 7, y - 8); ctx.lineTo(x + 7, y - 8); ctx.lineTo(x - 7, y + 8); ctx.lineTo(x + 7, y + 8); ctx.closePath(); ctx.fill();
    } else {
      const meta = vars[e.nombre] || {}, valor = v(e.nombre);
      if (meta.tipo === "nivel") {
        const w = Math.max(110, e.w * 2 * esc), h = Math.max(46, e.h * 2 * esc), lleno = Math.min(1, Math.abs(valor) / (S.maximos[e.nombre] || 1));
        ctx.fillStyle = css("--panel"); ctx.strokeStyle = S.hover === e.nombre ? css("--acento") : css("--tinta2"); ctx.lineWidth = 2;
        ctx.fillRect(x - w / 2, y - h / 2, w, h);
        ctx.fillStyle = e.nombre.startsWith("Confianza") ? colorConfianza(valor) : e.nombre.includes("pendientes") ? css("--naranja") : css("--azul");
        ctx.globalAlpha = 0.35; ctx.fillRect(x - w / 2, y + h / 2 - h * lleno, w, h * lleno); ctx.globalAlpha = 1;
        ctx.strokeRect(x - w / 2, y - h / 2, w, h);
        txt(e.nombre, x, y - 8, { tam, peso: 600 });
        txt(num(valor, Math.abs(valor) < 10 ? 2 : 0), x, y + 10, { tam: tam + 2, peso: 700 });
        zonas.push({ nombre: e.nombre, x0: x - w / 2, y0: y - h / 2, x1: x + w / 2, y1: y + h / 2 });
      } else {
        const esConst = meta.tipo === "constante", esFlujo = meta.tipo === "flujo";
        let tx = x, ty = y;
        if (esFlujo) {  // el nombre del flujo va justo debajo de su válvula, sin tapar la tubería
          const valv = porId[String(Number(e.id) - 1)];
          if (valv && valv.clase === "valvula") { const [vx, vy] = P(valv.x, valv.y); tx = vx; ty = vy + 24; }
        }
        const color = S.hover === e.nombre ? css("--acento") : esConst ? css("--tinta3") : css("--tinta");
        ctx.font = `${esFlujo ? 600 : 400} ${tam}px system-ui`; const ancho = ctx.measureText(e.nombre).width;
        const alto = esConst ? 16 : 30;
        ctx.fillStyle = css("--lienzo"); ctx.globalAlpha = 0.88;  // fondo para que las flechas no tapen el texto
        ctx.fillRect(tx - ancho / 2 - 3, ty - alto / 2 - (esConst ? 0 : 1), ancho + 6, alto); ctx.globalAlpha = 1;
        txt(e.nombre, tx, ty - (esConst ? 0 : 7), { tam: esConst ? tam - 1 : tam, peso: esFlujo ? 600 : 400, color });
        if (!esConst) txt(num(valor, Math.abs(valor) < 10 ? 3 : 0), tx, ty + 8, { tam: tam - 1, peso: 600, color: esFlujo ? css("--azul") : css("--tinta2") });
        zonas.push({ nombre: e.nombre, x0: tx - ancho / 2 - 4, y0: ty - 15, x1: tx + ancho / 2 + 4, y1: ty + 15 });
      }
    }
  }
}

// ------------------------------------------------------------------ vista 2: ciudad 3D (isométrica)
function dibujarCiudad(W, H) {
  ctx.clearRect(0, 0, W, H);
  zonas = [];
  const conf = v("Confianza de la comunidad"), U = v("Usuarios activos"), Umax = S.maximos["Usuarios activos"] || 1;
  const mods = v("Moderadores activos"), carga = v("Carga percibida"), pend = v("Apelaciones pendientes") + v("Denuncias pendientes");
  const k = Math.min(W / 900, H / 560);           // escala de la escena
  const T = 30 * k, D = 15 * k;                     // medio ancho y medio alto de una baldosa
  const hexColor = (c) => { const m = c.match(/\d+/g).map(Number); return m.map((n) => n.toString(16).padStart(2, "0")).join(""); };
  // dibuja un bloque isométrico con la base centrada en (x, y)
  const bloque = (x, y, alto, color, ventanas = 0, semilla = 0) => {
    const w = T * 0.78, d = D * 0.78;
    const cara = (pts, c) => { ctx.fillStyle = c; ctx.beginPath(); pts.forEach(([a, b], i) => (i ? ctx.lineTo(a, b) : ctx.moveTo(a, b))); ctx.closePath(); ctx.fill(); };
    cara([[x - w, y], [x, y + d], [x, y + d - alto], [x - w, y - alto]], mezcla(color, "000000", 0.22));
    cara([[x, y + d], [x + w, y], [x + w, y - alto], [x, y + d - alto]], mezcla(color, "000000", 0.40));
    cara([[x - w, y - alto], [x, y + d - alto], [x + w, y - alto], [x, y - d - alto]], mezcla(color, "ffffff", 0.18));
    if (ventanas >= 0 && alto > 14) {  // ventanas: fracción encendida = confianza (patrón fijo, no aleatorio)
      for (let f = 7 * k; f < alto - 5 * k; f += 9 * k) for (let c = 0; c < 3; c++) {
        const enc = ((semilla * 7 + Math.round(f) * 3 + c * 5) % 10) / 10 < ventanas;
        ctx.fillStyle = enc ? "rgba(255,236,160,.95)" : "rgba(20,24,30,.5)";
        ctx.fillRect(x - w + (3 + c * 6) * k, y - f + (c * 3 + 1) * k, 3.5 * k, 3.5 * k);
      }
    }
  };
  // --- ciudad (6 × 5 edificios iguales)
  const cx = W * 0.36, cy = H * 0.30;
  const iso = (gx, gy) => [cx + (gx - gy) * T, cy + (gx + gy) * D];
  for (let gx = -1; gx <= 6; gx++) for (let gy = -1; gy <= 5; gy++) {
    const [x, y] = iso(gx, gy); ctx.fillStyle = (gx + gy) % 2 ? "rgba(120,130,145,.10)" : "rgba(120,130,145,.17)";
    ctx.beginPath(); ctx.moveTo(x, y - D); ctx.lineTo(x + T, y); ctx.lineTo(x, y + D); ctx.lineTo(x - T, y); ctx.closePath(); ctx.fill();
  }
  const altura = (16 + 150 * (U / Umax)) * k, colorC = hexColor(colorConfianza(conf));
  for (let gx = 0; gx < 6; gx++) for (let gy = 0; gy < 5; gy++) { const [x, y] = iso(gx, gy); bloque(x, y, altura, colorC, conf, gx * 5 + gy); }
  const [ax, ay] = iso(0, 5), [bx2, by2] = iso(6, 0);
  zonas.push({ nombre: "Usuarios activos", x0: ax - T, y0: cy - D - altura, x1: bx2 + T, y1: iso(6, 5)[1] + D });
  txt(`Comunidad: ${num(U)} usuarios`, cx, iso(6, 5)[1] + D + 22 * k, { tam: 15, peso: 700 });
  txt(`Confianza ${num(conf, 2)} (${nivelConfianza(conf)})`, cx, iso(6, 5)[1] + D + 42 * k, { tam: 13, color: css("--tinta2") });

  // --- torre de moderación: un piso por moderador activo
  const tx = W * 0.72, tyBase = H * 0.62, piso = 20 * k;
  const pisos = Math.ceil(mods - 1e-6), colorT = carga > 1 ? "e34948" : hexColor(mezcla("2a78d6", "6250d6", carga));
  ctx.fillStyle = "rgba(120,130,145,.17)"; ctx.beginPath(); ctx.moveTo(tx, tyBase - D); ctx.lineTo(tx + T, tyBase); ctx.lineTo(tx, tyBase + D); ctx.lineTo(tx - T, tyBase); ctx.closePath(); ctx.fill();
  for (let p = 0; p < pisos; p++) {
    ctx.globalAlpha = p === pisos - 1 ? Math.max(0.3, mods - p) : 1;
    bloque(tx, tyBase - p * piso, piso - 2 * k, colorT, -1);
    ctx.globalAlpha = 1;
  }
  txt("Torre de moderación", tx, tyBase + D + 18 * k, { tam: 13, peso: 700 });
  txt(`${num(mods, 1)} moderadores · carga ${num(carga * 100)} %`, tx, tyBase + D + 36 * k, { tam: 12, color: carga > 1 ? css("--rojo") : css("--tinta2"), peso: carga > 1 ? 700 : 400 });
  zonas.push({ nombre: "Moderadores activos", x0: tx - T, y0: tyBase - pisos * piso - D, x1: tx + T, y1: tyBase + D + 40 * k });

  // --- bodega de casos pendientes (cajas en escala logarítmica)
  const bx = W * 0.90, by = H * 0.62, lado = 12 * k;
  const cajas = Math.round(Math.log10(1 + pend) * 5);
  for (let c = 0; c < cajas; c++) {
    const col = c % 3, fila = Math.floor(c / 3);
    ctx.fillStyle = css("--naranja"); ctx.strokeStyle = "rgba(0,0,0,.35)"; ctx.lineWidth = 1;
    ctx.fillRect(bx + (col - 1.5) * (lado + 2), by - (fila + 1) * (lado + 2), lado, lado);
    ctx.strokeRect(bx + (col - 1.5) * (lado + 2), by - (fila + 1) * (lado + 2), lado, lado);
  }
  txt("Casos pendientes", bx, by + 18 * k, { tam: 13, peso: 700 });
  txt(`${num(pend)} (apelaciones + denuncias)`, bx, by + 36 * k, { tam: 12, color: css("--tinta2") });
  zonas.push({ nombre: "Apelaciones pendientes", x0: bx - 40 * k, y0: by - (Math.ceil(cajas / 3) + 1) * (lado + 2), x1: bx + 40 * k, y1: by + 40 * k });

  txt("Ilustración de la misma comunidad del modelo: los 30 edificios son iguales. Los informes no tienen datos por servidor ni por país.",
    W / 2, H - 16, { tam: 12, color: css("--tinta2") });
}

// ------------------------------------------------------------------ gráficos comparativos
const GRAFICOS = [
  { serie: "Usuarios activos", titulo: "Usuarios activos", unidad: "usuarios" },
  { serie: "Confianza de la comunidad", titulo: "Confianza de la comunidad", unidad: "índice 0–1", min: 0, max: 1 },
  { serie: "Moderadores activos", titulo: "Moderadores activos", unidad: "moderadores", min: 0 },
  { serie: ["Apelaciones pendientes", "Denuncias pendientes"], titulo: "Trabajo pendiente", unidad: "casos" },
  { serie: "Bloqueos por error", titulo: "Bloqueos por error (falsos positivos)", unidad: "mensajes por semana", min: 0 },
  { serie: "Nocivo que se escapa", titulo: "Nocivo que se escapa (falsos negativos)", unidad: "mensajes por semana", min: 0 },
];
function crearGraficos() {
  $("rejilla").innerHTML = GRAFICOS.map((g, k) => `<div class="grafico" data-k="${k}"><h3>${g.titulo} <small>(${g.unidad})</small></h3><canvas></canvas></div>`).join("");
  document.querySelectorAll(".grafico").forEach((div) => {
    const c = div.querySelector("canvas");
    const ir = (ev) => { const r = c.getBoundingClientRect(); irA(((ev.clientX - r.left - 46) / (r.width - 54)) * ULTIMO); };
    c.addEventListener("click", ir);
    c.addEventListener("mousemove", (ev) => { if (ev.buttons) ir(ev); });
  });
}
function serie(g, m) {
  const s = Array.isArray(g.serie) ? g.serie : [g.serie];
  return S.datos[m][s[0]].map((_, i) => s.reduce((a, n) => a + S.datos[m][n][i], 0));
}
function pintarGraficos() {
  if (!S.datos) return;
  document.querySelectorAll(".grafico").forEach((div) => {
    const g = GRAFICOS[div.dataset.k], c = div.querySelector("canvas"), x = c.getContext("2d");
    const r = c.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
    c.width = r.width * dpr; c.height = r.height * dpr; x.setTransform(dpr, 0, 0, dpr, 0, 0);
    const W = r.width, H = r.height, m = { l: 46, r: 8, t: 8, b: 20 }, iw = W - m.l - m.r, ih = H - m.t - m.b;
    const a = serie(g, "actual"), b = serie(g, "mejora");
    let min = g.min ?? Math.min(...a, ...b), max = g.max ?? Math.max(...a, ...b);
    if (g.min === undefined) min = Math.min(0, min);
    if (max - min < 1e-9) max = min + 1;
    if (g.max === undefined) max *= 1.05;
    const X = (i) => m.l + (iw * i) / ULTIMO, Y = (val) => m.t + ih * (1 - (val - min) / (max - min));
    x.font = "11px system-ui"; x.fillStyle = css("--tinta2"); x.strokeStyle = css("--borde"); x.lineWidth = 1;
    for (let k = 0; k <= 2; k++) {
      const val = min + ((max - min) * k) / 2, y = Y(val);
      x.beginPath(); x.moveTo(m.l, y); x.lineTo(W - m.r, y); x.stroke();
      x.textAlign = "right"; x.textBaseline = "middle"; x.fillText(num(val, max < 10 ? 2 : 0), m.l - 5, y);
    }
    x.textAlign = "center"; x.textBaseline = "alphabetic";
    for (const s of [0, 26, 52, 78, 104]) x.fillText(s, X(s / PASO), H - 5);
    for (const [d, color] of [[a, css("--azul")], [b, css("--naranja")]]) {
      x.strokeStyle = color; x.lineWidth = 2;
      x.globalAlpha = 0.28; x.beginPath(); d.forEach((val, i) => (i ? x.lineTo(X(i), Y(val)) : x.moveTo(X(i), Y(val)))); x.stroke();
      x.globalAlpha = 1; x.beginPath(); for (let i = 0; i <= S.idx; i++) (i ? x.lineTo(X(i), Y(d[i])) : x.moveTo(X(i), Y(d[i]))); x.stroke();
      x.fillStyle = color; x.beginPath(); x.arc(X(S.idx), Y(d[S.idx]), 3.5, 0, 7); x.fill();
    }
    x.strokeStyle = css("--tinta3"); x.setLineDash([3, 3]); x.beginPath(); x.moveTo(X(S.idx), m.t); x.lineTo(X(S.idx), m.t + ih); x.stroke(); x.setLineDash([]);
  });
}

// ------------------------------------------------------------------ pintar todo
function pintarTodo() {
  $("linea").value = S.idx;
  $("lblSemana").textContent = num(S.idx * PASO, S.idx % 4 ? 2 : 0);
  $("lblSemana2").textContent = num(S.idx * PASO, S.idx % 4 ? 2 : 0);
  if (!S.datos) return;
  pintarPalabras(); pintarGraficos(); pintarQueVeo();
}
function cuadro(ahora) {
  const dt = Math.min(0.1, (ahora - S.ultimo) / 1000); S.ultimo = ahora; S.fase += dt;
  if (S.corriendo && S.datos) {
    S.acumulado += (dt * Number($("velocidad").value)) / PASO;
    const n = Math.floor(S.acumulado);
    if (n > 0) { S.acumulado -= n; S.idx = Math.min(ULTIMO, S.idx + n); pintarTodo(); if (S.idx >= ULTIMO) play(false); }
  }
  const { W, H } = ajustarLienzo();
  if (S.vista === "diagrama") dibujarDiagrama(W, H); else dibujarCiudad(W, H);
  requestAnimationFrame(cuadro);
}

// ------------------------------------------------------------------ tooltip
lienzo.addEventListener("mousemove", (ev) => {
  const r = lienzo.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top;
  const z = zonas.find((q) => x >= q.x0 && x <= q.x1 && y >= q.y0 && y <= q.y1);
  const tip = $("tooltip");
  S.hover = z?.nombre || null;
  if (!z) { tip.hidden = true; return; }
  const meta = S.info[S.modelo].variables[z.nombre] || {};
  const tipos = { nivel: "Nivel (acumulación)", flujo: "Flujo", auxiliar: "Variable auxiliar", constante: "Constante" };
  const valor = v(z.nombre);
  tip.innerHTML = `<b>${z.nombre}</b> ${etiquetaTipo(meta.comentario || "")}<br><small>${tipos[meta.tipo] || ""}</small>
    <div class="valor">${num(valor, Math.abs(valor) < 10 ? 3 : 0)} <small>${unidadLegible(meta.unidad)}</small></div>
    ${meta.comentario || ""}<code>${z.nombre} = ${meta.ecuacion || ""}</code>`;
  tip.hidden = false;
  tip.style.left = Math.min(x + 14, r.width - 350) + "px"; tip.style.top = Math.min(y + 14, r.height - 160) + "px";
});
lienzo.addEventListener("mouseleave", () => { $("tooltip").hidden = true; S.hover = null; });

// ------------------------------------------------------------------ eventos
document.querySelectorAll(".escenario").forEach((b) => b.addEventListener("click", () => elegirEscenario(b.dataset.esc)));
document.querySelectorAll("[data-vista]").forEach((b) => b.addEventListener("click", () => {
  S.vista = b.dataset.vista; document.querySelectorAll("[data-vista]").forEach((x) => x.classList.toggle("activo", x === b)); pintarQueVeo();
}));
document.querySelectorAll("[data-modelo]").forEach((b) => b.addEventListener("click", () => {
  S.modelo = b.dataset.modelo; document.querySelectorAll("[data-modelo]").forEach((x) => x.classList.toggle("activo", x === b)); pintarTodo();
}));
$("btnPlay").addEventListener("click", () => play());
$("btnReiniciar").addEventListener("click", () => { play(false); irA(0); });
$("btnSemana").addEventListener("click", () => irA(S.idx + 1 / PASO));
$("linea").addEventListener("input", (e) => irA(Number(e.target.value)));
$("btnRecargar").addEventListener("click", async () => { await cargarModelos(); await simular(); });
window.addEventListener("resize", pintarGraficos);

(async () => {
  crearGraficos();
  await cargarModelos();
  await simular();
  requestAnimationFrame(cuadro);
})();
