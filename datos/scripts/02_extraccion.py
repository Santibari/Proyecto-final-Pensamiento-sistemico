"""02_extraccion.py – Extrae las cifras de los informes de transparencia de Discord.

Entradas (datos/raw/, sin modificar):
  - Informes generales Q1 2022 … H1 2024: CSV oficial de datos + PDF.
  - Informes DSA 2024 y 2025: CSV oficiales por sección + PDF.
  - Informe general 2026 (PDF), si está descargado.

Salidas:
  - interim/texto_pdf/*.txt            texto de cada PDF, separado por página
  - processed/discord_transparencia_largo.csv   formato largo, una cifra por fila

Criterios:
  - Las tablas por categoría salen del CSV oficial; para cada cifra se busca en qué
    página del PDF aparece escrita (columna pagina_fuente). Si no aparece en el texto
    del PDF se marca "CSV anexo".
  - El spam NO está en los CSV: sale del texto del PDF. Cada cifra de spam se verifica
    contra el texto (si no aparece, el script se detiene).
  - Se separa siempre spam / no_spam en la columna `grupo`.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import csv
import glob
import re
from datetime import date
from pathlib import Path

import pandas as pd
import pymupdf

BASE = Path(__file__).resolve().parents[1]
RAW, INTERIM, PROC = BASE / "raw", BASE / "interim", BASE / "processed"
TXT = INTERIM / "texto_pdf"

# ---------------------------------------------------------------- periodos
INFORMES = {
    # clave: (nombre, inicio, fin, carpeta raw)
    "Q4-2021": ("General Q4 2021 (citado)", date(2021, 10, 1), date(2021, 12, 31), None),
    "Q1-2022": ("General Q1 2022", date(2022, 1, 1), date(2022, 3, 31), "Discord-Transparency-Report-Q1-2022"),
    "Q2-2022": ("General Q2 2022", date(2022, 4, 1), date(2022, 6, 30), "Discord-Transparency-Report-Q2-2022"),
    "Q3-2022": ("General Q3 2022", date(2022, 7, 1), date(2022, 9, 30), "Discord-Transparency-Report-Q3-2022"),
    "Q4-2022": ("General Q4 2022 (citado)", date(2022, 10, 1), date(2022, 12, 31), None),
    "Q1-2023": ("General Q1 2023", date(2023, 1, 1), date(2023, 3, 31), "Discord-Transparency-Report-Q1-2023"),
    "Q2-2023": ("General Q2 2023", date(2023, 4, 1), date(2023, 6, 30), "Discord-Transparency-Report-Q2-2023"),
    "Q3-2023": ("General Q3 2023", date(2023, 7, 1), date(2023, 9, 30), "Discord-Transparency-Report-Q3-2023"),
    "Q4-2023": ("General Q4 2023", date(2023, 10, 1), date(2023, 12, 31), "Discord-Transparency-Report-Q4-2023"),
    "H1-2024": ("General H1 2024", date(2024, 1, 1), date(2024, 6, 30), "Discord-Transparency-Report-H1-2024"),
    "DSA-2024": ("DSA 2024 (UE)", date(2024, 2, 17), date(2024, 12, 31), "DSA-2024_Discord-DSA_Transparency_Report"),
    "DSA-2025": ("DSA 2025 (UE)", date(2025, 1, 1), date(2025, 12, 31), "DSA-2025_Discord-DSA_Transparency_Report.July-2026"),
}

CATEGORIAS = {
    "Child Safety": "seguridad_infantil",
    "Deceptive Practices": "practicas_enganosas",
    "Exploitative and Unsolicited Content": "contenido_explotador_no_solicitado",
    "Harassment and Bullying": "acoso",
    "Hateful Conduct": "odio",
    "Identity and Authenticity": "identidad_autenticidad",
    "Misinformation": "desinformacion",
    "Platform Manipulation": "manipulacion_plataforma",
    "Regulated or Illegal Activities": "actividades_ilegales_reguladas",
    "Self-Harm Concerns": "autolesion",
    "Violent and Graphic Content": "contenido_violento_grafico",
    "Violent Extremism": "extremismo_violento",
}

FILAS: list[dict] = []
PAGINAS: dict[str, list[str]] = {}  # clave informe -> texto por página


# ---------------------------------------------------------------- utilidades
def semanas(ini: date, fin: date) -> float:
    return round(((fin - ini).days + 1) / 7, 4)


def numero(txt: str):
    """'1,234' -> 1234 ; '12.5%' -> 12.5 ; '--', 'N/A' -> None."""
    t = str(txt).strip().replace("hours", "").replace("hr", "").strip()
    if t in ("", "--", "N/A", "n/a", "-"):
        return None
    t = t.replace(",", "").replace(" ", "").rstrip("%")
    try:
        v = float(t)
        return int(v) if v.is_integer() else v
    except ValueError:
        return None


def texto_pdfs() -> None:
    """Guarda el texto de cada PDF en interim/ y lo deja en memoria por informe."""
    TXT.mkdir(parents=True, exist_ok=True)
    for clave, (_, _, _, carpeta) in INFORMES.items():
        if not carpeta:
            continue
        pdfs = [p for p in glob.glob(str(RAW / carpeta / "**" / "*.pdf"), recursive=True) if "__MACOSX" not in p]
        if not pdfs:
            continue
        doc = pymupdf.open(pdfs[0])
        PAGINAS[clave] = [re.sub(r"\s+", " ", p.get_text()) for p in doc]
        salida = TXT / (Path(pdfs[0]).stem.replace(" ", "_") + ".txt")
        with open(salida, "w", encoding="utf-8") as f:
            for i, t in enumerate(PAGINAS[clave], 1):
                f.write(f"\n\n=== PAGINA {i} ===\n{t}")
    # informe general 2026 (puede faltar)
    pdf26 = RAW / "Discord-Transparency-Report-2026-Updated.pdf"
    if pdf26.exists():
        doc = pymupdf.open(pdf26)
        PAGINAS["G-2026"] = [re.sub(r"\s+", " ", p.get_text()) for p in doc]
        with open(TXT / "Discord-Transparency-Report-2026-Updated.txt", "w", encoding="utf-8") as f:
            for i, t in enumerate(PAGINAS["G-2026"], 1):
                f.write(f"\n\n=== PAGINA {i} ===\n{t}")


def buscar_pagina(clave: str, valor) -> str:
    """Páginas del PDF donde aparece el valor escrito con separador de miles."""
    if clave not in PAGINAS or valor is None:
        return ""
    if isinstance(valor, float):
        cand = [f"{valor:.2f}%", f"{valor}%"]
    else:
        cand = [f"{valor:,}"]
        if valor < 1000:  # números pequeños: demasiado ambiguos para buscar
            return ""
    pags = [str(i) for i, t in enumerate(PAGINAS[clave], 1)
            if any(re.search(r"(?<![\d,.])" + re.escape(c) + r"(?![\d,])", t) for c in cand)]
    return ",".join(pags[:4])


def agregar(clave, metrica, categoria, valor, unidad, grupo, fuente, pagina="", nota=""):
    nombre, ini, fin, _ = INFORMES[clave]
    if pagina == "":
        pagina = buscar_pagina(clave, valor) or "CSV anexo"
    FILAS.append({
        "informe": nombre, "clave_informe": clave,
        "periodo_inicio": ini.isoformat(), "periodo_fin": fin.isoformat(),
        "semanas_periodo": semanas(ini, fin),
        "metrica": metrica, "categoria": categoria, "grupo": grupo,
        "valor": valor, "unidad": unidad,
        "archivo_fuente": fuente, "pagina_fuente": pagina, "nota": nota,
    })


# ---------------------------------------------------------------- informes generales (CSV)
def secciones_csv(ruta: str) -> dict[str, list[list[str]]]:
    """Divide el CSV oficial en secciones {titulo: filas}."""
    filas = list(csv.reader(open(ruta, encoding="utf-8-sig")))
    out, actual = {}, None
    for i, r in enumerate(filas):
        nz = [c.strip() for c in r if c.strip()]
        if not nz:
            continue
        # título de sección: una sola celda seguida (tras blancos) de una fila de encabezado
        if len(nz) == 1 and not re.match(r"^[\d,\.%]+$", nz[0]) and nz[0] not in ("Total:", "Total"):
            siguientes = [f for f in filas[i + 1:i + 4] if any(c.strip() for c in f)]
            if siguientes and len([c for c in siguientes[0] if c.strip()]) > 1 or nz[0].endswith("Interventions"):
                actual = nz[0]
                out[actual] = []
                continue
        if actual:
            out[actual].append([c.strip() for c in r])
    return out


def filas_categoria(filas):
    """Devuelve (categoria_es, celdas) de las filas de datos y la fila total."""
    for r in filas:
        etiqueta = r[0]
        if etiqueta in CATEGORIAS:
            yield CATEGORIAS[etiqueta], r[1:]
        elif etiqueta.rstrip(":").lower() in ("total", "sum"):
            yield "total_no_spam", r[1:]


def procesar_general(clave: str) -> None:
    carpeta = INFORMES[clave][3]
    ruta = [p for p in glob.glob(str(RAW / carpeta / "*.csv"))][0]
    fuente = f"{carpeta}/{Path(ruta).name}"
    sec = secciones_csv(ruta)

    for titulo, filas in sec.items():
        t = titulo.lower()
        if t.startswith("warns") or "warnings" in t:
            for cat, c in filas_categoria(filas):
                agregar(clave, "advertencias_cuentas", cat, numero(c[0]), "cuentas", "no_spam", fuente)
                agregar(clave, "advertencias_servidores", cat, numero(c[1]), "servidores", "no_spam", fuente)
                agregar(clave, "advertencias_miembros_servidor", cat, numero(c[2]), "miembros", "no_spam", fuente)
        elif t == "accounts disabled":
            if clave == "Q3-2023":
                continue  # tabla desalineada en el CSV; se toma de la tabla de apelaciones (ver abajo)
            for cat, c in filas_categoria(filas):
                agregar(clave, "cuentas_deshabilitadas", cat, numero(c[0]), "cuentas", "no_spam", fuente)
        elif t == "servers removed":
            for cat, c in filas_categoria(filas):
                vals = [numero(x) for x in c if x]
                if len(vals) >= 3:  # proactivo / reactivo / total (2022–2023)
                    agregar(clave, "servidores_eliminados_proactivo", cat, vals[0], "servidores", "no_spam", fuente)
                    agregar(clave, "servidores_eliminados_reactivo", cat, vals[1], "servidores", "no_spam", fuente)
                    agregar(clave, "servidores_eliminados", cat, vals[2], "servidores", "no_spam", fuente)
                elif vals:
                    agregar(clave, "servidores_eliminados", cat, vals[0], "servidores", "no_spam", fuente)
        elif t == "appeals":
            enc = [x.lower() for x in filas[0]] if filas and filas[0][0].lower().endswith("category") else None
            base = "cuentas_sancionadas_base_apelacion" if clave == "H1-2024" else "cuentas_deshabilitadas_base_apelacion"
            nota_base = ("H1 2024: base = 'Distinct Accounts Actioned' (incluye advertencias e intervenciones "
                         "temporales, no solo cuentas deshabilitadas)") if clave == "H1-2024" else \
                        "Base = cuentas deshabilitadas no-spam del periodo"
            for cat, c in filas_categoria(filas):
                agregar(clave, base, cat, numero(c[0]), "cuentas", "no_spam", fuente, nota=nota_base)
                agregar(clave, "apelaciones", cat, numero(c[1]), "apelaciones", "no_spam", fuente)
                agregar(clave, "pct_cuentas_que_apelan", cat, numero(c[2]), "%", "no_spam", fuente)
                agregar(clave, "apelaciones_concedidas", cat, numero(c[3]), "cuentas", "no_spam", fuente,
                        nota="Cuentas restauradas/reinstaladas tras apelación (definición 2022–2024)")
                agregar(clave, "pct_apelaciones_concedidas", cat, numero(c[4]), "%", "no_spam", fuente)
                if len(c) > 5 and c[5]:
                    agregar(clave, "pct_cuentas_desbaneadas", cat, numero(c[5]), "%", "no_spam", fuente)
                if clave == "Q3-2023" and cat != "total_no_spam":
                    agregar(clave, "cuentas_deshabilitadas", cat, numero(c[0]), "cuentas", "no_spam", fuente,
                            nota="Tomado de la columna 'Accounts Disabled' de la tabla Appeals: la tabla "
                                 "'Accounts Disabled' del CSV está corrida una fila (verificado en PDF p. 13 y p. 19)")
            if clave == "Q3-2023":
                agregar(clave, "cuentas_deshabilitadas", "total_no_spam", 260461, "cuentas", "no_spam", fuente)
        elif "reports" in t:
            canal = {"online reports": "formulario_web", "in-app reports": "en_app"}.get(t, "formulario_web")
            if clave in ("Q1-2022", "Q2-2022", "Q3-2022", "Q1-2023"):
                canal = "formulario_web"
            if clave == "H1-2024":
                canal = "en_app"
            for cat, c in filas_categoria(filas):
                v = numero(c[0])
                grupo = "no_spam" if canal == "formulario_web" else (
                    "mixto" if cat in ("manipulacion_plataforma", "total_no_spam") else "no_spam")
                cat_out = "total" if (cat == "total_no_spam" and grupo == "mixto") else cat
                nota = ("Reportes por formulario web; el spam se reporta aparte (reporte de un clic)"
                        if canal == "formulario_web" else
                        "Reportes en la app; 'Platform Manipulation' incluye TODOS los reportes de spam")
                agregar(clave, f"reportes_recibidos_{canal}", cat_out, v, "reportes", grupo, fuente, nota=nota)
                if len(c) > 1 and numero(c[1]) is not None and canal == "formulario_web" and "%" not in c[1]:
                    agregar(clave, f"reportes_accionados_{canal}", cat_out, numero(c[1]), "reportes", grupo, fuente)


# ---------------------------------------------------------------- spam y otras cifras del texto PDF
# (clave_informe_dueño_del_pdf, clave_periodo, metrica, categoria, valor, unidad, grupo, nota)
CIFRAS_TEXTO = [
    ("Q1-2022", "Q4-2021", "cuentas_deshabilitadas", "total_no_spam", 1127220, "cuentas", "no_spam", "Citado como trimestre anterior en el informe Q1 2022"),
    ("Q1-2022", "Q4-2021", "cuentas_deshabilitadas", "spam", 19794949, "cuentas", "spam", "Citado como trimestre anterior en el informe Q1 2022"),
    ("Q1-2022", "Q1-2022", "cuentas_deshabilitadas", "spam", 26017742, "cuentas", "spam", ""),
    ("Q1-2022", "Q1-2022", "reportes_spam_un_clic", "spam", 21200699, "reportes", "spam", "Reportes de spam de un clic"),
    ("Q1-2022", "Q1-2022", "cuentas_unicas_reportadas_spam", "spam", 11011054, "cuentas", "spam", ""),
    ("Q2-2022", "Q2-2022", "cuentas_deshabilitadas", "spam", 27733948, "cuentas", "spam", ""),
    ("Q2-2022", "Q2-2022", "reportes_spam_un_clic", "spam", 14132392, "reportes", "spam", "Reportes de spam de un clic"),
    ("Q2-2022", "Q2-2022", "cuentas_unicas_reportadas_spam", "spam", 7785111, "cuentas", "spam", ""),
    ("Q3-2022", "Q3-2022", "cuentas_deshabilitadas", "spam", 50510769, "cuentas", "spam", ""),
    ("Q3-2022", "Q3-2022", "reportes_spam_un_clic", "spam", 8685638, "reportes", "spam", "Reportes de spam de un clic"),
    ("Q3-2022", "Q3-2022", "cuentas_unicas_reportadas_spam", "spam", 4818261, "cuentas", "spam", ""),
    ("Q1-2023", "Q4-2022", "cuentas_deshabilitadas", "total_no_spam", 153883, "cuentas", "no_spam", "Citado como trimestre anterior en el informe Q1 2023 (el informe Q4 2022 no está en la página)"),
    ("Q1-2023", "Q4-2022", "cuentas_deshabilitadas", "spam", 36825143, "cuentas", "spam", "Citado como trimestre anterior en el informe Q1 2023 (el informe Q4 2022 no está en la página)"),
    ("Q1-2023", "Q1-2023", "cuentas_deshabilitadas", "spam", 10693885, "cuentas", "spam", ""),
    ("Q1-2023", "Q1-2023", "reportes_spam_un_clic", "spam", 6023898, "reportes", "spam", "Reportes de spam"),
    ("Q1-2023", "Q1-2023", "cuentas_unicas_reportadas_spam", "spam", 3090654, "cuentas", "spam", ""),
    ("Q2-2023", "Q2-2023", "cuentas_deshabilitadas", "spam", 7971335, "cuentas", "spam", ""),
    ("Q3-2023", "Q3-2023", "cuentas_deshabilitadas", "spam", 12845746, "cuentas", "spam", ""),
    ("Q4-2023", "Q4-2023", "cuentas_deshabilitadas", "spam", 32973473, "cuentas", "spam", ""),
    ("H1-2024", "H1-2024", "cuentas_deshabilitadas", "spam", 35456553, "cuentas", "spam", ""),
]

# Porcentaje de cuentas de spam deshabilitadas de forma proactiva (frase en el PDF)
PROACTIVO_SPAM = {"Q1-2022": 90, "Q2-2022": 90, "Q3-2022": 90, "Q1-2023": 99, "Q2-2023": 99, "Q3-2023": 99, "Q4-2023": 99}


def procesar_texto() -> None:
    for dueno, periodo, met, cat, val, uni, grupo, nota in CIFRAS_TEXTO:
        pag = buscar_pagina(dueno, val)
        if not pag:
            raise SystemExit(f"ERROR: {val:,} no aparece en el PDF de {dueno}")
        nombre_pdf = INFORMES[dueno][0]
        agregar(periodo, met, cat, val, uni, grupo, f"PDF {nombre_pdf} (texto)", pagina=pag, nota=nota)
    for clave, pct in PROACTIVO_SPAM.items():
        pags = [str(i) for i, t in enumerate(PAGINAS[clave], 1)
                if re.search(rf"{pct}% of accounts disabled for spam were disabled proactively", t)]
        if not pags:
            raise SystemExit(f"ERROR: no se encontró {pct}% proactivo spam en {clave}")
        agregar(clave, "pct_spam_deshabilitado_proactivo", "spam", pct, "%", "spam",
                f"PDF {INFORMES[clave][0]} (texto)", pagina=",".join(pags),
                nota="Deshabilitadas antes de recibir cualquier reporte de usuario")


# ---------------------------------------------------------------- DSA (UE)
def dsa_csv(clave: str, patron: str) -> tuple[list[dict], str]:
    ruta = [p for p in glob.glob(str(RAW / INFORMES[clave][3] / "**" / f"*{patron}*.csv"), recursive=True)
            if "__MACOSX" not in p][0]
    with open(ruta, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f)), f"{INFORMES[clave][3]}/{Path(ruta).name}"


def procesar_dsa() -> None:
    nota_dsa = "Solo usuarios/contenido de la UE; incluye spam y no-spam sin separar"
    # --- DSA 2024: sección 6 "Overall Figures"
    filas, fuente = dsa_csv("DSA-2024", "6. Overall")
    mapa = {
        ("Number of complaints submitted", "Total number"): ("dsa_quejas_internas", "quejas"),
        ("Number of complaints submitted", "Decisions upheld"): ("dsa_quejas_decision_confirmada", "quejas"),
        ("Number of complaints submitted", "Decisions reversed"): ("dsa_quejas_decision_revertida", "quejas"),
        ("Number of complaints submitted", "Median time (in hours)"): ("dsa_quejas_tiempo_mediano", "horas"),
    }
    for r in filas:
        ind, alc, val = r["Indicator"].strip(), r["Scope"].strip(), r["Value"]
        for (k_ind, k_alc), (met, uni) in mapa.items():
            if ind.startswith(k_ind) and alc == k_alc:
                agregar("DSA-2024", met, "total", numero(val), uni, "mixto", fuente, nota=nota_dsa)
        if r["Section"].startswith("Use of automated means"):
            sub = {"Total number": "total", "Internal complaints mechanism": "quejas_internas",
                   "Own-initiative": "iniciativa_propia", "NAM Total": "avisos"}.get(alc)
            if not sub or numero(val) is None:
                continue
            if ind.startswith("Number of items solely"):
                met, uni = "dsa_items_solo_automatizado", "items"
            elif ind.startswith("Number of items not"):
                met, uni = "dsa_items_no_automatizado", "items"
            elif ind.startswith("Accuracy rate"):
                met, uni = "dsa_exactitud_automatizado", "%"
            elif ind.startswith("Error rate"):
                met, uni = "dsa_tasa_error_automatizado", "%"
            else:
                continue
            nota = nota_dsa + ("; el periodo en el CSV figura como 'YYYY-MM-DD' en esta fila" if r["Reporting period"].startswith("YYYY") else "")
            agregar("DSA-2024", met, sub, numero(val), uni, "mixto", fuente, nota=nota)
    # --- DSA 2024: sección 7 "Appeals" (restricciones)
    filas, fuente = dsa_csv("DSA-2024", "7. Appeals")
    for r in filas:
        ind = r["Indicator"]
        met = ("dsa_restricciones_confirmadas" if "upheld" in ind else
               "dsa_restricciones_revertidas" if "reversed" in ind else
               "dsa_restricciones_nuevas_tras_queja" if "newly" in ind else None)
        if met:
            agregar("DSA-2024", met, "total", numero(r["Total number"]), "restricciones", "mixto", fuente, nota=nota_dsa)

    # --- DSA 2025: sección 6 "Appeals and Recidivism"
    filas, fuente = dsa_csv("DSA-2025", "6. Appeals")
    for r in filas[:6]:  # bloque general de quejas internas
        alc, val = r["Scope"], r["Value - NEW"]
        met = {"Total number": ("dsa_quejas_internas", "quejas"),
               "Decisions upheld": ("dsa_quejas_decision_confirmada", "quejas"),
               "Decisions reversed": ("dsa_quejas_decision_revertida", "quejas"),
               "Median time": ("dsa_quejas_tiempo_mediano", "horas")}.get(alc)
        if met and numero(val) is not None:
            agregar("DSA-2025", met[0], "total", numero(val), met[1], "mixto", fuente,
                    nota=nota_dsa + "; ADVERTENCIA: confirmadas + revertidas (638) no suman el total de quejas")
    # --- DSA 2025: sección 7 "Automated Means"
    filas, fuente = dsa_csv("DSA-2025", "7. Automated")
    for r in filas:
        ind, alc, val = r["Indicator"].strip(), r["Scope"].strip(), r["Value"]
        sub = {"Total number": "total", "Own-initiative": "iniciativa_propia", "NAM Total": "avisos"}.get(alc)
        if not sub or numero(val) is None:
            continue
        if "solely" in ind:
            met, uni = "dsa_items_solo_automatizado", "medidas"
        elif "not " in ind:
            met, uni = "dsa_items_no_automatizado", "medidas"
        elif ind.endswith("Accuracy"):
            met, uni = "dsa_exactitud_automatizado", "%"
        elif ind.endswith("Precision"):
            met, uni = "dsa_precision_automatizado", "%"
        elif ind.endswith("Recall"):
            met, uni = "dsa_sensibilidad_recall_automatizado", "%"
        else:
            continue
        agregar("DSA-2025", met, sub, numero(val), uni, "mixto", fuente, nota=nota_dsa)
    # --- DSA 2025: avisos (notices) totales
    filas, fuente = dsa_csv("DSA-2025", "4. Notices")
    tot = [r for r in filas if r["Category of illegal content"] == "TOTAL"][0]
    agregar("DSA-2025", "dsa_avisos_recibidos", "total", numero(tot["Number of notices received\n"]), "avisos", "mixto", fuente, nota=nota_dsa)
    agregar("DSA-2025", "dsa_items_moderados_por_aviso", "total", numero(tot["Number of Items Moderated"]), "items", "mixto", fuente, nota=nota_dsa)


# ---------------------------------------------------------------- principal
def main() -> None:
    PROC.mkdir(parents=True, exist_ok=True)
    texto_pdfs()
    for clave in ["Q1-2022", "Q2-2022", "Q3-2022", "Q1-2023", "Q2-2023", "Q3-2023", "Q4-2023", "H1-2024"]:
        procesar_general(clave)
    procesar_texto()
    procesar_dsa()
    df = pd.DataFrame(FILAS)
    df = df[df["valor"].notna()]
    df.to_csv(PROC / "discord_transparencia_largo.csv", index=False, encoding="utf-8-sig")
    print(f"Filas extraídas: {len(df)}")
    print(df.groupby(["clave_informe"]).size().to_string())
    print("\nGeneral 2026 en raw/:", "SÍ" if "G-2026" in PAGINAS else "NO (pendiente de descarga)")


if __name__ == "__main__":
    main()
