"""04_normalizacion.py – Convierte las cifras a tasa semanal (valor ÷ semanas del periodo).

El modelo de Vensim usa la SEMANA como unidad de tiempo. La periodicidad de la fuente
cambia (trimestral 2022–2023, semestral H1 2024, anual DSA), así que todo se lleva a
"por semana". Los porcentajes no se normalizan (ya son razones).
Salida: processed/serie_semanal.csv (una fila por informe).
"""
from pathlib import Path

import sys
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROC = BASE / "processed"
df = pd.read_csv(PROC / "discord_transparencia_largo.csv")

# (columna de salida, métrica, categoría, ¿normalizar?)
COLUMNAS = [
    ("cuentas_deshabilitadas_spam_sem", "cuentas_deshabilitadas", "spam", True),
    ("cuentas_deshabilitadas_no_spam_sem", "cuentas_deshabilitadas", "total_no_spam", True),
    ("servidores_eliminados_no_spam_sem", "servidores_eliminados", "total_no_spam", True),
    ("advertencias_cuentas_no_spam_sem", "advertencias_cuentas", "total_no_spam", True),
    ("reportes_formulario_web_no_spam_sem", "reportes_recibidos_formulario_web", "total_no_spam", True),
    ("reportes_spam_un_clic_sem", "reportes_spam_un_clic", "spam", True),
    ("reportes_en_app_total_sem", "reportes_recibidos_en_app", "total", True),
    ("reportes_en_app_manip_plataforma_sem", "reportes_recibidos_en_app", "manipulacion_plataforma", True),
    ("apelaciones_no_spam_sem", "apelaciones", "total_no_spam", True),
    ("apelaciones_concedidas_no_spam_sem", "apelaciones_concedidas", "total_no_spam", True),
    ("pct_cuentas_que_apelan", "pct_cuentas_que_apelan", "total_no_spam", False),
    ("pct_apelaciones_concedidas", "pct_apelaciones_concedidas", "total_no_spam", False),
    ("pct_spam_deshabilitado_proactivo", "pct_spam_deshabilitado_proactivo", "spam", False),
    ("dsa_quejas_internas_sem", "dsa_quejas_internas", "total", True),
    ("dsa_quejas_revertidas_sem", "dsa_quejas_decision_revertida", "total", True),
]

meta = df.groupby("clave_informe")[["informe", "periodo_inicio", "periodo_fin", "semanas_periodo"]].first()
out = meta.copy()
for col, met, cat, norm in COLUMNAS:
    s = df[(df.metrica == met) & (df.categoria == cat)].set_index("clave_informe")["valor"]
    out[col] = (s / meta["semanas_periodo"]).round(2) if norm else s

# Reportes en app sin la categoría que contiene el spam (aproximación de reportes no-spam)
out["reportes_en_app_sin_manip_plataforma_sem"] = (out["reportes_en_app_total_sem"] - out["reportes_en_app_manip_plataforma_sem"]).round(2)
out["nota"] = ""
out.loc[["Q4-2021", "Q4-2022"], "nota"] = "Solo totales citados en el informe del trimestre siguiente"
out.loc["H1-2024", "nota"] = "pct_cuentas_que_apelan con base 'cuentas sancionadas distintas' (no comparable con 2022–2023)"
out.loc[["Q2-2023", "Q3-2023", "Q4-2023", "H1-2024"], "nota"] += "; reportes en app: 'manipulación de plataforma' incluye todo el spam"
out.loc[["DSA-2024", "DSA-2025"], "nota"] = "Solo UE; spam y no-spam mezclados"
out = out.sort_values("periodo_inicio").reset_index()
out.to_csv(PROC / "serie_semanal.csv", index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250)
print(out.drop(columns=["informe", "nota"]).T.to_string())
