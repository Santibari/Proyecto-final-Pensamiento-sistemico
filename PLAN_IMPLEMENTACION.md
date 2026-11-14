# Plan de implementación – Proyecto final PSO: Discord

> Instrucciones para Claude Code. Léelas completas antes de empezar.
> Proyecto: *Moderación automatizada de contenido mediante IA, falsos positivos y salud comunitaria en Discord*.
> Curso: Pensamiento Sistémico Organizacional 2026-2, Universidad de La Sabana. Entrega: domingo 15 de noviembre, 11:59 p. m.

---

## 0. Reglas generales

1. **Fuente única de datos:** la página de transparencia de Discord, https://discord.com/safety-transparency, con sus informes generales 2022–2026, los informes DSA (Unión Europea) y los ECA (Brasil). No uses datos de otras webs. Si un dato no está en esos informes, márcalo como **supuesto**.
   - **Dominios permitidos para descargar:** solo `discord.com` y `cdn.discordapp.com`, que son las plataformas oficiales de Discord. Prohibido usar blogs, sitios de estadísticas, Wikipedia, Kaggle, noticias, espejos o caché.
   - Antes de descargar, comprueba que el enlace aparezca publicado en https://discord.com/safety-transparency. Si un enlace redirige a otro dominio, no lo descargues y regístralo en la bitácora.
   - En `MANIFIESTO.csv` agrega una columna `dominio` para dejar constancia de que todo vino de Discord.
2. **No toques la carpeta del modelo de Vensim.** En esta fase no se crea ni se edita ningún `.mdl`.
3. **No redactes la interpretación de resultados del informe final.** El curso exige que la escriba el equipo, sin corrección de estilo. Tú entregas datos, tablas, gráficos y hallazgos descriptivos.
4. **Separa spam y no-spam** en todo el análisis. El modelo se centrará en el contenido dañino **no-spam**; el spam se analiza como contexto.
5. **Registra todo en la bitácora** (sección 5): cada descarga, consulta, extracción y decisión.
6. **Usa Python** para el tratamiento de datos: pandas, pdfplumber (o PyMuPDF), matplotlib, openpyxl y requests. Crea un `requirements.txt`.
7. **No inventes cifras.** Cada número debe poder rastrearse al informe, la página y la tabla de donde salió.

### Estructura de carpetas

```
<proyecto>/
├── modelo_vensim/      ← existe; NO tocar
├── bitacora/           ← existe; Claude Code escribe aquí su registro
└── datos/              ← la crea Claude Code
    ├── raw/            ← archivos descargados, sin modificar
    ├── interim/        ← textos y tablas extraídas de los PDF
    ├── processed/      ← CSV limpios y listos para usar
    ├── figuras/        ← gráficos PNG
    ├── scripts/        ← scripts Python numerados (01_descarga.py, 02_extraccion.py…)
    ├── requirements.txt
    ├── RESUMEN_DATOS.md
    └── PLANTEAMIENTO_MODELO.md
```

> Si las carpetas existentes tienen otro nombre (por ejemplo `modelo vensim` o `bitácora`), usa los nombres reales y no las renombres.

---

## FASE 1 – Tratamiento y análisis de datos (hacer ahora)

### 1.1 Descarga (`scripts/01_descarga.py`)

Descarga a `datos/raw/` todos los archivos listados en https://discord.com/safety-transparency. Primero lee la página para confirmar los enlaces vigentes. A la fecha eran estos:

| Informe | URL |
|---|---|
| General 2026 | https://cdn.discordapp.com/assets/transparency-reports/Discord-Transparency-Report-2026-Updated.pdf |
| TCO 2026 | https://cdn.discordapp.com/assets/transparency-reports/TCO-Report-2026.pdf |
| General H1 2024 | https://cdn.discordapp.com/assets/transparency-reports/Discord-Transparency-Report-H1-2024.zip |
| General Q1–Q4 2023 | …/Discord-Transparency-Report-Q1-2023.zip … Q4-2023.zip |
| General Q1–Q3 2022 | …/Discord-Transparency-Report-Q1-2022.zip … Q3-2022.zip |
| DSA 2024 | https://cdn.discordapp.com/assets/2024/Discord-DSA_Transparency_Report.zip |
| DSA 2025 | https://cdn.discordapp.com/assets/2025/Discord-DSA_Transparency_Report.July-2026.zip |
| ECA Brasil H1 2026 (EN) | https://cdn.discordapp.com/assets/eca-digital-transparency-reports/english-brazil-eca-report-september-2026.pdf |

- Descomprime los `.zip` en subcarpetas de `raw/` y conserva los originales.
- Genera `raw/MANIFIESTO.csv` con nombre de archivo, URL, fecha de descarga, tamaño y hash SHA-256.
- Si una descarga falla, regístrala en la bitácora, sigue con las demás y avísale al usuario al final.

### 1.2 Extracción (`scripts/02_extraccion.py`)

Extrae las tablas y cifras de cada informe a `interim/` y luego a un formato largo y ordenado:

`processed/discord_transparencia_largo.csv` con estas columnas:

| columna | ejemplo |
|---|---|
| informe | General H1 2024 |
| periodo_inicio / periodo_fin | 2024-01-01 / 2024-06-30 |
| semanas_periodo | 26 |
| metrica | cuentas_deshabilitadas |
| categoria | spam / no_spam / acoso / odio / … / total |
| valor | 35456553 |
| unidad | cuentas / reportes / servidores / % |
| pagina_fuente | 4 |
| nota | definición o advertencia |

Métricas que hay que buscar en cada informe (si existen):
- Cuentas deshabilitadas, totales y por categoría de política (spam y no-spam por separado).
- Servidores eliminados, por categoría.
- Advertencias e intervenciones temporales, tanto a cuentas como a servidores.
- Reportes recibidos, por categoría.
- Apelaciones: % o número de cuentas que apelaron, y cuentas restauradas o intervenciones retiradas (número y %).
- Detección proactiva frente a reactiva, si aparece.
- **DSA:** quejas o apelaciones de usuarios de la UE, decisiones revertidas, uso de medios automatizados para detectar y decidir, e **indicadores de precisión o tasas de error de los medios automatizados**. Este es el dato más valioso para estimar falsos positivos.
- **ECA:** solo como contexto (protección de menores en Brasil).

### 1.3 Validación (`scripts/03_validacion.py`)

1. Revisa que los totales cuadren con la suma de las categorías y anota las diferencias.
2. Compara con estas cifras de control:
   - H1 2024: 35.813.609 cuentas deshabilitadas (35.456.553 por spam y 357.056 no-spam), 41.002 servidores eliminados, 29.495.313 reportes, apelación del 1,85 % de las cuentas sancionadas, 1.705 cuentas restauradas (2,59 % de las que apelaron).
   - 2026 (marzo 2025 – marzo 2026), cifras sin verificar: 47.832.832 cuentas de spam deshabilitadas, 34.304.587 reportes no-spam, 26.174.231 reportes de spam, 585.307 cuentas que apelaron, 60.686 intervenciones retiradas (10,37 %). **Confírmalas contra el PDF** y anota si coinciden.
3. **Cambios de definición:** documenta cuándo cambia una métrica, por ejemplo "cuentas restauradas" (2024) frente a "intervenciones retiradas" (2026). No compares directamente métricas con definiciones distintas sin advertirlo.
4. Guarda el resultado en `processed/validacion.md`.

### 1.4 Normalización (`scripts/04_normalizacion.py`)

- La periodicidad cambia: trimestral en 2022–2023, semestral en 2024 y anual en 2026. Convierte todo a **tasa semanal** (valor ÷ semanas del periodo), porque el modelo usará la semana como unidad de tiempo.
- Salida: `processed/serie_semanal.csv`, con una fila por informe y una columna por métrica normalizada.

### 1.5 Análisis (`scripts/05_analisis.py`)

Calcula y grafica en `figuras/`:
1. Serie 2022–2026 de cuentas deshabilitadas por semana, con spam y no-spam en curvas separadas.
2. Serie de reportes por semana, spam y no-spam.
3. Composición del no-spam por categoría de política, en barras apiladas por periodo.
4. Tasa de apelación y tasa de reversión por periodo, marcando los cambios de definición.
5. Razones derivadas por periodo: sanciones por reporte, fracción spam/no-spam y reportes por cuenta sancionada.
6. DSA: proporción de decisiones automatizadas y manuales, y los indicadores de error de los sistemas automatizados.

Tabla resumen: `processed/indicadores_clave.csv`, con indicador, valor, periodo, fórmula, informe y página.

Usa gráficos simples y legibles, con título, ejes con unidades y la fuente en el pie ("Fuente: Discord Transparency Report …").

### 1.6 Resumen de datos (`RESUMEN_DATOS.md`)

Debe responder, de forma descriptiva y con cifras:
- Qué datos existen, para qué periodos y con qué vacíos.
- Cómo evolucionaron las sanciones, los reportes y las apelaciones entre 2022 y 2026.
- Qué evidencia hay de falsos positivos: reversión de apelaciones e indicadores DSA.
- Limitaciones: fuente única escrita por la propia empresa, cambios de definición, periodicidad irregular y falsos positivos no apelados.

No escribas conclusiones interpretativas para el informe final; eso le corresponde al equipo.

---

## FASE 1B – Planteamiento del modelo con base en los datos (hacer ahora, sin Vensim)

Crea `datos/PLANTEAMIENTO_MODELO.md`, que el equipo usará después para construir el modelo en Vensim.

### Contenido obligatorio

1. **Delimitación:** una comunidad representativa de 100.000 usuarios, contenido dañino **no-spam** y el spam como contexto.
2. **Unidad de tiempo:** semana. Justificación: la confianza y el agotamiento de moderadores cambian en semanas, y los datos se normalizaron a tasas semanales. Horizonte: 104 semanas (mínimo exigido: 70). TIME STEP = 0,25.
3. **Variables propuestas** (ajústalas según los datos):
   - **Niveles:** Usuarios activos, Cola de revisión, Moderadores, Confianza de usuarios.
   - **Flujos:** Nuevos usuarios, Abandono, Entrada a revisión, Revisiones resueltas, Incorporación de moderadores, Renuncias, Cambio en confianza.
   - **Auxiliares:** Mensajes publicados, Contenido dañino no-spam, Contenido legítimo, Verdaderos positivos, Falsos positivos, Falsos negativos, Apelaciones, Reportes, Capacidad de revisión, Carga relativa, Confianza objetivo.
   - **Constantes:** Sensibilidad del filtro (palanca de política), Tasa base de falsos positivos, Fracción que apela, Fracción reportada, Productividad de moderadores, Tiempo de ajuste de confianza, entre otras.
4. **Tabla de parámetros:** variable · valor · unidad · **tipo (DATO o SUPUESTO)** · fórmula de cálculo · informe y página. Usa los indicadores de la fase 1. Mínimo:
   - Fracción que apela ← tasa de apelación de los informes.
   - Fracción de apelaciones con error confirmado ← tasa de reversión (≈ 0,10 en 2026, sin verificar).
   - Tasa base de falsos positivos ← indicadores DSA si existen; si no, calibrarla para que las apelaciones aceptadas den ≈ 10 %.
   - Relación reportes/sanciones no-spam ← series normalizadas.
5. **Ecuaciones propuestas con unidades**, en sintaxis de Vensim, para cada variable. Que sean coherentes en unidades, para que pasen Units Check.
6. **Diagrama causal en texto:** relaciones con polaridad (+/−) y ciclos identificados:
   - R1 crecimiento de usuarios; B1 daño visible; B2 falsos positivos; R2 espiral de agotamiento de moderadores; B3 voluntariado.
7. **Arquetipos candidatos:** "Soluciones que fallan" (subir la sensibilidad del filtro) y "Límites al crecimiento".
8. **Objetivos de calibración y validación:** qué comportamiento real debe reproducir el modelo, por ejemplo la tasa de reversión ≈ 10 % y la proporción reportes/sanciones.
9. **Escenarios para la propuesta de mejora**, solo planteados: sensibilidad 0,7 frente a 0,9; sistema de dos umbrales con revisión humana en la zona gris; triage asistido por IA (más productividad); sensibilidad adaptativa a la carga.
10. **Supuestos y limitaciones**, explícitos, cada uno con su justificación.

---

## FASE 2 – Modelado en Vensim (posterior, fase aparte; NO hacer ahora)

La hace el equipo en `modelo_vensim/` a partir de `PLANTEAMIENTO_MODELO.md`: modelo actual y modelo con mejora, Check Model y Units Check sin errores, y simulación de 104 semanas.

---

## FASE 3 – Simulación animada estilo NetLogo con PySD (posterior, fase aparte; NO hacer ahora)

Solo empieza cuando exista el `.mdl` validado de la fase 2.

### Objetivo
Una página web que se vea y se use como NetLogo: dinámica de sistemas con **agentes animados**, conectada al modelo de Vensim mediante PySD.

### Arquitectura
- **Motor:** PySD carga `modelo_vensim/<modelo>.mdl` y simula con los parámetros que el usuario elige. Vensim sigue siendo el modelo oficial; PySD solo lo ejecuta.
- **Backend:** FastAPI con un endpoint `POST /simular` que recibe los parámetros (sensibilidad, productividad, etc.) y devuelve las series de tiempo en JSON.
- **Frontend:** HTML + JavaScript (canvas o p5.js) en un solo proyecto `simulacion/`.

### Diseño tipo NetLogo
- **Panel izquierdo (Interface):** botones `setup`, `go` (continuo) y `go once`; sliders para Sensibilidad del filtro, Productividad, Tasa de voluntariado, etc.; selector "modelo actual / modelo con mejora"; monitores numéricos (Usuarios, Moderadores, Confianza, Cola).
- **Centro (World view):** cuadrícula de "parches" que representan servidores.
  - **Usuarios:** agentes en forma de persona que se mueven entre servidores. 1 agente = N usuarios del modelo (escala configurable). Entran por un borde y salen por otro según los flujos de Nuevos usuarios y Abandono.
  - **Mensajes:** partículas que cruzan una "compuerta" de filtro de IA. Verde = legítimo que pasa, rojo = dañino bloqueado, naranja = falso positivo (legítimo bloqueado), rojo que pasa = falso negativo.
  - **Moderadores:** agentes con escudo junto a una cola visual de casos; se ponen de color rojo a medida que aumenta la carga relativa y se van cuando renuncian.
  - El color de fondo de cada servidor refleja la confianza de los usuarios.
- **Panel derecho (Plots):** gráficos que se actualizan en vivo (Usuarios, Confianza, Cola de revisión, Moderadores, FP/FN).
- Al cambiar un slider se re-simula desde el paso actual, y las curvas y la animación cambian en tiempo real. Esto sirve para el "cambio de escenario" de la sustentación.

### Entregable de la fase 3
`simulacion/` con README de instalación (`pip install pysd fastapi uvicorn`) y ejecución (`uvicorn app:app`), más una captura o GIF de la simulación.

---

## 5. Bitácora (obligatoria en todas las fases)

Escribe en `bitacora/registro_ia_AAAA-MM-DD.md`, con la sesión marcada como **"Uso de IA – Claude Code"**. Usa una fila por acción relevante:

| Fecha y hora | Consulta o acción | Herramienta | Información obtenida | Decisión (acepta / descarta / ajusta) | Justificación |
|---|---|---|---|---|---|

Incluye también:
- Las descargas fallidas y qué se hizo.
- Las cifras que no coincidieron con las de control.
- Los supuestos introducidos y por qué.
- Los ajustes frente al plan de aprendizaje original (por ejemplo: "no hubo encuesta de percepción por falta de tiempo; se usa la tasa de reversión de apelaciones como medida indirecta").

---

## 6. Criterios de terminado (fase 1 y 1B)

- [ ] `datos/` creada con la estructura indicada y `requirements.txt`.
- [ ] Todos los informes descargados, con manifiesto y hash (o fallos registrados).
- [ ] `discord_transparencia_largo.csv` con cada cifra rastreable a informe y página.
- [ ] `validacion.md` con la verificación de las cifras de control y los cambios de definición.
- [ ] `serie_semanal.csv` e `indicadores_clave.csv`.
- [ ] Gráficos en `figuras/`, con spam y no-spam separados.
- [ ] `RESUMEN_DATOS.md`, descriptivo y sin interpretación final.
- [ ] `PLANTEAMIENTO_MODELO.md` con la tabla de parámetros marcada DATO/SUPUESTO, las ecuaciones con unidades, los ciclos y los escenarios.
- [ ] Bitácora con todas las acciones registradas.
- [ ] Nada modificado en `modelo_vensim/`.
- [ ] Mensaje final al usuario: qué se logró, qué falló y qué falta verificar a mano.

**Prioridad por tiempo** (la entrega es mañana): 1.1 → 1.2 → 1.3 → 1B → 1.4 → 1.5 → 1.6. Si el tiempo no alcanza, el planteamiento del modelo (1B) va antes que los gráficos.
