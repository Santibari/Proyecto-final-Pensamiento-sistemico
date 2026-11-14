# Moderación automatizada con IA en Discord – Proyecto final PSO

**Curso:** Pensamiento Sistémico Organizacional 2026-2, Universidad de La Sabana.
**Tema:** moderación automatizada de contenido mediante IA en Discord, sus falsos positivos y falsos negativos, y la salud de la comunidad.

El proyecto toma los informes de transparencia oficiales de Discord, los limpia y analiza, y con esos datos calibra un modelo de dinámica de sistemas en **Vensim**. El modelo tiene dos versiones: la situación actual y una propuesta de mejora. Además hay una **página web** que ejecuta esos mismos modelos y los muestra de forma visual.

```
Informes de Discord ──► datos/ (scripts 01–05) ──► calibración ──► Modelos Vensim/*.mdl ──► simulacion/ (página web)
     (fuente única)        limpieza y análisis                      modelo oficial           PySD + FastAPI
```

---

## 1. Qué hay en el repositorio

| Carpeta / archivo | Qué contiene |
|---|---|
| `Caso final PSO Jueves.pdf` | Enunciado y rúbrica del proyecto |
| `PLAN_IMPLEMENTACION.md` | Plan de trabajo por fases (1: datos, 1B: planteamiento, 2: Vensim, 3: simulación web) |
| `Bitacora/registro_ia_2026-11-14.md` | **Bitácora de uso de IA**: cada descarga, extracción, validación, supuesto, decisión y error, con hora y justificación (entregable del curso) |
| `datos/` | Datos, scripts de Python, resultados y documentos del modelo (sección 3) |
| `Modelos Vensim/` | **Los dos modelos oficiales** (sección 4) |
| `simulacion/` | Página web que ejecuta los modelos de Vensim (sección 5) |

Las carpetas `.claude/` (instrucciones y skills para Claude Code) y los archivos de caché (`_cache_pysd/`, `__pycache__/`) no se suben: están en `.gitignore`.

---

## 2. Requisitos

| Para | Se necesita |
|---|---|
| Abrir y simular los modelos | **Vensim PLE** 10 o más reciente (gratuito para uso académico) |
| Volver a correr el análisis de datos | Python 3.11+ y `pip install -r datos/requirements.txt` (pandas, PyMuPDF, matplotlib, openpyxl, requests) |
| Ejecutar la página web | Python 3.11+ y `pip install -r simulacion/requirements.txt` (pysd, fastapi, uvicorn, numpy) |

---

## 3. `datos/` – de los informes de Discord al modelo

**Regla del proyecto:** la única fuente es https://discord.com/safety-transparency (informes generales 2022–2024, DSA 2024–2025 de la UE). Lo que no está en los informes se marca **SUPUESTO**. Ninguna cifra se inventa: cada una lleva informe y página.

### Cómo funciona

Cinco scripts numerados que se ejecutan en orden. Cada uno lee lo que dejó el anterior.

| Script | Qué hace | Produce |
|---|---|---|
| `01_descarga.py` | Lee la página de transparencia, descarga los informes publicados (solo de `discord.com` y `cdn.discordapp.com`), descomprime los .zip y calcula el hash SHA-256 | `raw/` y `raw/MANIFIESTO.csv` |
| `02_extraccion.py` | Extrae las tablas de los CSV oficiales y el spam del texto de los PDF, y anota en qué página aparece cada cifra | `processed/discord_transparencia_largo.csv` (1.494 cifras) |
| `03_validacion.py` | Compara con las cifras de control y suma categorías contra los totales; documenta errores de la fuente y cambios de definición | `processed/validacion.md` |
| `04_normalizacion.py` | Convierte todo a **tasa semanal**, porque el modelo usa la semana como unidad | `processed/serie_semanal.csv` |
| `05_analisis.py` | Calcula los indicadores (apelación, reversión, precisión de la IA…) y hace los gráficos | `processed/indicadores_clave.csv`, `figuras/01…06` |
| `06_modelos_vensim.py` | Genera los dos `.mdl` de Vensim (ecuaciones y diagrama) | `Modelos Vensim/*.mdl` |
| `07_verificacion_modelos.py` | Simula los `.mdl` con un intérprete propio y revisa la calibración y el signo (+/−) de cada flecha | `processed/simulacion_*.csv`, `figuras/sim_*` |

> **Cuidado:** `06_modelos_vensim.py` **sobrescribe** los `.mdl`. Si el equipo ya editó los modelos en Vensim, no lo vuelva a ejecutar.

### Cómo ejecutar

Desde la carpeta `datos/`:

```bash
pip install -r requirements.txt
```
```bash
python scripts/01_descarga.py
```
```bash
python scripts/02_extraccion.py
```
```bash
python scripts/03_validacion.py
```
```bash
python scripts/04_normalizacion.py
```
```bash
python scripts/05_analisis.py
```
```bash
python scripts/07_verificacion_modelos.py
```

Si la red bloquea `cdn.discordapp.com` (pasó durante el proyecto), descargue los .zip a mano desde la página de transparencia, cópielos en `datos/raw/` y ejecute `01_descarga.py`: el script los verifica y los registra en el manifiesto.

### Documentos

| Archivo | Para qué sirve |
|---|---|
| `datos/RESUMEN_DATOS.md` | Qué datos hay, cómo evolucionaron 2022–2024, evidencia de falsos positivos y limitaciones (descriptivo) |
| `datos/MODELO_VENSIM.md` | **Explicación del modelo vigente**: las 50 variables una por una, ciclos, arquetipos, supuestos y validación |
| `datos/PLANTEAMIENTO_MODELO.md` | Planteamiento inicial y calibración (las secciones 4, 5 y 11 están superadas por `MODELO_VENSIM.md`) |
| `datos/processed/validacion.md` | Verificación de cifras, errores de la fuente y cambios de definición |

---

## 4. `Modelos Vensim/` – el modelo oficial

| Archivo | Contenido |
|---|---|
| `Discord_moderacion_actual.mdl` | Situación actual: 48 variables (6 niveles, 10 flujos, 12 auxiliares, 20 constantes), una sola vista, flechas con signo + o − |
| `Discord_moderacion_mejora.mdl` | Con mejora: 50 variables (filtro de IA adaptativo y triage asistido por IA) |
| `*.vdfx` | Resultados de corridas de Vensim (se regeneran al simular) |

### Cómo funciona el modelo

Una comunidad de 100.000 usuarios en la que un filtro de IA bloquea contenido:
- Acierta (**nocivo bloqueado**).
- Se equivoca con contenido legítimo (**bloqueos por error**, es decir, falsos positivos).
- Deja pasar contenido nocivo (**nocivo que se escapa**, es decir, falsos negativos).

Los usuarios apelan los bloqueos y denuncian lo que se escapa. Esas apelaciones y denuncias forman dos colas en paralelo que los moderadores voluntarios atienden con una capacidad limitada. Si la carga sube, los moderadores renuncian; si el daño o los bloqueos injustos suben, cae la confianza y la comunidad deja de crecer.

- **Calibrado con datos reales:**
  - Precisión de la IA 55,1 % y detección 97,3 % (DSA 2025).
  - Apelan el 15,5 % (2022–2023).
  - Se acepta el 2,39 % de las apelaciones (2022–2024).
  - Revisión en 57 horas (DSA 2024).
- **Contenido de clase:**
  - Niveles en serie y en paralelo.
  - `DELAY1`, `DELAY3`, `DELAY FIXED` y `SMOOTH`.
  - Ciclos de refuerzo y de balance.
  - Arquetipos: límites al crecimiento, desplazamiento de la carga y tragedia de los comunes.
- **Validación:** *Model is OK* y *Units are OK* en Vensim PLE 10.5.2. Las capturas están en `datos/figuras/evidencia_vensim_*.jpg`.

### Cómo ejecutar

1. Abra el `.mdl` en Vensim (File > Open Model).
2. Si el diagrama no se ve completo: View > Fit to Screen.
3. Model > Check Model y Model > Units Check.
4. Pulse **Simulate** (horizonte de 104 semanas, TIME STEP 0,25).
5. Para probar el arquetipo, cambie la constante *Sensibilidad del filtro IA* de 0.973 a 0.99 y vuelva a simular.

El detalle de cada variable está en `datos/MODELO_VENSIM.md`.

---

## 5. `simulacion/` – página web conectada a Vensim

### Cómo funciona

```
Modelos Vensim/*.mdl ──► PySD lo traduce a Python ──► FastAPI (app.py) lo simula ──► el navegador lo muestra (static/)
```

- La página **no tiene ecuaciones propias**: ejecuta los `.mdl` con PySD.
- Del `.mdl` también toma el **diagrama** (posiciones y signos de las flechas), las **unidades**, los **comentarios** y los **valores por defecto**.
- **Si cambian el modelo en Vensim y guardan,** el servidor lo detecta y lo vuelve a traducir. En la página basta con pulsar «Volver a leer los .mdl».
- **Si renombran una variable,** la página no la encuentra.

**Qué muestra la página:**
- Tres escenarios con un clic: situación actual, filtro endurecido a 0,99 y personalizado.
- El diagrama de Vensim animado, con ayudas al pasar el mouse.
- La comparación del modelo actual con el de mejora.
- Frases en lenguaje común, cada una al lado del dato real.
- Una ciudad 3D ilustrativa. No hay datos por país ni por servidor: los edificios son iguales y la página lo aclara.

### Cómo ejecutar

Desde la carpeta `simulacion/`:

```bash
pip install -r requirements.txt
```
```bash
uvicorn app:app --port 8000
```

Abra **http://localhost:8000** en el navegador. Funciona sin internet. Más detalles en `simulacion/README.md`.

---

## 6. Qué le corresponde al equipo

- **Redactar la interpretación de resultados, la comparación entre modelos y las conclusiones.** El curso exige que lo haga el equipo, sin corrección de estilo; la IA solo entregó datos, modelos, gráficos y hallazgos descriptivos.
- **Renombrar los `.mdl` con los nombres de los integrantes,** como exige el enunciado.
- **Preparar la defensa de los SUPUESTOS** (listados en `datos/MODELO_VENSIM.md`, sección 8).

## 7. Limitaciones conocidas

- **No se pudieron obtener** el informe general 2026, el TCO 2026 ni el ECA de Brasil. Los datos llegan hasta H1 2024 (generales) y 2025 (DSA, solo UE).
- **Los indicadores DSA mezclan spam y no-spam y son solo de la UE.**
- **La confianza no se mide en los informes:** es un índice SUPUESTO.
- Todo está registrado en la bitácora y en `datos/processed/validacion.md`.
