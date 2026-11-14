# Resumen de datos – Informes de transparencia de Discord

> Documento **descriptivo**: qué hay en los datos, con cifras y su ubicación. La interpretación para el informe final la redacta el equipo.
> Fuente única: https://discord.com/safety-transparency · Detalle: `processed/discord_transparencia_largo.csv`, `processed/serie_semanal.csv`, `processed/indicadores_clave.csv`, `processed/validacion.md` · Gráficos: `figuras/`.

## 1. Qué datos existen

| Informe | Periodo | Semanas | Formato | Estado |
|---|---|---|---|---|
| General Q1, Q2, Q3 2022 | trimestral | 12,9–13,1 | PDF + CSV | Extraído |
| General Q4 2022 | trimestral | 13,1 | — | No publicado en la página; solo los totales citados en Q1 2023 (no-spam 153.883; spam 36.825.143; p. 5–6) |
| General Q1, Q2, Q3, Q4 2023 | trimestral | 12,9–13,1 | PDF + CSV | Extraído |
| General H1 2024 | ene–jun 2024 | 26 | PDF + CSV | Extraído; cifras de control verificadas 8/8 |
| General 2026 | mar 2025 – mar 2026 (según el plan) | ≈ 52 | PDF | **No disponible**: la red bloquea cdn.discordapp.com y el equipo no lo encontró. Se trabaja sin él |
| TCO 2026 | — | — | PDF | **No descargado** |
| DSA 2024 (UE) | 17-02-2024 a 31-12-2024 | 45,6 | PDF + 8 CSV | Extraído (quejas, reversiones, medios automatizados) |
| DSA 2025 (UE) | 2025 | 52,1 | PDF + 8 CSV | Extraído (quejas, medios automatizados con precisión y recall, avisos) |
| ECA Brasil 2026 | — | — | PDF | **No descargado** (solo contexto) |

**Vacíos:**
- El informe Q4 2022 no está completo.
- Entre julio de 2024 y febrero de 2025 no hay informe general.
- Las tablas por categoría de los DSA (avisos y medidas de iniciativa propia por tipo de contenido) quedaron en `raw/` sin procesar.

## 2. Evolución 2022–2024

### Cuentas deshabilitadas (figura `01_cuentas_deshabilitadas_semana.png`)

| Periodo | No-spam (total) | No-spam / semana | Spam (total) | Spam / semana | % spam |
|---|---|---|---|---|---|
| Q4 2021 (citado) | 1.127.220 | 85.766 | 19.794.949 | 1.506.133 | 94,6 % |
| Q1 2022 | 1.054.358 | 82.006 | 26.017.742 | 2.023.609 | 96,1 % |
| Q2 2022 | 726.759 | 55.905 | 27.733.948 | 2.133.381 | 97,4 % |
| Q3 2022 | 185.756 | 14.134 | 50.510.769 | 3.843.198 | 99,6 % |
| Q4 2022 (citado) | 153.883 | 11.708 | 36.825.143 | 2.801.904 | 99,6 % |
| Q1 2023 | 173.745 | 13.514 | 10.693.885 | 831.749 | 98,4 % |
| Q2 2023 | 294.255 | 22.635 | 7.971.335 | 613.180 | 96,4 % |
| Q3 2023 | 260.461 | 19.818 | 12.845.746 | 977.391 | 98,0 % |
| Q4 2023 | 255.063 | 19.407 | 32.973.473 | 2.508.843 | 99,2 % |
| H1 2024 | 357.056 | 13.733 | 35.456.553 | 1.363.714 | 99,0 % |

**Composición del no-spam** (figura `03`):
- Seguridad infantil es la categoría más grande en 7 de 8 periodos: 78 % en Q1 2022 y 50 % en H1 2024.
- En Q3 2022 y Q1 2023 pesan más "contenido explotador / no solicitado" y "actividades ilegales o reguladas".

### Servidores eliminados (no-spam)
- 28.370 (Q2 2022) a 54.362 (Q2 2023) por trimestre; 41.002 en H1 2024.
- La fracción eliminada de forma proactiva pasó de 51,9 % (Q1 2022: 20.764 de 40.009) a 93,7 % (Q4 2023: 47.594 de 50.814), según las tablas Servers Removed.

### Reportes (figura `02`), con cambio de definición
- **2022 – Q1 2023:** reportes no-spam por formulario web, de 117.042 a 178.414 por trimestre (≈ 9.100–13.900 por semana). Los reportes de spam de un clic van aparte: de 21.200.699 (Q1 2022) a 6.023.898 (Q1 2023).
- **Q2 2023 – H1 2024:** reportes en la app, de 11.967.380 a 13.044.219 por trimestre y 29.495.313 en H1 2024 (≈ 0,92–1,13 millones por semana). La categoría "Platform Manipulation" incluye todos los reportes de spam: entre 49,7 % y 54,7 % del total.
- **No son comparables** antes y después de Q2 2023.

### Apelaciones y reversión (figura `04`), no-spam

| Periodo | Apelaciones | % de cuentas que apelan | Cuentas restauradas | % de apelaciones concedidas |
|---|---|---|---|---|
| Q1 2022 | 113.231 | 10,74 % | 2.275 | 2,01 % |
| Q2 2022 | 122.714 | 16,89 % | 733 | 0,60 % |
| Q3 2022 | 28.736 | 15,47 % | 1.334 | 4,64 % |
| Q1 2023 | 38.134 | 21,95 % | 778 | 2,04 % |
| Q2 2023 | 30.330 | 10,31 % | 712 | 2,35 % |
| Q3 2023 | 46.325 | 17,79 % | 1.163 | 2,51 % |
| Q4 2023 | 33.780 | 13,24 % | 821 | 2,43 % |
| H1 2024 | 65.901 | 1,85 %* | 1.705 | 2,59 % |

\* En H1 2024 la base son 3.568.821 cuentas sancionadas distintas (incluye advertencias y suspensiones temporales), no las cuentas deshabilitadas. No es comparable con los periodos anteriores.

## 3. Evidencia sobre falsos positivos

| Evidencia | Cifra | Fuente | Advertencia |
|---|---|---|---|
| Cuentas restauradas / apelaciones | mediana 2,39 % (0,60 %–4,64 %) | Generales 2022 – H1 2024 | Solo cuenta a quien apela y gana |
| Cuentas restauradas / cuentas deshabilitadas | 0,10 %–0,72 % | Derivado | Cota inferior de los falsos positivos |
| Quejas con decisión revertida (UE) | 16,36 % (43.715 de 267.137) | DSA 2024, p. 12 | Mezcla spam y no-spam |
| Restricciones revertidas tras queja (UE) | 25,65 % (34.385 de 134.062) | DSA 2024, p. 13 | Cuenta restricciones, no quejas |
| Tasa de error de los medios automatizados (UE) | 6,65 % total; 11,86 % al procesar quejas; 1,44 % en iniciativa propia | DSA 2024, p. 12 | Métrica distinta de la de 2025 |
| Precisión de los medios automatizados (UE) | 55,1 % total (44,9 % de las decisiones automáticas positivas fueron erróneas); 60,0 % iniciativa propia; 92,3 % avisos | DSA 2025, p. 9 | Mezcla spam y no-spam |
| Recall de los medios automatizados (UE) | 97,3 % total; 96,4 % iniciativa propia; 90,5 % avisos | DSA 2025, p. 9 | — |
| Intervenciones retiradas | 10,37 % (60.686), cifra del plan | General 2026 | **Descartada**: sin PDF no se puede rastrear; además tiene otra definición |

**Grado de automatización (UE)** (figura `06`):
- DSA 2024: 81,6 % de los ítems procesados solo por medios automatizados (114.252 de 140.034).
- DSA 2025: 46,4 % de los avisos procesados solo de forma automatizada.
- El total DSA 2025 (2,2 %) no es fiable: la fuente reporta más medidas automatizadas de iniciativa propia (35.731) que el total (30.740).

## 4. Limitaciones

1. **Fuente única escrita por la propia empresa:** no hay contraste externo, por regla del proyecto.
2. **Cambios de definición:**
   - Canal de reportes (web → app, Q2 2023).
   - Base de la tasa de apelación (deshabilitadas → sancionadas distintas, H1 2024).
   - Reversión: cuentas restauradas (2022–2024) frente a intervenciones retiradas (2026).
   - DSA: tasa de error (2024) frente a precisión y recall (2025).
3. **Periodicidad irregular:** trimestral, semestral y anual. Todo se normalizó a tasa semanal (valor ÷ semanas), que es un promedio del periodo.
4. **Falsos positivos no apelados:** no se observan. Las restauraciones son una cota inferior del error.
5. **Spam:** está en el texto de los PDF y no en los CSV. Los indicadores DSA lo mezclan con el no-spam.
6. **Errores de la fuente** (ver `validacion.md`):
   - Las advertencias de Q3 2022 son idénticas a las de Q1 2023.
   - La tabla Accounts Disabled de Q3 2023 en el CSV está desalineada (se corrigió).
   - Hay inconsistencias internas en los DSA 2025.
7. **Faltan informes:** el general 2026, el TCO y el ECA no se pudieron obtener. Los datos más recientes son H1 2024 (generales) y 2025 (DSA, solo UE); no hay serie general después de junio de 2024.
