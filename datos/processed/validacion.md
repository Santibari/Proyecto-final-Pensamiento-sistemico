# Validación de cifras – Informes de transparencia de Discord

Generado por `scripts/03_validacion.py`. Fuente: https://discord.com/safety-transparency

## 1. Cifras de control H1 2024

| Indicador | Control | Extraído | Resultado | Ubicación |
|---|---|---|---|---|
| Cuentas deshabilitadas totales | 35.813.609 | 35.813.609 | Coincide | p. 5 (suma spam + no-spam) |
| Cuentas deshabilitadas por spam | 35.456.553 | 35.456.553 | Coincide | p. 5, p. 16 |
| Cuentas deshabilitadas no-spam | 357.056 | 357.056 | Coincide | p. 5; CSV |
| Servidores eliminados | 41.002 | 41.002 | Coincide | CSV; PDF |
| Reportes | 29.495.313 | 29.495.313 | Coincide | CSV; PDF |
| % de cuentas sancionadas que apelaron | 1,85 | 1,85 | Coincide | p. 9; CSV |
| Cuentas restauradas | 1.705 | 1.705 | Coincide | p. 9 |
| % restauradas de las que apelaron | 2,59 | 2,59 | Coincide | p. 9 |

> Nota: el 1,85 % de H1 2024 se calcula sobre 3.568.821 *cuentas sancionadas distintas* ("Distinct Accounts Actioned", incluye advertencias e intervenciones temporales), no sobre cuentas deshabilitadas. En 2022–2023 la base era *cuentas deshabilitadas*. Ver sección 5.

## 2. Cifras de control 2026 (marzo 2025 – marzo 2026)

| Indicador | Valor de control (sin verificar) | Resultado |
|---|---|---|
| Cuentas de spam deshabilitadas | 47.832.832 | PDF 2026 no descargado |
| Reportes no-spam | 34.304.587 | PDF 2026 no descargado |
| Reportes de spam | 26.174.231 | PDF 2026 no descargado |
| Cuentas que apelaron | 585.307 | PDF 2026 no descargado |
| Intervenciones retiradas | 60.686 | PDF 2026 no descargado |
| % intervenciones retiradas | 10.37% | PDF 2026 no descargado |

**DESCARTADAS:** `Discord-Transparency-Report-2026-Updated.pdf` no se pudo descargar (la red bloquea cdn.discordapp.com) y el equipo no lo encontró. Por decisión del equipo (14-11-2026) se trabaja solo con Q1 2022 – H1 2024 y DSA 2024–2025. Estas cifras NO se usan en el análisis ni en la calibración del modelo.

## 3. Suma de categorías frente al total publicado

Diferencias distintas de cero (las demás cuadran exactamente; detalle completo en `validacion_sumas.csv`):

| Periodo | Métrica | Total publicado | Suma categorías | Diferencia |
|---|---|---|---|---|
| — | — | — | — | Todas cuadran |

Combinaciones revisadas: 92; cuadran exactamente: 92.

## 4. Anomalías de la fuente

1. **Advertencias Q3 2022 = Q1 2023.** Los CSV de ambos informes traen exactamente las mismas cifras de advertencias (17.809 cuentas, 2.330 servidores). Probable error de copia en la fuente: no usar las advertencias de Q3 2022 sin revisar el PDF.
2. **NCMEC Q2 2022 = Q1 2022** (10.641 reportes de medios y 54 escalamientos en ambos CSV). No se usa en el modelo; se deja anotado.
3. **Q3 2023 – tabla 'Accounts Disabled' del CSV desalineada** una fila. Se corrigió con la tabla Appeals del mismo CSV, verificada contra el PDF (p. 13: seguridad infantil 128.153; p. 19: extremismo violento 8.300). Total 260.461 cuadra.
4. **Q3 2023 – Desinformación en Appeals:** 49 cuentas deshabilitadas y 596 apelaciones con 0,00 %. Inconsistente en la fuente; no se usa por categoría.
5. **Q2 2022 – tasa de reinstalación 0,60 %** (733 de 122.714 apelaciones; PDF p. 6 dice ".6%"). Es atípica frente al 2–4,6 % de los demás trimestres; es dato de la fuente.
6. **DSA 2025 – quejas internas:** total 334.874, pero confirmadas (552) + revertidas (86) = 638. El desglose no cubre el total; la tasa de reversión DSA 2025 NO se puede calcular con fiabilidad.
7. **DSA 2025 – medios automatizados:** las medidas 'solo automatizadas' de iniciativa propia (35.731) superan el total (30.740). Inconsistencia de la fuente.
8. **DSA 2024 – fila de ítems solo automatizados** con periodo 'YYYY-MM-DD' en el CSV (plantilla sin llenar); el valor 114.252 sí aparece en el PDF p. 12.
9. **Informes generales Q4 2022 y Q2 2024 – Q1 2025** no están publicados en la página de transparencia. Q4 2022 se reconstruye solo con los totales citados en Q1 2023; entre julio 2024 y febrero 2025 hay un vacío.

## 5. Cambios de definición entre informes

| Métrica | Cambio | Consecuencia para el análisis |
|---|---|---|
| Reportes | Q1 2022 – Q1 2023: reportes por formulario web (no-spam) + reportes de spam de un clic por separado. Q2 2023: aparecen 'Online Reports' (web) y 'In-App Reports'. Q3 2023 – H1 2024: solo reportes en la app, donde 'Platform Manipulation' incluye TODOS los reportes de spam. | No comparar el volumen de reportes antes y después de Q2 2023: cambia el canal medido (≈ 150 mil frente a ≈ 12–29 millones). |
| Base de la tasa de apelación | 2022–2023: % de *cuentas deshabilitadas* que apelaron. H1 2024: % de *cuentas sancionadas distintas* (incluye advertencias y suspensiones temporales, 3.568.821). | El 1,85 % de H1 2024 no es comparable con el 10–22 % de 2022–2023. |
| Reversión | 2022 Q1–Q2: 'accounts reinstated'; 2022 Q3 – 2023: 'reinstated'; H1 2024: 'restored to pre-intervention status' (cuentas restauradas). 2026: 'intervenciones retiradas' (según el plan, sin verificar). | La cifra 2026 (≈ 10,37 %) cuenta intervenciones, no cuentas: no compararla directamente con el 2–4,6 % de 2022–2024. |
| Spam | Los CSV generales NO incluyen spam; las cuentas de spam deshabilitadas se publican solo en el texto del PDF. 'Platform Manipulation' en las tablas es solo la parte no-spam. | Spam y no-spam se tratan por separado en todo el análisis. |
| Periodicidad | Trimestral 2022–2023, semestral H1 2024, anual DSA (UE) y anual 2026 (mar 2025 – mar 2026). | Normalizar a tasa semanal antes de comparar (04_normalizacion.py). |
| DSA 2024 vs DSA 2025 | 2024 publica 'exactitud' y 'tasa de error'; 2025 publica exactitud, precisión y recall. El periodo 2024 empieza el 17-02-2024. | La tasa de error 2024 (6,65 %) y la precisión 2025 (55,1 %) miden cosas distintas; no restarlas ni compararlas como serie. |
