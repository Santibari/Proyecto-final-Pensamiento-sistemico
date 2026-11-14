"""05_analisis.py – Indicadores clave y gráficos descriptivos.

Salidas:
  - processed/indicadores_clave.csv  (indicador, valor, periodo, fórmula, informe, página)
  - figuras/01…06_*.png
Spam y no-spam van siempre en paneles separados (escalas ~100× distintas; sin doble eje).
"""
from pathlib import Path

import sys
sys.stdout.reconfigure(encoding="utf-8")
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")
BASE = Path(__file__).resolve().parents[1]
PROC, FIG = BASE / "processed", BASE / "figuras"
FIG.mkdir(exist_ok=True)

largo = pd.read_csv(PROC / "discord_transparencia_largo.csv")
sem = pd.read_csv(PROC / "serie_semanal.csv", parse_dates=["periodo_inicio", "periodo_fin"])
gen = sem[~sem.clave_informe.str.startswith("DSA")].copy()
gen["medio"] = gen.periodo_inicio + (gen.periodo_fin - gen.periodo_inicio) / 2

# Paleta categórica validada (orden fijo) + tinta de texto
AZUL, NARANJA, AQUA, AMARILLO, MAGENTA, VERDE, VIOLETA, ROJO = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
GRIS, TINTA, TINTA2 = "#b5b4ad", "#0b0b0b", "#52514e"
plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": "#d6d5cf", "axes.labelcolor": TINTA2, "xtick.color": TINTA2,
    "ytick.color": TINTA2, "axes.grid": True, "grid.color": "#ebeae6", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb", "axes.titlesize": 11, "axes.axisbelow": True, "axes.titleweight": "bold",
})
MILES = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", "."))


def pie(fig, texto):
    fig.text(0.01, 0.01, texto, fontsize=8, color=TINTA2, ha="left", va="bottom")


def guardar(fig, nombre):
    fig.savefig(FIG / nombre, dpi=150, bbox_inches="tight")
    plt.close(fig)


def linea(ax, x, y, color, etiqueta):
    m = y.notna()
    ax.plot(x[m], y[m], color=color, lw=2, marker="o", ms=6, mec="#fcfcfb", mew=2, label=etiqueta)


def fechas(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))


FUENTE_GEN = "Fuente: Discord Transparency Report Q1 2022 – H1 2024 (Q4 2021 y Q4 2022: cifras citadas en el informe siguiente)"

# ---------------------------------------------------------------- 1. cuentas deshabilitadas
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
linea(a1, gen.medio, gen.cuentas_deshabilitadas_spam_sem, NARANJA, "Spam")
a1.set_title("Cuentas deshabilitadas por semana – SPAM")
linea(a2, gen.medio, gen.cuentas_deshabilitadas_no_spam_sem, AZUL, "No-spam")
a2.set_title("Cuentas deshabilitadas por semana – NO-SPAM (foco del modelo)")
for a in (a1, a2):
    a.set_ylabel("cuentas / semana")
    a.yaxis.set_major_formatter(MILES)
    a.set_ylim(bottom=0)
fechas(a2)
a2.set_xlabel("Periodo del informe (punto medio)")
fig.suptitle("Discord: cuentas deshabilitadas, 2021–2024", fontweight="bold")
pie(fig, FUENTE_GEN)
fig.tight_layout(rect=(0, 0.03, 1, 1))
guardar(fig, "01_cuentas_deshabilitadas_semana.png")

# ---------------------------------------------------------------- 2. reportes
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
linea(a1, gen.medio, gen.reportes_spam_un_clic_sem, NARANJA, "Spam – reporte de un clic (2022–Q1 2023)")
linea(a1, gen.medio, gen.reportes_en_app_manip_plataforma_sem, AMARILLO, "En app: manipulación de plataforma, incluye spam (Q2 2023+)")
a1.set_title("Reportes por semana – SPAM")
linea(a2, gen.medio, gen.reportes_formulario_web_no_spam_sem, AZUL, "No-spam – formulario web (2022–Q2 2023)")
linea(a2, gen.medio, gen.reportes_en_app_sin_manip_plataforma_sem, AQUA, "No-spam – en app, sin manipulación de plataforma (Q2 2023+)")
a2.set_title("Reportes por semana – NO-SPAM")
for a in (a1, a2):
    a.set_ylabel("reportes / semana")
    a.yaxis.set_major_formatter(MILES)
    a.set_ylim(bottom=0)
    a.legend(frameon=False, fontsize=8, loc="upper left")
    a.axvline(pd.Timestamp("2023-04-01"), color=GRIS, lw=1, ls="--")
a2.text(pd.Timestamp("2023-04-10"), a2.get_ylim()[1] * 0.92, "cambio de canal medido", fontsize=8, color=TINTA2)
fechas(a2)
a2.set_xlabel("Periodo del informe (punto medio)")
fig.suptitle("Discord: reportes recibidos – la definición cambia en Q2 2023 (no comparar a través de la línea)", fontweight="bold", fontsize=10)
pie(fig, "Fuente: Discord Transparency Report Q1 2022 – H1 2024")
fig.tight_layout(rect=(0, 0.03, 1, 1))
guardar(fig, "02_reportes_semana.png")

# ---------------------------------------------------------------- 3. composición no-spam
cd = largo[(largo.metrica == "cuentas_deshabilitadas") & (largo.grupo == "no_spam") &
           (~largo.categoria.isin(["total_no_spam"])) & (~largo.clave_informe.isin(["Q4-2021", "Q4-2022"]))]
tab = cd.pivot_table(index="clave_informe", columns="categoria", values="valor", aggfunc="first").fillna(0)
orden = ["Q1-2022", "Q2-2022", "Q3-2022", "Q1-2023", "Q2-2023", "Q3-2023", "Q4-2023", "H1-2024"]
tab = tab.loc[orden]
pct = tab.div(tab.sum(axis=1), axis=0) * 100
top = pct.mean().sort_values(ascending=False).index[:5]
nombres = {"seguridad_infantil": "Seguridad infantil", "contenido_explotador_no_solicitado": "Contenido explotador / no solicitado",
           "actividades_ilegales_reguladas": "Actividades ilegales o reguladas", "acoso": "Acoso", "odio": "Conducta de odio",
           "practicas_enganosas": "Prácticas engañosas", "contenido_violento_grafico": "Contenido violento o gráfico",
           "extremismo_violento": "Extremismo violento", "autolesion": "Autolesión"}
comp = pct[top].copy()
comp["Otras"] = 100 - comp.sum(axis=1)
colores = [AZUL, NARANJA, AQUA, AMARILLO, MAGENTA][:len(top)] + [GRIS]
fig, ax = plt.subplots(figsize=(9, 5))
izq = pd.Series(0.0, index=comp.index)
for col, c in zip(comp.columns, colores):
    ax.barh(comp.index, comp[col], left=izq, color=c, edgecolor="#fcfcfb", linewidth=2, height=0.7,
            label=nombres.get(col, col))
    izq += comp[col]
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("% de cuentas no-spam deshabilitadas en el periodo")
ax.set_ylabel("Informe")
ax.set_title("Composición del contenido dañino no-spam por categoría de política (cuentas deshabilitadas)")
ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
ax.grid(axis="y", visible=False)
pie(fig, "Fuente: Discord Transparency Report Q1 2022 – H1 2024 (Q3 2023 corregido con la tabla Appeals; ver validacion.md)")
fig.tight_layout(rect=(0, 0.04, 1, 1))
guardar(fig, "03_composicion_no_spam.png")

# ---------------------------------------------------------------- 4. apelación y reversión
g = gen[gen.pct_cuentas_que_apelan.notna()]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
linea(a1, g.medio, g.pct_cuentas_que_apelan, AZUL, "% que apela")
a1.set_title("Tasa de apelación (no-spam)")
a1.set_ylabel("% de cuentas")
h1 = g[g.clave_informe == "H1-2024"]
a1.annotate("H1 2024: base = cuentas sancionadas\ndistintas (no comparable)", (h1.medio.iloc[0], h1.pct_cuentas_que_apelan.iloc[0]),
            xytext=(-170, 25), textcoords="offset points", fontsize=8, color=TINTA2,
            arrowprops=dict(arrowstyle="-", color=GRIS))
linea(a2, g.medio, g.pct_apelaciones_concedidas, NARANJA, "% de apelaciones concedidas")
a2.set_title("Tasa de reversión: cuentas restauradas / apelaciones (no-spam)")
a2.set_ylabel("% de apelaciones")
for a in (a1, a2):
    a.set_ylim(bottom=0)
fechas(a2)
a2.set_xlabel("Periodo del informe (punto medio)")
fig.suptitle("Discord: apelaciones y reversiones 2022–2024", fontweight="bold")
pie(fig, "Fuente: Discord Transparency Report Q1 2022 – H1 2024. La cifra 2026 ('intervenciones retiradas') tiene otra definición y no se incluye.")
fig.tight_layout(rect=(0, 0.03, 1, 1))
guardar(fig, "04_apelacion_reversion.png")

# ---------------------------------------------------------------- 5. razones derivadas
gen["frac_spam_deshabilitadas"] = 100 * gen.cuentas_deshabilitadas_spam_sem / (gen.cuentas_deshabilitadas_spam_sem + gen.cuentas_deshabilitadas_no_spam_sem)
gen["reportes_web_por_cuenta_no_spam"] = gen.reportes_formulario_web_no_spam_sem / gen.cuentas_deshabilitadas_no_spam_sem
gen["reportes_app_por_cuenta_no_spam"] = gen.reportes_en_app_sin_manip_plataforma_sem / gen.cuentas_deshabilitadas_no_spam_sem
acc = largo[(largo.metrica == "reportes_accionados_formulario_web") & (largo.categoria == "total_no_spam")].set_index("clave_informe").valor
rec = largo[(largo.metrica == "reportes_recibidos_formulario_web") & (largo.categoria == "total_no_spam")].set_index("clave_informe").valor
gen["pct_reportes_web_accionados"] = gen.clave_informe.map(100 * acc / rec)
fig, axs = plt.subplots(1, 3, figsize=(12, 4))
linea(axs[0], gen.medio, gen.frac_spam_deshabilitadas, NARANJA, "")
axs[0].set_title("Spam / total de cuentas deshabilitadas")
axs[0].set_ylabel("%")
axs[0].set_ylim(90, 100.5)
linea(axs[1], gen.medio, gen.reportes_web_por_cuenta_no_spam, AZUL, "formulario web")
linea(axs[1], gen.medio, gen.reportes_app_por_cuenta_no_spam, AQUA, "en app (sin manip. plataforma)")
axs[1].set_yscale("log")
axs[1].set_title("Reportes no-spam por cuenta deshabilitada")
axs[1].set_ylabel("reportes / cuenta (escala log)")
axs[1].legend(frameon=False, fontsize=8)
linea(axs[2], gen.medio, gen.pct_reportes_web_accionados, AZUL, "")
axs[2].set_title("Reportes web no-spam con acción")
axs[2].set_ylabel("% de reportes")
axs[2].set_ylim(bottom=0)
for a in axs:
    fechas(a)
    a.tick_params(axis="x", rotation=45)
fig.suptitle("Discord: razones derivadas por periodo", fontweight="bold")
pie(fig, "Fuente: Discord Transparency Report Q1 2022 – H1 2024")
fig.tight_layout(rect=(0, 0.04, 1, 1))
guardar(fig, "05_razones_derivadas.png")

# ---------------------------------------------------------------- 6. DSA
def dsa(clave, met, cat="total"):
    s = largo[(largo.clave_informe == clave) & (largo.metrica == met) & (largo.categoria == cat)].valor
    return None if s.empty else float(s.iloc[0])


fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5))
grupos = [("DSA 2024\n(total)", dsa("DSA-2024", "dsa_items_solo_automatizado"), dsa("DSA-2024", "dsa_items_no_automatizado")),
          ("DSA 2025\n(total)", dsa("DSA-2025", "dsa_items_solo_automatizado"), dsa("DSA-2025", "dsa_items_no_automatizado")),
          ("DSA 2025\n(avisos)", dsa("DSA-2025", "dsa_items_solo_automatizado", "avisos"), dsa("DSA-2025", "dsa_items_no_automatizado", "avisos"))]
for i, (n, aut, man) in enumerate(grupos):
    t = aut + man
    a1.bar(i, 100 * aut / t, color=AZUL, edgecolor="#fcfcfb", linewidth=2, width=0.6, label="Solo automatizado" if i == 0 else None)
    a1.bar(i, 100 * man / t, bottom=100 * aut / t, color=NARANJA, edgecolor="#fcfcfb", linewidth=2, width=0.6, label="Con intervención humana" if i == 0 else None)
    a1.text(i, 100 * aut / t / 2 if aut / t > 0.08 else 100 * aut / t + 3, f"{100 * aut / t:.1f} %", ha="center", fontsize=9, color=TINTA)
a1.set_xticks(range(len(grupos)), [g_[0] for g_ in grupos])
a1.set_ylabel("% de medidas / ítems")
a1.set_ylim(0, 100)
a1.set_title("Decisiones solo automatizadas vs. con revisión humana")
a1.grid(axis="x", visible=False)
a1.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
ind = [("2024 · exactitud", dsa("DSA-2024", "dsa_exactitud_automatizado")),
       ("2025 · exactitud", dsa("DSA-2025", "dsa_exactitud_automatizado")),
       ("2025 · precisión", dsa("DSA-2025", "dsa_precision_automatizado")),
       ("2025 · recall", dsa("DSA-2025", "dsa_sensibilidad_recall_automatizado")),
       ("2025 avisos · precisión", dsa("DSA-2025", "dsa_precision_automatizado", "avisos")),
       ("2025 avisos · recall", dsa("DSA-2025", "dsa_sensibilidad_recall_automatizado", "avisos"))]
y = range(len(ind))
a2.barh(list(y), [v for _, v in ind], color=[AZUL, AZUL, AQUA, VIOLETA, AQUA, VIOLETA], height=0.6, edgecolor="#fcfcfb", linewidth=2)
for i, (_, v) in enumerate(ind):
    a2.text(v + 1, i, f"{v:.1f} %".replace(".", ","), va="center", fontsize=9, color=TINTA)
a2.set_yticks(list(y), [n for n, _ in ind])
a2.invert_yaxis()
a2.set_xlim(0, 110)
a2.set_xlabel("%")
a2.set_title("Indicadores de los medios automatizados (UE)")
a2.grid(axis="y", visible=False)
fig.suptitle("Discord – informes DSA (UE): automatización y calidad de los sistemas automáticos", fontweight="bold")
pie(fig, "Fuente: Discord DSA Transparency Report 2024 (p. 12) y 2025 (p. 9; CSV '7. Automated Means'). Spam y no-spam mezclados; solo UE. "
         "2024 y 2025 usan métricas distintas.")
fig.tight_layout(rect=(0, 0.05, 1, 1))
guardar(fig, "06_dsa_automatizacion.png")

# ---------------------------------------------------------------- indicadores clave
def pag(clave, met, cat):
    s = largo[(largo.clave_informe == clave) & (largo.metrica == met) & (largo.categoria == cat)].pagina_fuente
    return "" if s.empty else str(s.iloc[0])


I = []


def ind_(nombre, valor, periodo, formula, informe, pagina, nota=""):
    I.append({"indicador": nombre, "valor": round(valor, 4) if valor is not None else None, "periodo": periodo,
              "formula": formula, "informe": informe, "pagina": pagina, "nota": nota})


for _, r in gen.iterrows():
    k = r.clave_informe
    if pd.notna(r.pct_cuentas_que_apelan):
        ind_("tasa_apelacion_no_spam_pct", r.pct_cuentas_que_apelan, k, "apelaciones / base de cuentas × 100", r.informe,
             pag(k, "pct_cuentas_que_apelan", "total_no_spam"),
             "Base = cuentas sancionadas distintas (no comparable)" if k == "H1-2024" else "Base = cuentas deshabilitadas no-spam")
        ind_("tasa_reversion_apelaciones_pct", r.pct_apelaciones_concedidas, k, "cuentas restauradas / apelaciones × 100", r.informe,
             pag(k, "pct_apelaciones_concedidas", "total_no_spam"), "Definición 'cuentas restauradas/reinstaladas'")
        ind_("restauradas_sobre_deshabilitadas_pct", 100 * r.apelaciones_concedidas_no_spam_sem / r.cuentas_deshabilitadas_no_spam_sem, k,
             "cuentas restauradas / cuentas deshabilitadas no-spam × 100", r.informe, "derivado",
             "Cota inferior de falsos positivos detectados (solo los que apelan y ganan)")
    if pd.notna(r.cuentas_deshabilitadas_spam_sem):
        ind_("cuentas_deshabilitadas_no_spam_semana", r.cuentas_deshabilitadas_no_spam_sem, k, "total no-spam / semanas", r.informe,
             pag(k, "cuentas_deshabilitadas", "total_no_spam"))
        ind_("cuentas_deshabilitadas_spam_semana", r.cuentas_deshabilitadas_spam_sem, k, "spam / semanas", r.informe,
             pag(k, "cuentas_deshabilitadas", "spam"))
        ind_("fraccion_spam_deshabilitadas_pct", r.frac_spam_deshabilitadas, k, "spam / (spam + no-spam) × 100", r.informe, "derivado")
    if pd.notna(r.reportes_web_por_cuenta_no_spam):
        ind_("reportes_web_por_cuenta_deshabilitada_no_spam", r.reportes_web_por_cuenta_no_spam, k,
             "reportes formulario web / cuentas deshabilitadas no-spam", r.informe, "derivado", "Canal web; spam excluido")
    if pd.notna(r.reportes_app_por_cuenta_no_spam):
        ind_("reportes_app_por_cuenta_deshabilitada_no_spam", r.reportes_app_por_cuenta_no_spam, k,
             "(reportes en app − manip. plataforma) / cuentas deshabilitadas no-spam", r.informe, "derivado",
             "Aproximación: excluir 'manip. plataforma' quita también su parte no-spam")
    if pd.notna(r.pct_reportes_web_accionados):
        ind_("reportes_web_accionados_pct", r.pct_reportes_web_accionados, k, "reportes accionados / recibidos × 100", r.informe, "CSV anexo")
for clave, nombre in (("DSA-2024", "DSA 2024 (UE)"), ("DSA-2025", "DSA 2025 (UE)")):
    q, rv = dsa(clave, "dsa_quejas_internas"), dsa(clave, "dsa_quejas_decision_revertida")
    ind_("dsa_reversion_quejas_pct", 100 * rv / q, clave, "quejas con decisión revertida / quejas × 100", nombre,
         pag(clave, "dsa_quejas_decision_revertida", "total"),
         "No fiable en 2025: el desglose solo cubre 638 de 334.874 quejas" if clave == "DSA-2025" else "UE; spam y no-spam mezclados")
    a, m = dsa(clave, "dsa_items_solo_automatizado"), dsa(clave, "dsa_items_no_automatizado")
    ind_("dsa_fraccion_solo_automatizada_pct", 100 * a / (a + m), clave, "solo automatizado / (solo automatizado + no automatizado) × 100",
         nombre, pag(clave, "dsa_items_solo_automatizado", "total"),
         "2025: inconsistente (iniciativa propia automatizada > total)" if clave == "DSA-2025" else "")
r0, c0 = dsa("DSA-2024", "dsa_restricciones_revertidas"), dsa("DSA-2024", "dsa_restricciones_confirmadas")
ind_("dsa_restricciones_revertidas_pct", 100 * r0 / (r0 + c0), "DSA-2024", "revertidas / (revertidas + confirmadas) × 100", "DSA 2024 (UE)", pag("DSA-2024", "dsa_restricciones_revertidas", "total"))
for cat in ("total", "quejas_internas", "iniciativa_propia"):
    ind_(f"dsa_tasa_error_automatizado_{cat}_pct", dsa("DSA-2024", "dsa_tasa_error_automatizado", cat), "DSA-2024", "dato publicado",
         "DSA 2024 (UE)", pag("DSA-2024", "dsa_tasa_error_automatizado", cat))
for cat in ("total", "iniciativa_propia", "avisos"):
    p_ = dsa("DSA-2025", "dsa_precision_automatizado", cat)
    rc = dsa("DSA-2025", "dsa_sensibilidad_recall_automatizado", cat)
    ind_(f"dsa_precision_{cat}_pct", p_, "DSA-2025", "dato publicado", "DSA 2025 (UE)", pag("DSA-2025", "dsa_precision_automatizado", cat))
    ind_(f"dsa_fraccion_falsos_positivos_entre_positivos_{cat}_pct", 100 - p_, "DSA-2025", "100 − precisión", "DSA 2025 (UE)", "derivado",
         "Falsos positivos / (VP + FP) en decisiones automatizadas")
    ind_(f"dsa_recall_{cat}_pct", rc, "DSA-2025", "dato publicado", "DSA 2025 (UE)", pag("DSA-2025", "dsa_sensibilidad_recall_automatizado", cat))
    ind_(f"dsa_fraccion_falsos_negativos_{cat}_pct", 100 - rc, "DSA-2025", "100 − recall", "DSA 2025 (UE)", "derivado",
         "Falsos negativos / (VP + FN)")

ind_df = pd.DataFrame(I)
ind_df.to_csv(PROC / "indicadores_clave.csv", index=False, encoding="utf-8-sig")
print(ind_df.to_string())
