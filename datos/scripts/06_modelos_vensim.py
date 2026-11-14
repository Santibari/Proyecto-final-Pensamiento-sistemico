"""06_modelos_vensim.py – Genera los dos modelos de Vensim (versión 2, simplificada).

Salidas en "Modelos Vensim/":
  - Discord_moderacion_actual.mdl   (48 variables)
  - Discord_moderacion_mejora.mdl   (50 variables)

Características pedidas por el equipo:
  - máximo 50 variables, todo en UNA sola vista;
  - nombres comprensibles para cualquier persona;
  - flechas curvas y con polaridad (+ / −) en TODAS las flechas causales.
Contenido de clase cubierto: niveles, flujos, auxiliares y constantes · niveles en serie
(entrenamiento → moderadores activos) · niveles en paralelo (apelaciones y denuncias pendientes con
capacidad compartida) · heterogéneos acoplados (confianza ↔ usuarios) · DELAY1, DELAY3, DELAY FIXED,
SMOOTH · ciclos R y B · no linealidades · arquetipos: límites al crecimiento, desplazamiento de la
carga, tragedia de los comunes.
Convención de polaridad para tiempos (retrasos y tiempos de ajuste): "−" = un tiempo mayor hace más
lenta la respuesta.
"""
import math
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parents[2]
SALIDA = BASE / "Modelos Vensim"

# nombre -> (ecuación, unidad, comentario, tipo)  tipo: nivel / flujo / aux / const
E = {}


def eq(nombre, ecuacion, unidad, comentario, tipo):
    E[nombre] = (ecuacion, unidad, comentario, tipo)


# ------------------------------------------------------------------ USUARIOS Y CONFIANZA
eq("Usuarios activos", "INTEG(Usuarios que llegan - Usuarios que se van, 100000)", "usuarios",
   "Personas activas en la comunidad representativa de Discord (SUPUESTO: 100.000).", "nivel")
eq("Usuarios que llegan", "Usuarios activos * Tasa de crecimiento base * Reputacion externa", "usuarios/Week",
   "Los usuarios atraen a más usuarios (ciclo R1), según la reputación que la comunidad tiene afuera.", "flujo")
eq("Usuarios que se van", "Usuarios activos * Tasa de abandono por desconfianza * (1 - Confianza de la comunidad)",
   "usuarios/Week", "Cuanto menor es la confianza, más usuarios abandonan.", "flujo")
eq("Tasa de crecimiento base", "0.015", "1/Week", "SUPUESTO. Con reputación 0,8 da 1,2 % semanal.", "const")
eq("Tasa de abandono por desconfianza", "0.05", "1/Week", "SUPUESTO. Con confianza 0,8 da 1 % semanal.", "const")
eq("Reputacion externa", "DELAY FIXED(Confianza de la comunidad, Retraso de la reputacion, 0.8)", "Dmnl",
   "RETRASO DE INFORMACIÓN PURO (DELAY FIXED): la confianza interna tarda semanas en conocerse afuera.", "aux")
eq("Retraso de la reputacion", "6", "Week", "SUPUESTO.", "const")
eq("Confianza de la comunidad", "INTEG(Cambio de confianza, 0.8)", "Dmnl",
   "Índice de 0 a 1 (SUPUESTO: los informes no miden confianza). Nivel de información.", "nivel")
eq("Cambio de confianza", "(Confianza deseada - Confianza de la comunidad) / Tiempo para ajustar la confianza", "1/Week",
   "La confianza se acerca poco a poco a la confianza deseada (retraso de percepción de primer orden).", "flujo")
eq("Tiempo para ajustar la confianza", "8", "Week", "SUPUESTO.", "const")
eq("Confianza deseada", "MAX(0, 1 - Molestia por contenido nocivo - Molestia por bloqueos injustos)", "Dmnl",
   "Confianza que tendría la comunidad con el nivel actual de molestias.", "aux")
eq("Molestia por contenido nocivo",
   "(Nocivo que se escapa / Usuarios activos) * ZIDZ(Denuncias pendientes, Denuncias resueltas) / Tolerancia al contenido nocivo",
   "Dmnl", "Contenido nocivo que cada usuario ve, multiplicado por el tiempo que sigue visible mientras la denuncia espera.", "aux")
eq("Tolerancia al contenido nocivo", "0.001836", "piezas/usuarios",
   "CALIBRADO: con los valores iniciales la molestia vale 0,1.", "const")
eq("Molestia por bloqueos injustos", "MAX(0, Bloqueos por error - Apelaciones aceptadas) / Usuarios activos / Tolerancia a bloqueos injustos",
   "Dmnl", "Bloqueos a contenido legítimo que nadie corrige, por usuario.", "aux")
eq("Tolerancia a bloqueos injustos", "0.1573", "piezas/(usuarios*Week)",
   "CALIBRADO: con los valores iniciales la molestia vale 0,1.", "const")

# ------------------------------------------------------------------ CONTENIDO Y FILTRO DE IA
eq("Contenido nocivo por usuario", "0.02", "piezas/(usuarios*Week)",
   "SUPUESTO: 1 de cada 1.000 mensajes (20 mensajes por usuario a la semana) es nocivo (no-spam).", "const")
eq("Mensajes sanos por usuario", "19.98", "piezas/(usuarios*Week)", "SUPUESTO: el resto de los 20 mensajes semanales.", "const")
eq("Contenido nocivo", "Usuarios activos * Contenido nocivo por usuario", "piezas/Week", "Acoso, odio, etc. (sin spam).", "aux")
eq("Sensibilidad del filtro IA", "0.973", "Dmnl [0.5,0.999,0.001]",
   "PALANCA DE POLÍTICA. DATO: el sistema automático detecta 97,3 % del contenido infractor (DSA 2025, p. 9).", "const")
eq("Nocivo bloqueado", "Contenido nocivo * Sensibilidad del filtro IA", "piezas/Week", "Aciertos del filtro (verdaderos positivos).", "aux")
eq("Nocivo que se escapa", "Contenido nocivo * (1 - Sensibilidad del filtro IA)", "piezas/Week",
   "Contenido nocivo que el filtro no detecta (falsos negativos).", "aux")
eq("Factor de error del filtro", "2.2033e-005", "Dmnl",
   "CALIBRADO para que la precisión inicial sea 55,1 % (DSA 2025, p. 9).", "const")
eq("Bloqueos por error",
   "Usuarios activos * Mensajes sanos por usuario * Factor de error del filtro * Sensibilidad del filtro IA / (1 - Sensibilidad del filtro IA)",
   "piezas/Week", "Contenido legítimo bloqueado (falsos positivos). NO LINEAL: crece muy rápido cuando la sensibilidad se acerca a 1.", "aux")
eq("Precision del filtro", "ZIDZ(Nocivo bloqueado, Nocivo bloqueado + Bloqueos por error)", "Dmnl",
   "De todo lo bloqueado, qué fracción era realmente nociva. Meta: 0,551 (DSA 2025).", "aux")

# ------------------------------------------------------------------ COLAS EN PARALELO
eq("Apelaciones pendientes", "INTEG(Apelaciones que llegan - Apelaciones resueltas, 186)", "piezas",
   "Cola EN PARALELO con las denuncias: ambas usan la misma capacidad de revisión.", "nivel")
eq("Apelaciones que llegan",
   "DELAY3((Nocivo bloqueado + Bloqueos por error) * Fraccion de bloqueados que apela, Tiempo de reaccion de los usuarios)",
   "piezas/Week", "RETRASO MATERIAL DE TERCER ORDEN (DELAY3): los usuarios bloqueados tardan en apelar.", "flujo")
eq("Fraccion de bloqueados que apela", "0.155", "Dmnl", "DATO: mediana de la tasa de apelación 2022-2023 (informes generales).", "const")
eq("Tiempo de reaccion de los usuarios", "1", "Week", "SUPUESTO: tiempo para apelar o denunciar.", "const")
eq("Apelaciones resueltas",
   "MIN(Apelaciones pendientes / Tiempo minimo de revision, Capacidad de revision * XIDZ(Apelaciones pendientes, Apelaciones pendientes + Denuncias pendientes, 0.5))",
   "piezas/Week", "La capacidad se reparte entre las dos colas según su tamaño (recurso común).", "flujo")
eq("Tiempo minimo de revision", "0.34", "Week", "DATO: 57,34 h, mediana de resolución de quejas (DSA 2024).", "const")
eq("Apelaciones aceptadas", "Apelaciones resueltas * (1 - Precision del filtro) * Probabilidad de corregir un error", "piezas/Week",
   "Bloqueos por error que se revierten al apelar.", "aux")
eq("Probabilidad de corregir un error", "0.0532", "Dmnl",
   "CALIBRADO: reversión inicial 2,39 % (mediana de cuentas restauradas / apelaciones, Q1 2022 - H1 2024).", "const")
eq("Denuncias pendientes", "INTEG(Denuncias que llegan - Denuncias resueltas, 9)", "piezas",
   "Cola EN PARALELO: contenido nocivo denunciado por usuarios.", "nivel")
eq("Denuncias que llegan", "DELAY1(Nocivo que se escapa * Fraccion de nocivo denunciado, Tiempo de reaccion de los usuarios)",
   "piezas/Week", "RETRASO MATERIAL DE PRIMER ORDEN (DELAY1).", "flujo")
eq("Fraccion de nocivo denunciado", "0.5", "Dmnl", "SUPUESTO.", "const")
eq("Denuncias resueltas",
   "MIN(Denuncias pendientes / Tiempo minimo de revision, Capacidad de revision * XIDZ(Denuncias pendientes, Apelaciones pendientes + Denuncias pendientes, 0.5))",
   "piezas/Week", "", "flujo")

# ------------------------------------------------------------------ MODERADORES EN SERIE
eq("Capacidad de revision", "Moderadores activos * Productividad por moderador", "piezas/Week",
   "Recurso común que comparten apelaciones y denuncias (tragedia de los comunes).", "aux")
eq("Productividad por moderador", "120", "piezas/(moderadores*Week)", "SUPUESTO: carga inicial cercana a 0,8.", "const")
eq("Carga percibida",
   "SMOOTH(XIDZ(Apelaciones que llegan + Denuncias que llegan, Capacidad de revision, 10), Tiempo para percibir la carga)",
   "Dmnl", "RETRASO DE INFORMACIÓN (SMOOTH): trabajo que llega ÷ capacidad, como lo perciben los moderadores con retraso.", "aux")
eq("Tiempo para percibir la carga", "4", "Week", "SUPUESTO.", "const")
eq("Moderadores en entrenamiento", "INTEG(Voluntarios nuevos - Moderadores graduados, 0.48)", "moderadores",
   "NIVEL EN SERIE con Moderadores activos.", "nivel")
eq("Voluntarios nuevos", "Usuarios activos * Tasa de voluntariado * Confianza de la comunidad", "moderadores/Week",
   "Una comunidad que confía aporta voluntarios.", "flujo")
eq("Tasa de voluntariado", "1.5e-006", "moderadores/(usuarios*Week)", "CALIBRADO: voluntarios iniciales = renuncias iniciales.", "const")
eq("Moderadores graduados", "Moderadores en entrenamiento / Tiempo de entrenamiento", "moderadores/Week", "", "flujo")
eq("Tiempo de entrenamiento", "4", "Week", "SUPUESTO.", "const")
eq("Moderadores activos", "INTEG(Moderadores graduados - Moderadores que renuncian, 6)", "moderadores",
   "SUPUESTO: 6 moderadores (el DSA no publica personal).", "nivel")
eq("Moderadores que renuncian", "Moderadores activos * Tasa normal de renuncia * MIN(4, MAX(1, Carga percibida) ^ 2)", "moderadores/Week",
   "NO LINEAL: por encima de carga 1 el agotamiento multiplica las renuncias (ciclo R2), como máximo por 4 (SUPUESTO).", "flujo")
eq("Tasa normal de renuncia", "0.02", "1/Week", "SUPUESTO: un moderador dura en promedio 50 semanas.", "const")

ACTUAL = dict(E)

# ------------------------------------------------------------------ MODELO CON MEJORA
M = dict(E)
M["Productividad por moderador"] = ("160", "piezas/(moderadores*Week)",
                                    "MEJORA 2 - Triage asistido por IA: +33 % de productividad (SUPUESTO; actual 120).", "const")
M["Sensibilidad efectiva del filtro"] = (
    "Sensibilidad del filtro IA / (1 + Ajuste automatico de sensibilidad * MAX(0, XIDZ((Apelaciones pendientes + Denuncias pendientes) / Tiempo minimo de revision, Capacidad de revision, 10) - 1))",
    "Dmnl", "MEJORA 1 - Sensibilidad adaptativa: el filtro se vuelve menos estricto cuando el trabajo pendiente supera la capacidad (ciclo B5).", "aux")
M["Ajuste automatico de sensibilidad"] = ("0.1", "Dmnl", "MEJORA 1 (SUPUESTO).", "const")
for v in ("Nocivo bloqueado", "Nocivo que se escapa", "Bloqueos por error"):
    e, u, c, t = M[v]
    M[v] = (e.replace("Sensibilidad del filtro IA", "Sensibilidad efectiva del filtro"), u, c, t)

# ------------------------------------------------------------------ DIAGRAMA (una vista)
NIVELES = {"Usuarios activos": (700, 110), "Confianza de la comunidad": (700, 300), "Apelaciones pendientes": (900, 640),
           "Denuncias pendientes": (900, 800), "Moderadores en entrenamiento": (850, 1010), "Moderadores activos": (1170, 1010)}
FLUJOS = {  # nombre: (origen, destino, x_valvula, y)
    "Usuarios que llegan": ("nube@330", "Usuarios activos", 510, 110),
    "Usuarios que se van": ("Usuarios activos", "nube@1060", 890, 110),
    "Cambio de confianza": ("nube@330", "Confianza de la comunidad", 510, 300),
    "Apelaciones que llegan": ("nube@560", "Apelaciones pendientes", 730, 640),
    "Apelaciones resueltas": ("Apelaciones pendientes", "nube@1250", 1070, 640),
    "Denuncias que llegan": ("nube@560", "Denuncias pendientes", 730, 800),
    "Denuncias resueltas": ("Denuncias pendientes", "nube@1250", 1070, 800),
    "Voluntarios nuevos": ("nube@560", "Moderadores en entrenamiento", 700, 1010),
    "Moderadores graduados": ("Moderadores en entrenamiento", "Moderadores activos", 1010, 1010),
    "Moderadores que renuncian": ("Moderadores activos", "nube@1470", 1330, 1010),
}
AUX = {
    "Tasa de crecimiento base": (430, 30), "Reputacion externa": (470, 200), "Retraso de la reputacion": (280, 200),
    "Tasa de abandono por desconfianza": (1010, 30), "Tiempo para ajustar la confianza": (330, 380),
    "Confianza deseada": (520, 420), "Molestia por contenido nocivo": (290, 500), "Tolerancia al contenido nocivo": (100, 430),
    "Molestia por bloqueos injustos": (770, 460), "Tolerancia a bloqueos injustos": (990, 420),
    "Contenido nocivo por usuario": (90, 560), "Contenido nocivo": (230, 620), "Sensibilidad del filtro IA": (90, 700),
    "Nocivo bloqueado": (380, 690), "Nocivo que se escapa": (380, 800), "Mensajes sanos por usuario": (90, 880),
    "Factor de error del filtro": (200, 960), "Bloqueos por error": (390, 910), "Precision del filtro": (580, 550),
    "Fraccion de bloqueados que apela": (530, 720), "Tiempo de reaccion de los usuarios": (690, 730),
    "Fraccion de nocivo denunciado": (560, 880), "Apelaciones aceptadas": (1050, 540),
    "Probabilidad de corregir un error": (1260, 540), "Tiempo minimo de revision": (1250, 720),
    "Capacidad de revision": (1170, 900), "Productividad por moderador": (1390, 900), "Carga percibida": (1410, 800),
    "Tiempo para percibir la carga": (1420, 700), "Tasa de voluntariado": (560, 1090), "Tiempo de entrenamiento": (1010, 1100),
    "Tasa normal de renuncia": (1400, 1100),
    "Sensibilidad efectiva del filtro": (220, 760), "Ajuste automatico de sensibilidad": (90, 790),
}
# Polaridad de TODAS las flechas (origen, destino) -> signo
P = {
    ("Usuarios activos", "Usuarios que llegan"): "+", ("Tasa de crecimiento base", "Usuarios que llegan"): "+",
    ("Reputacion externa", "Usuarios que llegan"): "+",
    ("Usuarios activos", "Usuarios que se van"): "+", ("Tasa de abandono por desconfianza", "Usuarios que se van"): "+",
    ("Confianza de la comunidad", "Usuarios que se van"): "-",
    ("Confianza de la comunidad", "Reputacion externa"): "+", ("Retraso de la reputacion", "Reputacion externa"): "-",
    ("Confianza deseada", "Cambio de confianza"): "+", ("Confianza de la comunidad", "Cambio de confianza"): "-",
    ("Tiempo para ajustar la confianza", "Cambio de confianza"): "-",
    ("Molestia por contenido nocivo", "Confianza deseada"): "-", ("Molestia por bloqueos injustos", "Confianza deseada"): "-",
    ("Nocivo que se escapa", "Molestia por contenido nocivo"): "+", ("Usuarios activos", "Molestia por contenido nocivo"): "-",
    ("Denuncias pendientes", "Molestia por contenido nocivo"): "+", ("Denuncias resueltas", "Molestia por contenido nocivo"): "-",
    ("Tolerancia al contenido nocivo", "Molestia por contenido nocivo"): "-",
    ("Bloqueos por error", "Molestia por bloqueos injustos"): "+", ("Apelaciones aceptadas", "Molestia por bloqueos injustos"): "-",
    ("Usuarios activos", "Molestia por bloqueos injustos"): "-", ("Tolerancia a bloqueos injustos", "Molestia por bloqueos injustos"): "-",
    ("Usuarios activos", "Contenido nocivo"): "+", ("Contenido nocivo por usuario", "Contenido nocivo"): "+",
    ("Contenido nocivo", "Nocivo bloqueado"): "+", ("Sensibilidad del filtro IA", "Nocivo bloqueado"): "+",
    ("Contenido nocivo", "Nocivo que se escapa"): "+", ("Sensibilidad del filtro IA", "Nocivo que se escapa"): "-",
    ("Usuarios activos", "Bloqueos por error"): "+", ("Mensajes sanos por usuario", "Bloqueos por error"): "+",
    ("Factor de error del filtro", "Bloqueos por error"): "+", ("Sensibilidad del filtro IA", "Bloqueos por error"): "+",
    ("Nocivo bloqueado", "Precision del filtro"): "+", ("Bloqueos por error", "Precision del filtro"): "-",
    ("Nocivo bloqueado", "Apelaciones que llegan"): "+", ("Bloqueos por error", "Apelaciones que llegan"): "+",
    ("Fraccion de bloqueados que apela", "Apelaciones que llegan"): "+",
    ("Tiempo de reaccion de los usuarios", "Apelaciones que llegan"): "-",
    ("Apelaciones pendientes", "Apelaciones resueltas"): "+", ("Tiempo minimo de revision", "Apelaciones resueltas"): "-",
    ("Capacidad de revision", "Apelaciones resueltas"): "+", ("Denuncias pendientes", "Apelaciones resueltas"): "-",
    ("Apelaciones resueltas", "Apelaciones aceptadas"): "+", ("Precision del filtro", "Apelaciones aceptadas"): "-",
    ("Probabilidad de corregir un error", "Apelaciones aceptadas"): "+",
    ("Nocivo que se escapa", "Denuncias que llegan"): "+", ("Fraccion de nocivo denunciado", "Denuncias que llegan"): "+",
    ("Tiempo de reaccion de los usuarios", "Denuncias que llegan"): "-",
    ("Denuncias pendientes", "Denuncias resueltas"): "+", ("Tiempo minimo de revision", "Denuncias resueltas"): "-",
    ("Capacidad de revision", "Denuncias resueltas"): "+", ("Apelaciones pendientes", "Denuncias resueltas"): "-",
    ("Moderadores activos", "Capacidad de revision"): "+", ("Productividad por moderador", "Capacidad de revision"): "+",
    ("Apelaciones que llegan", "Carga percibida"): "+", ("Denuncias que llegan", "Carga percibida"): "+",
    ("Capacidad de revision", "Carga percibida"): "-", ("Tiempo para percibir la carga", "Carga percibida"): "-",
    ("Usuarios activos", "Voluntarios nuevos"): "+", ("Tasa de voluntariado", "Voluntarios nuevos"): "+",
    ("Confianza de la comunidad", "Voluntarios nuevos"): "+",
    ("Moderadores en entrenamiento", "Moderadores graduados"): "+", ("Tiempo de entrenamiento", "Moderadores graduados"): "-",
    ("Moderadores activos", "Moderadores que renuncian"): "+", ("Tasa normal de renuncia", "Moderadores que renuncian"): "+",
    ("Carga percibida", "Moderadores que renuncian"): "+",
    # mejora
    ("Sensibilidad del filtro IA", "Sensibilidad efectiva del filtro"): "+",
    ("Ajuste automatico de sensibilidad", "Sensibilidad efectiva del filtro"): "-",
    ("Apelaciones pendientes", "Sensibilidad efectiva del filtro"): "-", ("Denuncias pendientes", "Sensibilidad efectiva del filtro"): "-",
    ("Tiempo minimo de revision", "Sensibilidad efectiva del filtro"): "+", ("Capacidad de revision", "Sensibilidad efectiva del filtro"): "+",
    ("Contenido nocivo", "Nocivo bloqueado"): "+", ("Sensibilidad efectiva del filtro", "Nocivo bloqueado"): "+",
    ("Sensibilidad efectiva del filtro", "Nocivo que se escapa"): "-", ("Sensibilidad efectiva del filtro", "Bloqueos por error"): "+",
}


# Escala del lienzo: separa las variables para que los nombres no se monten
EX, EY = 1.5, 1.3
NIVELES = {k: (int(x * EX), int(y * EY)) for k, (x, y) in NIVELES.items()}


def _escalar_extremo(e):
    return f"nube@{int(int(e[5:]) * EX)}" if e.startswith("nube@") else e


FLUJOS = {k: (_escalar_extremo(o), _escalar_extremo(d), int(x * EX), int(y * EY)) for k, (o, d, x, y) in FLUJOS.items()}
AUX = {k: (int(x * EX), int(y * EY)) for k, (x, y) in AUX.items()}


def dependencias(nombre, modelo):
    ecuacion = modelo[nombre][0]
    if ecuacion.startswith("INTEG"):  # los flujos se conectan con tuberías
        return []
    deps = []
    for otro in sorted(modelo, key=len, reverse=True):
        patron = r"(?<![A-Za-z0-9_])" + re.escape(otro) + r"(?![A-Za-z0-9_])"
        if otro != nombre and re.search(patron, ecuacion):
            deps.append(otro)
            ecuacion = re.sub(patron, " ", ecuacion)
    return deps


def ancho(nombre):
    return int(len(nombre) * 3.3) + 6


def sketch(modelo):
    L = ["\\\\\\---/// Sketch information - do not modify anything except names",
         "V300  Do not put anything below this section - it will be ignored",
         "*Modelo Discord",
         "$192-192-192,0,Times New Roman|12||0-0-0|0-0-0|0-0-255|-1--1--1|-1--1--1|96,96,100,0"]
    ids, pos, n = {}, {}, [0]

    def nuevo():
        n[0] += 1
        return n[0]

    for nom, (x, y) in NIVELES.items():
        i = nuevo()
        ids[nom], pos[nom] = i, (x, y)
        L.append(f"10,{i},{nom},{x},{y},{ancho(nom) + 8},24,3,3,0,0,0,0,0,0")
    for nom, (org, dst, x, y) in FLUJOS.items():
        ext = []
        for e in (org, dst):
            if e.startswith("nube@"):
                cx = int(e[5:])
                i = nuevo()
                L.append(f"12,{i},48,{cx},{y},10,8,0,3,0,0,-1,0,0,0")
                ext.append((i, cx))
            else:
                ext.append((ids[e], NIVELES[e][0]))
        p1, p2, val, var = nuevo(), nuevo(), nuevo(), nuevo()
        (io, xo), (idd, xd) = ext
        ids[nom], pos[nom] = var, (x, y + 28)
        L.append(f"1,{p1},{val},{idd},4,0,0,22,0,0,0,-1--1--1,,1|({(x + xd) // 2},{y})|")
        L.append(f"1,{p2},{val},{io},100,0,0,22,0,0,0,-1--1--1,,1|({(x + xo) // 2},{y})|")
        L.append(f"11,{val},48,{x},{y},6,8,34,3,0,0,1,0,0,0")
        L.append(f"10,{var},{nom},{x},{y + 28},{ancho(nom)},11,40,3,0,0,-1,0,0,0")
    for nom, (x, y) in AUX.items():
        if nom in modelo:
            i = nuevo()
            ids[nom], pos[nom] = i, (x, y)
            L.append(f"10,{i},{nom},{x},{y},{ancho(nom)},11,8,3,0,0,0,0,0,0")
    faltan = []
    for dst in modelo:
        for org in dependencias(dst, modelo):
            signo = P.get((org, dst))
            if signo is None:
                faltan.append((org, dst))
                continue
            (x0, y0), (x1, y1) = pos[org], pos[dst]
            dx, dy = x1 - x0, y1 - y0
            largo = math.hypot(dx, dy) or 1
            k = 0.10 * largo  # curvatura: punto de control desplazado en perpendicular
            cx, cy = int((x0 + x1) / 2 - dy / largo * k), int((y0 + y1) / 2 + dx / largo * k)
            L.append(f"1,{nuevo()},{ids[org]},{ids[dst]},1,0,{43 if signo == '+' else 45},0,0,64,0,-1--1--1,,1|({cx},{cy})|")
    if faltan:
        raise SystemExit("Flechas sin polaridad: " + "; ".join(f"{a} -> {b}" for a, b in faltan))
    return L


def escribir(modelo, archivo):
    out = ["{UTF-8}"]
    for nom, (ecu, uni, com, _t) in modelo.items():
        if ecu.startswith("INTEG("):
            cuerpo = ecu[6:-1]
            k = cuerpo.rindex(",")
            out.append(f"{nom}= INTEG (\n\t{cuerpo[:k].strip()},\n\t\t{cuerpo[k + 1:].strip()})")
        else:
            out.append(f"{nom}=\n\t{ecu}")
        out.append(f"\t~\t{uni}\n\t~\t{com}\n\t|\n")
    out += ["********************************************************\n\t.Control\n********************************************************~",
            "\t\tSimulation Control Parameters\n\t|\n",
            "FINAL TIME  = 104\n\t~\tWeek\n\t~\tHorizonte de 104 semanas (mínimo exigido: 70).\n\t|\n",
            "INITIAL TIME  = 0\n\t~\tWeek\n\t~\tThe initial time for the simulation.\n\t|\n",
            "SAVEPER  = \n        TIME STEP\n\t~\tWeek [0,?]\n\t~\tThe frequency with which output is stored.\n\t|\n",
            "TIME STEP  = 0.25\n\t~\tWeek [0,?]\n\t~\tMenor que la constante de tiempo más corta (0,34 semanas).\n\t|\n"]
    out += sketch(modelo)
    out += ["///---\\\\\\", ":L<%^E!@", "9:Current", "15:0,0,0,0,0,0", "19:100,0", "5:Usuarios activos", ""]
    SALIDA.mkdir(exist_ok=True)
    (SALIDA / archivo).write_text("\n".join(out), encoding="utf-8")
    tipos = {t: sum(1 for v in modelo.values() if v[3] == t) for t in ("nivel", "flujo", "aux", "const")}
    flechas = sum(len(dependencias(v, modelo)) for v in modelo)
    print(f"{archivo}: {len(modelo)} variables {tipos} · {flechas} flechas con polaridad")


if __name__ == "__main__":
    for mod in (ACTUAL, M):
        for v in mod:
            if v not in NIVELES and v not in FLUJOS and v not in AUX:
                raise SystemExit(f"Sin posición: {v}")
        assert len(mod) <= 50, len(mod)
    escribir(ACTUAL, "Discord_moderacion_actual.mdl")
    escribir(M, "Discord_moderacion_mejora.mdl")
