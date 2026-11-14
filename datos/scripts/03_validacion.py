"""03_validacion.py – Valida las cifras extraídas y documenta cambios de definición.

1. Suma de categorías frente al total publicado, por métrica y periodo.
2. Cifras de control del plan (H1 2024 y 2026).
3. Anomalías detectadas en la fuente.
4. Cambios de definición entre informes.
Salida: processed/validacion.md y processed/validacion_sumas.csv
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import re
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROC, TXT, RAW = BASE / "processed", BASE / "interim" / "texto_pdf", BASE / "raw"

df = pd.read_csv(PROC / "discord_transparencia_largo.csv")
gen = df[~df["metrica"].str.startswith("dsa") & ~df["metrica"].str.startswith("pct")]


def valor(clave, metrica, categoria):
    s = df[(df.clave_informe == clave) & (df.metrica == metrica) & (df.categoria == categoria)]["valor"]
    return None if s.empty else s.iloc[0]


def fmt(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{v:,.0f}".replace(",", ".") if float(v).is_integer() else f"{v:,.2f}".replace(".", "#").replace(",", ".").replace("#", ",")


# ---------------------------------------------------------------- 1. sumas
filas = []
for (clave, met), g in gen.groupby(["clave_informe", "metrica"]):
    tot = g[g.categoria.isin(["total_no_spam", "total"])]["valor"]
    cats = g[~g.categoria.isin(["total_no_spam", "total", "spam"])]["valor"]
    if tot.empty or cats.empty:
        continue
    t, s = tot.iloc[0], cats.sum()
    filas.append({"clave_informe": clave, "metrica": met, "total_publicado": t, "suma_categorias": s,
                  "diferencia": s - t, "dif_pct": round(100 * (s - t) / t, 3) if t else None})
sumas = pd.DataFrame(filas)
sumas.to_csv(PROC / "validacion_sumas.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- 2. control
control_h1 = [
    ("Cuentas deshabilitadas totales", 35813609, (valor("H1-2024", "cuentas_deshabilitadas", "spam") or 0) + (valor("H1-2024", "cuentas_deshabilitadas", "total_no_spam") or 0), "p. 5 (suma spam + no-spam)"),
    ("Cuentas deshabilitadas por spam", 35456553, valor("H1-2024", "cuentas_deshabilitadas", "spam"), "p. 5, p. 16"),
    ("Cuentas deshabilitadas no-spam", 357056, valor("H1-2024", "cuentas_deshabilitadas", "total_no_spam"), "p. 5; CSV"),
    ("Servidores eliminados", 41002, valor("H1-2024", "servidores_eliminados", "total_no_spam"), "CSV; PDF"),
    ("Reportes", 29495313, valor("H1-2024", "reportes_recibidos_en_app", "total"), "CSV; PDF"),
    ("% de cuentas sancionadas que apelaron", 1.85, valor("H1-2024", "pct_cuentas_que_apelan", "total_no_spam"), "p. 9; CSV"),
    ("Cuentas restauradas", 1705, valor("H1-2024", "apelaciones_concedidas", "total_no_spam"), "p. 9"),
    ("% restauradas de las que apelaron", 2.59, valor("H1-2024", "pct_apelaciones_concedidas", "total_no_spam"), "p. 9"),
]
control_26 = [
    ("Cuentas de spam deshabilitadas", 47832832),
    ("Reportes no-spam", 34304587),
    ("Reportes de spam", 26174231),
    ("Cuentas que apelaron", 585307),
    ("Intervenciones retiradas", 60686),
    ("% intervenciones retiradas", "10.37%"),
]
txt26 = TXT / "Discord-Transparency-Report-2026-Updated.txt"
paginas26 = open(txt26, encoding="utf-8").read().split("=== PAGINA ")[1:] if txt26.exists() else None


def buscar26(v):
    if paginas26 is None:
        return "PDF 2026 no descargado"
    cad = v if isinstance(v, str) else f"{v:,}"
    pags = [p.split(" ===")[0] for p in paginas26 if cad in re.sub(r"\s+", " ", p)]
    return f"Coincide (p. {', '.join(pags)})" if pags else "NO aparece en el PDF"


# ---------------------------------------------------------------- 3. escribir informe
L = ["# Validación de cifras – Informes de transparencia de Discord", "",
     "Generado por `scripts/03_validacion.py`. Fuente: https://discord.com/safety-transparency", "",
     "## 1. Cifras de control H1 2024", "",
     "| Indicador | Control | Extraído | Resultado | Ubicación |", "|---|---|---|---|---|"]
for nombre, ctl, ext, ubi in control_h1:
    ok = ext is not None and abs(float(ext) - float(ctl)) < 1e-6
    L.append(f"| {nombre} | {fmt(ctl)} | {fmt(ext)} | {'Coincide' if ok else 'NO coincide'} | {ubi} |")
L += ["", "> Nota: el 1,85 % de H1 2024 se calcula sobre 3.568.821 *cuentas sancionadas distintas* "
      "(\"Distinct Accounts Actioned\", incluye advertencias e intervenciones temporales), no sobre cuentas deshabilitadas. "
      "En 2022–2023 la base era *cuentas deshabilitadas*. Ver sección 5.", "",
      "## 2. Cifras de control 2026 (marzo 2025 – marzo 2026)", "",
      "| Indicador | Valor de control (sin verificar) | Resultado |", "|---|---|---|"]
for nombre, v in control_26:
    L.append(f"| {nombre} | {v if isinstance(v, str) else fmt(v)} | {buscar26(v)} |")
if paginas26 is None:
    L += ["", "**DESCARTADAS:** `Discord-Transparency-Report-2026-Updated.pdf` no se pudo descargar (la red bloquea "
          "cdn.discordapp.com) y el equipo no lo encontró. Por decisión del equipo (14-11-2026) se trabaja solo con "
          "Q1 2022 – H1 2024 y DSA 2024–2025. Estas cifras NO se usan en el análisis ni en la calibración del modelo."]

L += ["", "## 3. Suma de categorías frente al total publicado", "",
      "Diferencias distintas de cero (las demás cuadran exactamente; detalle completo en `validacion_sumas.csv`):", "",
      "| Periodo | Métrica | Total publicado | Suma categorías | Diferencia |", "|---|---|---|---|---|"]
dif = sumas[sumas.diferencia.abs() > 0.5]
for _, r in dif.iterrows():
    L.append(f"| {r.clave_informe} | {r.metrica} | {fmt(r.total_publicado)} | {fmt(r.suma_categorias)} | {fmt(r.diferencia)} |")
if dif.empty:
    L.append("| — | — | — | — | Todas cuadran |")
L.append(f"\nCombinaciones revisadas: {len(sumas)}; cuadran exactamente: {(sumas.diferencia.abs() <= 0.5).sum()}.")

# anomalías
a = []
w22 = [valor("Q3-2022", "advertencias_cuentas", "total_no_spam"), valor("Q3-2022", "advertencias_servidores", "total_no_spam")]
w23 = [valor("Q1-2023", "advertencias_cuentas", "total_no_spam"), valor("Q1-2023", "advertencias_servidores", "total_no_spam")]
if w22 == w23:
    a.append(f"**Advertencias Q3 2022 = Q1 2023.** Los CSV de ambos informes traen exactamente las mismas cifras de advertencias "
             f"({fmt(w22[0])} cuentas, {fmt(w22[1])} servidores). Probable error de copia en la fuente: no usar las advertencias de Q3 2022 sin revisar el PDF.")
a.append("**NCMEC Q2 2022 = Q1 2022** (10.641 reportes de medios y 54 escalamientos en ambos CSV). No se usa en el modelo; se deja anotado.")
a.append("**Q3 2023 – tabla 'Accounts Disabled' del CSV desalineada** una fila. Se corrigió con la tabla Appeals del mismo CSV, "
         "verificada contra el PDF (p. 13: seguridad infantil 128.153; p. 19: extremismo violento 8.300). Total 260.461 cuadra.")
a.append("**Q3 2023 – Desinformación en Appeals:** 49 cuentas deshabilitadas y 596 apelaciones con 0,00 %. Inconsistente en la fuente; no se usa por categoría.")
a.append("**Q2 2022 – tasa de reinstalación 0,60 %** (733 de 122.714 apelaciones; PDF p. 6 dice \".6%\"). Es atípica frente al 2–4,6 % de los demás trimestres; es dato de la fuente.")
a.append("**DSA 2025 – quejas internas:** total 334.874, pero confirmadas (552) + revertidas (86) = 638. El desglose no cubre el total; "
         "la tasa de reversión DSA 2025 NO se puede calcular con fiabilidad.")
a.append("**DSA 2025 – medios automatizados:** las medidas 'solo automatizadas' de iniciativa propia (35.731) superan el total (30.740). Inconsistencia de la fuente.")
a.append("**DSA 2024 – fila de ítems solo automatizados** con periodo 'YYYY-MM-DD' en el CSV (plantilla sin llenar); el valor 114.252 sí aparece en el PDF p. 12.")
a.append("**Informes generales Q4 2022 y Q2 2024 – Q1 2025** no están publicados en la página de transparencia. Q4 2022 se reconstruye solo "
         "con los totales citados en Q1 2023; entre julio 2024 y febrero 2025 hay un vacío.")
L += ["", "## 4. Anomalías de la fuente", ""] + [f"{i}. {t}" for i, t in enumerate(a, 1)]

cambios = [
    ("Reportes", "Q1 2022 – Q1 2023: reportes por formulario web (no-spam) + reportes de spam de un clic por separado. "
     "Q2 2023: aparecen 'Online Reports' (web) y 'In-App Reports'. Q3 2023 – H1 2024: solo reportes en la app, donde "
     "'Platform Manipulation' incluye TODOS los reportes de spam.",
     "No comparar el volumen de reportes antes y después de Q2 2023: cambia el canal medido (≈ 150 mil frente a ≈ 12–29 millones)."),
    ("Base de la tasa de apelación", "2022–2023: % de *cuentas deshabilitadas* que apelaron. H1 2024: % de *cuentas sancionadas distintas* "
     "(incluye advertencias y suspensiones temporales, 3.568.821).",
     "El 1,85 % de H1 2024 no es comparable con el 10–22 % de 2022–2023."),
    ("Reversión", "2022 Q1–Q2: 'accounts reinstated'; 2022 Q3 – 2023: 'reinstated'; H1 2024: 'restored to pre-intervention status' "
     "(cuentas restauradas). 2026: 'intervenciones retiradas' (según el plan, sin verificar).",
     "La cifra 2026 (≈ 10,37 %) cuenta intervenciones, no cuentas: no compararla directamente con el 2–4,6 % de 2022–2024."),
    ("Spam", "Los CSV generales NO incluyen spam; las cuentas de spam deshabilitadas se publican solo en el texto del PDF. "
     "'Platform Manipulation' en las tablas es solo la parte no-spam.",
     "Spam y no-spam se tratan por separado en todo el análisis."),
    ("Periodicidad", "Trimestral 2022–2023, semestral H1 2024, anual DSA (UE) y anual 2026 (mar 2025 – mar 2026).",
     "Normalizar a tasa semanal antes de comparar (04_normalizacion.py)."),
    ("DSA 2024 vs DSA 2025", "2024 publica 'exactitud' y 'tasa de error'; 2025 publica exactitud, precisión y recall. El periodo 2024 empieza el 17-02-2024.",
     "La tasa de error 2024 (6,65 %) y la precisión 2025 (55,1 %) miden cosas distintas; no restarlas ni compararlas como serie."),
]
L += ["", "## 5. Cambios de definición entre informes", "", "| Métrica | Cambio | Consecuencia para el análisis |", "|---|---|---|"]
L += [f"| {m} | {c} | {k} |" for m, c, k in cambios]

(PROC / "validacion.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:20]))
print(f"... diferencias en sumas: {len(dif)} de {len(sumas)}")
print(dif.to_string())
