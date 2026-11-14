"""07_verificacion_modelos.py – Lee los .mdl de "Modelos Vensim/" y los simula con un intérprete propio.

Sirve para verificar, fuera de Vensim, que:
  1. todas las ecuaciones se pueden evaluar (sin variables sin definir ni ciclos algebraicos);
  2. los indicadores de calibración en t = 0 coinciden con los DATOS;
  3. ambos modelos corren 104 semanas sin valores imposibles (negativos, NaN).
Método de integración: Euler, igual que Vensim por defecto. El ruido (RANDOM NORMAL) usa el generador
de Python, así que no reproduce exactamente la secuencia de Vensim.
Salida: processed/simulacion_<modelo>.csv y figuras/sim_*.png (gráficos de niveles y flujos).
"""
import math
import random
import re
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parents[2]
MODELOS = BASE / "Modelos Vensim"
PROC, FIG = BASE / "datos" / "processed", BASE / "datos" / "figuras"


# ------------------------------------------------------------------------------ lectura del .mdl
def leer_mdl(ruta):
    texto = ruta.read_text(encoding="utf-8").split("\\\\\\---///")[0]
    texto = texto.replace("{UTF-8}", "")
    eqs = {}
    for bloque in texto.split("|"):
        if "=" not in bloque or ".Control" in bloque:
            bloque = bloque.split("~~")[-1]
        partes = bloque.split("~")
        if len(partes) < 2 or "=" not in partes[0]:
            continue
        izq, der = partes[0].split("=", 1)
        nombre = " ".join(izq.split())
        if not nombre or nombre.startswith("*"):
            continue
        eqs[nombre] = (" ".join(der.split()), " ".join(partes[1].split()))
    return eqs


def argumentos(s, i):
    """Desde s[i] == '(' devuelve (lista de argumentos de nivel superior, índice de cierre)."""
    nivel, ini, args = 0, i + 1, []
    for j in range(i, len(s)):
        c = s[j]
        if c in "([":
            nivel += 1
        elif c in ")]":
            nivel -= 1
            if nivel == 0:
                args.append(s[ini:j])
                return args, j
        elif c == "," and nivel == 1:
            args.append(s[ini:j])
            ini = j + 1
    raise ValueError(s)


class Modelo:
    def __init__(self, eqs, cambios=None, semilla=1234):
        self.eqs = dict(eqs)
        for k, v in (cambios or {}).items():
            self.eqs[k] = (str(v), self.eqs[k][1])
        self.t, self.dt = 0.0, float(self.eqs["TIME STEP"][0])
        self.final = float(self.eqs["FINAL TIME"][0])
        self.estados, self.niveles, self.cache = [], {}, {}
        self.rng = random.Random(semilla)
        self.code = {}
        nombres = sorted([n for n in self.eqs if n not in ("FINAL TIME", "INITIAL TIME", "SAVEPER", "TIME STEP")], key=len, reverse=True)
        self.nombres = nombres
        for n in nombres:
            self.code[n] = self.compilar(n, self.eqs[n][0])

    # traduce una ecuación de Vensim a Python
    def compilar(self, nombre, e):
        if e.startswith("INTEG"):
            args, _ = argumentos(e, e.index("("))
            self.niveles[nombre] = {"flujo": self.traducir(args[0]), "ini": self.traducir(args[1]), "valor": None}
            return None
        return self.traducir(e)

    def traducir(self, e):
        fichas = {}
        for k, n in enumerate(self.nombres):
            patron = r"(?<![A-Za-z0-9_])" + re.escape(n) + r"(?![A-Za-z0-9_])"
            e2 = re.sub(patron, f" @{k}@ ", e)
            if e2 != e:
                fichas[f"@{k}@"] = n
                e = e2
        # funciones con estado y especiales
        for f in ("DELAY FIXED", "DELAY1I", "DELAY3I", "DELAY1", "DELAY3", "SMOOTHI", "SMOOTH", "WITH LOOKUP"):
            while f + "(" in e.replace(f + " (", f + "("):
                e = e.replace(f + " (", f + "(")
                i = e.index(f + "(")
                args, j = argumentos(e, i + len(f))
                if f == "WITH LOOKUP":
                    pts = [tuple(map(float, p.split(","))) for p in re.findall(r"\(([-\d.e]+,[-\d.e]+)\)", re.sub(r"\[.*?\]", "", args[1]))]
                    rep = f"LK({args[0]}, {pts!r})"
                else:
                    k = len(self.estados)
                    self.estados.append({"tipo": f, "args": [compile(self.sustituir(a, fichas).strip(), "<e>", "eval") for a in args], "st": None})
                    rep = f"EST({k})"
                e = e[:i] + rep + e[j + 1:]
        e = e.replace("IF THEN ELSE", "IFTE").replace("RANDOM NORMAL", "RN").replace("^", "**")
        return compile(self.sustituir(e, fichas).strip(), "<e>", "eval")

    @staticmethod
    def sustituir(e, fichas):
        for f, n in fichas.items():
            e = e.replace(f, f"V({n!r})")
        return e

    # entorno de evaluación
    def V(self, n):
        if n in self.niveles:
            nv = self.niveles[n]
            if nv["valor"] is None:
                nv["valor"] = self.ev(nv["ini"])
            return nv["valor"]
        if n not in self.cache:
            self.cache[n] = self.ev(self.code[n])
        return self.cache[n]

    def ev(self, c):
        return eval(c, {"V": self.V, "EST": self.est, "LK": lk, "MIN": min, "MAX": max, "ZIDZ": zidz, "XIDZ": xidz,
                        "IFTE": lambda c_, a, b: a if c_ else b, "STEP": lambda h, t0: h if self.t >= t0 - 1e-9 else 0,
                        "RN": self.rn, "exp": math.exp})

    def rn(self, lo, hi, media, sd, semilla):
        clave = ("rn", self.t)
        if clave not in self.cache:
            self.cache[clave] = max(lo, min(hi, self.rng.gauss(media, sd)))
        return self.cache[clave]

    def est(self, k):
        s = self.estados[k]
        a = s["args"]
        if s["st"] is None:  # inicialización perezosa con el valor de entrada en t0
            T = self.ev(a[1])
            x = None if s["tipo"] in ("SMOOTHI", "DELAY FIXED") else self.ev(a[2] if s["tipo"] in ("DELAY1I", "DELAY3I") else a[0])
            s["tipo"] = s["tipo"].rstrip("I") if s["tipo"] in ("DELAY1I", "DELAY3I") else s["tipo"]
            if s["tipo"] == "DELAY1":
                s["st"] = [x * T]
            elif s["tipo"] == "DELAY3":
                s["st"] = [x * T / 3] * 3
            elif s["tipo"] == "SMOOTH":
                s["st"] = [x]
            elif s["tipo"] == "SMOOTHI":
                s["st"] = [self.ev(a[2])]
            else:  # DELAY FIXED
                ini = self.ev(a[2])
                s["st"] = [ini] * max(1, round(T / self.dt))
        T = self.ev(a[1])
        if s["tipo"] == "DELAY1":
            return s["st"][0] / T
        if s["tipo"] == "DELAY3":
            return s["st"][2] / (T / 3)
        return s["st"][0]

    def avanzar(self):
        # calcula todo en t, luego integra (Euler)
        derivadas = {n: self.ev(nv["flujo"]) for n, nv in self.niveles.items()}
        nuevos = []
        for s in self.estados:
            x, T = self.ev(s["args"][0]), self.ev(s["args"][1])
            st = s["st"]
            if s["tipo"] == "DELAY1":
                nuevos.append([st[0] + self.dt * (x - st[0] / T)])
            elif s["tipo"] == "DELAY3":
                r = [v / (T / 3) for v in st]
                nuevos.append([st[0] + self.dt * (x - r[0]), st[1] + self.dt * (r[0] - r[1]), st[2] + self.dt * (r[1] - r[2])])
            elif s["tipo"] in ("SMOOTH", "SMOOTHI"):
                nuevos.append([st[0] + self.dt * (x - st[0]) / T])
            else:
                nuevos.append(st[1:] + [x])
        for (n, nv) in self.niveles.items():
            nv["valor"] = nv["valor"] + self.dt * derivadas[n]
        for s, st in zip(self.estados, nuevos):
            s["st"] = st
        self.t += self.dt
        self.cache = {}

    def correr(self, guardar):
        filas = []
        while self.t <= self.final + 1e-9:
            for n in self.nombres:  # fuerza la inicialización de todo en t0
                self.V(n)
            if abs(self.t * 4 - round(self.t * 4)) < 1e-6:
                fila = {"Time": round(self.t, 2)}
                fila.update({n: self.V(n) for n in guardar})
                filas.append(fila)
            if self.t + 1e-9 >= self.final:
                break
            self.avanzar()
        return pd.DataFrame(filas)


def lk(x, pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    if x <= xs[0]:
        return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return ys[-1]


def zidz(a, b):
    return 0 if b == 0 else a / b


def xidz(a, b, x):
    return x if b == 0 else a / b


# ------------------------------------------------------------------------------ ejecución
NIVELES = ["Usuarios activos", "Confianza de la comunidad", "Apelaciones pendientes", "Denuncias pendientes",
           "Moderadores en entrenamiento", "Moderadores activos"]
FLUJOS = ["Usuarios que llegan", "Usuarios que se van", "Cambio de confianza", "Apelaciones que llegan", "Apelaciones resueltas",
          "Denuncias que llegan", "Denuncias resueltas", "Voluntarios nuevos", "Moderadores graduados", "Moderadores que renuncian"]
OTRAS = ["Nocivo bloqueado", "Nocivo que se escapa", "Bloqueos por error", "Precision del filtro", "Apelaciones aceptadas",
         "Capacidad de revision", "Carga percibida", "Reputacion externa", "Confianza deseada",
         "Molestia por contenido nocivo", "Molestia por bloqueos injustos"]


def verificar_signos(eqs, archivo):
    """Compara la polaridad dibujada en el .mdl con el signo numérico de la derivada en t = 0."""
    texto = (MODELOS / archivo).read_text(encoding="utf-8").split("*Modelo Discord")[1]
    nombres = {}
    for l in texto.splitlines():
        c = l.split(",")
        if c[0] == "10":
            nombres[c[1]] = c[2]
    res = {"coincide": 0, "no verificable": [], "CONTRADICE": []}
    for l in texto.splitlines():
        c = l.split(",")
        if c[0] != "1" or c[7] == "22":
            continue
        org, dst = nombres.get(c[2]), nombres.get(c[3])
        if org is None or dst is None:
            continue
        signo = {"43": "+", "45": "-"}[c[6]]
        derivadas = []
        m = Modelo(eqs)
        for n in m.nombres:
            m.V(n)
        if m.code.get(dst) is None:  # nivel: no aplica
            continue
        base = m.ev(m.code[dst])
        for factor in (1.001, 0.999):
            valor = m.V(org)
            nuevo_valor = valor * factor if valor else (1e-6 if factor > 1 else -1e-6)
            guardado = dict(m.cache)
            nivel_previo = m.niveles[org]["valor"] if org in m.niveles else None
            if org in m.niveles:
                m.niveles[org]["valor"] = nuevo_valor
            else:
                m.cache[org] = nuevo_valor
            m.cache = {k: v for k, v in m.cache.items()}
            for k in list(m.cache):  # todo lo demás queda fijo (efecto directo, ceteris paribus)
                pass
            m.cache.pop(dst, None)
            nuevo = m.ev(m.code[dst])
            m.cache = guardado
            if nivel_previo is not None:
                m.niveles[org]["valor"] = nivel_previo
            derivadas.append((nuevo - base) * (1 if factor > 1 else -1))
        d = derivadas[0] if abs(derivadas[0]) > 1e-12 else derivadas[1]
        if abs(d) < 1e-12:
            res["no verificable"].append(f"{org} -> {dst} ({signo})")
        elif (d > 0) == (signo == "+"):
            res["coincide"] += 1
        else:
            res["CONTRADICE"].append(f"{org} -> {dst} (dibujado {signo})")
    return res


if __name__ == "__main__":
    res = {}
    escenarios = [("actual", "Discord_moderacion_actual.mdl", {}),
                  ("mejora", "Discord_moderacion_mejora.mdl", {}),
                  ("actual_S099", "Discord_moderacion_actual.mdl", {"Sensibilidad del filtro IA": "0.973 + STEP(0.017, 26)"}),
                  ("mejora_S099", "Discord_moderacion_mejora.mdl", {"Sensibilidad del filtro IA": "0.973 + STEP(0.017, 26)"})]
    for clave, archivo, cambios in escenarios:
        eqs = leer_mdl(MODELOS / archivo)
        if not cambios:
            r = verificar_signos(eqs, archivo)
            print(f"\n### Polaridades {archivo}: coinciden {r['coincide']} | no verificables en t=0 {len(r['no verificable'])} | contradicen {len(r['CONTRADICE'])}")
            for x in r["CONTRADICE"]:
                print("   CONTRADICE:", x)
            for x in r["no verificable"]:
                print("   no verificable:", x)
        m = Modelo(eqs, cambios)
        df = m.correr(NIVELES + FLUJOS + OTRAS)
        res[clave] = df
        df.to_csv(PROC / f"simulacion_{clave}.csv", index=False, encoding="utf-8-sig")
        neg = [c for c in NIVELES if (df[c] < -1e-6).any()]
        print(f"\n=== {clave} ({len(eqs) - 4} variables) | negativos: {neg or 'ninguno'} | NaN: {df.isna().any().any()}")
        t0 = df.iloc[0]
        ap = t0["Apelaciones que llegan"]
        print("  t=0  precisión {:.3f} | apelan {:.3f} | reversión {:.4f} | carga {:.2f} | confianza deseada {:.3f}".format(
            t0["Precision del filtro"], ap / (t0["Nocivo bloqueado"] + t0["Bloqueos por error"]),
            t0["Apelaciones aceptadas"] / t0["Apelaciones resueltas"], t0["Carga percibida"], t0["Confianza deseada"]))
        muestra = df[df.Time.isin([0, 26, 52, 78, 104])]
        print(muestra[["Time"] + NIVELES + ["Carga percibida"]].round(2).to_string(index=False))

    # gráficos de niveles y flujos (actual vs mejora), sin interpretación
    AZUL, NARANJA = "#2a78d6", "#eb6834"
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#ebeae6",
                         "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "font.size": 9, "axes.axisbelow": True})
    unidades = {"Usuarios activos": "usuarios", "Confianza de la comunidad": "índice 0-1 (Dmnl)", "Apelaciones pendientes": "piezas",
                "Denuncias pendientes": "piezas", "Moderadores en entrenamiento": "moderadores", "Moderadores activos": "moderadores"}
    for sufijo, titulo in (("", "escenario base"), ("_S099", "prueba: sensibilidad sube a 0,99 en la semana 26")):
        for grupo, cols, nombre in (("Niveles", NIVELES, "niveles"), ("Flujos", FLUJOS, "flujos")):
            filas = math.ceil(len(cols) / 2)
            fig, axs = plt.subplots(filas, 2, figsize=(11, 2.6 * filas), sharex=True)
            for ax, c in zip(axs.flat, cols):
                ax.plot(res["actual" + sufijo].Time, res["actual" + sufijo][c], color=AZUL, lw=2, label="Modelo actual")
                ax.plot(res["mejora" + sufijo].Time, res["mejora" + sufijo][c], color=NARANJA, lw=2, label="Modelo con mejora")
                ax.set_title(c, fontsize=10, fontweight="bold")
                ax.set_ylabel(unidades.get(c, "por semana (/Week)"))
            for ax in axs.flat[len(cols):]:
                ax.set_visible(False)
            for ax in axs[-1]:
                ax.set_xlabel("Tiempo (semanas)")
            axs.flat[0].legend(frameon=False)
            fig.suptitle(f"{grupo} del modelo – {titulo}", fontweight="bold")
            fig.text(0.01, 0.005, "Fuente: simulación de los modelos de Vensim (verificación en Python, Euler, dt = 0,25). "
                     "Parámetros: Discord Transparency Report 2022–2024 y DSA 2024–2025; ver MODELO_VENSIM.md",
                     fontsize=7, color="#52514e")
            fig.tight_layout(rect=(0, 0.02, 1, 0.97))
            fig.savefig(FIG / f"sim_{nombre}{sufijo or '_base'}.png", dpi=140)
            plt.close(fig)
    print("\nGráficos guardados en figuras/sim_*.png")
