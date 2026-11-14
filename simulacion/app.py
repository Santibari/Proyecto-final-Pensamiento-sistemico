"""Servidor de la simulación (fase 3).

Conexión con Vensim
-------------------
Todo sale de los archivos OFICIALES de Vensim (`Modelos Vensim/*.mdl`):
  - las ECUACIONES: PySD traduce el .mdl y lo ejecuta;
  - el DIAGRAMA: posiciones de niveles, flujos, variables y flechas (sección "Sketch" del .mdl);
  - las UNIDADES y los COMENTARIOS de cada variable (ayudas de la página);
  - los VALORES POR DEFECTO de los controles.
Si se modifica y guarda el .mdl en Vensim, en el siguiente pedido el servidor lo vuelve a traducir
(compara fechas de modificación) y la página muestra el modelo nuevo.

Ejecutar desde esta carpeta:   uvicorn app:app --port 8000
"""
import re
import shutil
import warnings
from pathlib import Path

import numpy as np
import pysd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

warnings.filterwarnings("ignore")
BASE = Path(__file__).resolve().parent
MODELOS = BASE.parent / "Modelos Vensim"
CACHE = BASE / "_cache_pysd"
ARCHIVOS = {"actual": "Discord_moderacion_actual.mdl", "mejora": "Discord_moderacion_mejora.mdl"}
CONTROL = {"FINAL TIME", "INITIAL TIME", "SAVEPER", "TIME STEP"}

# Controles del escenario personalizado (se aplican igual a los dos modelos)
CONTROLES = {
    "Sensibilidad del filtro IA": (0.90, 0.995, 0.001),
    "Fraccion de bloqueados que apela": (0.05, 0.40, 0.005),
    "Contenido nocivo por usuario": (0.005, 0.06, 0.001),
    "Tasa de voluntariado": (0.0, 4e-6, 1e-7),
    "Tasa normal de renuncia": (0.005, 0.06, 0.001),
}

app = FastAPI(title="Simulación Discord – PSO")


# ------------------------------------------------------------------ lectura del .mdl
def ruta_py(modelo: str) -> Path:
    """Traduce el .mdl con PySD cuando cambia y devuelve el .py generado (en caché)."""
    if modelo not in ARCHIVOS:
        raise HTTPException(404, f"Modelo desconocido: {modelo}")
    CACHE.mkdir(exist_ok=True)
    mdl, copia = MODELOS / ARCHIVOS[modelo], CACHE / ARCHIVOS[modelo]
    py = copia.with_suffix(".py")
    if not py.exists() or not copia.exists() or copia.stat().st_mtime < mdl.stat().st_mtime:
        shutil.copy2(mdl, copia)  # se traduce una copia para no dejar archivos en "Modelos Vensim"
        pysd.read_vensim(str(copia))
    return py


def leer_mdl(modelo: str):
    texto = (MODELOS / ARCHIVOS[modelo]).read_text(encoding="utf-8")
    ecuaciones, boceto = texto.split("\\\\\\---///", 1)
    variables = {}
    for bloque in ecuaciones.replace("{UTF-8}", "").split("|"):
        partes = bloque.split("~")
        if len(partes) < 3 or "=" not in partes[0]:
            continue
        izq, der = partes[0].split("=", 1)
        nombre = " ".join(izq.split())
        if not nombre or nombre in CONTROL or nombre.startswith("*"):
            continue
        ecuacion = " ".join(der.split())
        unidad = " ".join(partes[1].split()).split("[")[0].strip()
        comentario = " ".join(partes[2].split())
        if ecuacion.upper().startswith("INTEG"):
            tipo = "nivel"
        elif re.fullmatch(r"[-+\d.eE]+", ecuacion):
            tipo = "constante"
        else:
            tipo = "auxiliar"
        variables[nombre] = {"ecuacion": ecuacion, "unidad": unidad, "comentario": comentario, "tipo": tipo}
    # diagrama: todas las vistas del sketch (si el equipo agrega vistas en Vensim, se superponen)
    elementos, conexiones = {}, []
    for linea in boceto.split("///---\\\\\\")[0].splitlines():
        c = linea.split(",")
        if c[0] == "10" and len(c) > 8:
            nombre = c[2].strip('"')
            forma, bits = int(c[7]), int(c[8])
            if not bits & 1:  # variable sombra (bits = 2)
                continue
            if forma == 40 and nombre in variables:
                variables[nombre]["tipo"] = "flujo"
            elementos[c[1]] = {"id": c[1], "clase": "variable", "nombre": nombre, "x": int(c[3]), "y": int(c[4]),
                               "w": int(c[5]), "h": int(c[6]), "forma": forma}
        elif c[0] in ("11", "12"):
            elementos[c[1]] = {"id": c[1], "clase": "valvula" if c[0] == "11" else "nube", "x": int(c[3]), "y": int(c[4])}
        elif c[0] == "1" and len(c) > 7:
            punto = re.search(r"\|\((-?\d+),(-?\d+)\)\|", linea)
            conexiones.append({"de": c[2], "a": c[3], "tuberia": c[7] == "22", "sentido": int(c[4]),
                               "signo": {"43": "+", "45": "-"}.get(c[6], ""),
                               "control": [int(punto.group(1)), int(punto.group(2))] if punto else None})
    return variables, {"elementos": list(elementos.values()), "conexiones": conexiones}


# ------------------------------------------------------------------ API
class Pedido(BaseModel):
    parametros: dict[str, float] = {}


@app.get("/modelo/{modelo}")
def modelo_info(modelo: str):
    ruta_py(modelo)
    variables, diagrama = leer_mdl(modelo)
    return {"archivo": ARCHIVOS[modelo], "variables": variables, "diagrama": diagrama}


@app.get("/controles")
def controles():
    variables, _ = leer_mdl("actual")
    return [{"nombre": n, "min": a, "max": b, "paso": p, "valor": float(variables[n]["ecuacion"]),
             "unidad": variables[n]["unidad"], "comentario": variables[n]["comentario"]}
            for n, (a, b, p) in CONTROLES.items() if n in variables]


@app.post("/comparar")
def comparar(p: Pedido):
    """Corre el modelo actual y el modelo con mejora con los mismos parámetros, desde la semana 0."""
    validos = {}
    for k, v in p.parametros.items():
        if k not in CONTROLES:
            continue
        lo, hi, _ = CONTROLES[k]
        if not lo <= v <= hi:
            raise HTTPException(422, f"{k} fuera de rango [{lo}, {hi}]")
        validos[k] = float(v)
    salida = {}
    for nombre in ARCHIVOS:
        modelo = pysd.load(str(ruta_py(nombre)))  # carga limpia: los cambios no se arrastran
        r = modelo.run(params=validos, return_timestamps=np.arange(0, 104.0001, 0.25))
        r = r.drop(columns=[c for c in r.columns if c in CONTROL]).replace([np.inf, -np.inf], np.nan).fillna(0)
        salida[nombre] = {c: np.round(r[c].to_numpy(dtype=float), 6).tolist() for c in r.columns}
    return {"tiempo": [round(float(t), 2) for t in np.arange(0, 104.0001, 0.25)], **salida}


app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/")
def inicio():
    return FileResponse(BASE / "static" / "index.html")
