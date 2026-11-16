# Modelos de Vensim – Moderación con IA en Discord

Carpeta con los dos modelos oficiales del proyecto final de Pensamiento Sistémico Organizacional (PSO 2026-2, Universidad de La Sabana).

| Archivo | Contenido | Variables |
|---|---|---|
| `Discord_moderacion_actual.mdl` | Situación actual del sistema de moderación de Discord | 48 (6 niveles, 10 flujos, 12 auxiliares, 20 constantes) |
| `Discord_moderacion_mejora.mdl` | Situación con propuesta de mejora (2 intervenciones) | 51 (mismos niveles + 3 auxiliares de mejora) |

---

## 1. Análisis sistémico del modelo

### 1.1 Estructura del modelo

**Niveles (6):**
1. `Usuarios activos` – personas en la comunidad representativa (100.000 iniciales, supuesto).
2. `Confianza de la comunidad` – índice 0 a 1 (supuesto; los informes no miden confianza).
3. `Apelaciones pendientes` – cola de usuarios que apelan un bloqueo.
4. `Denuncias pendientes` – cola de contenido nocivo denunciado por usuarios.
5. `Moderadores en entrenamiento` – nivel en serie antes de ser moderador activo.
6. `Moderadores activos` – personal que atiende las colas.

**Flujos (10):**
- `Usuarios que llegan`, `Usuarios que se van`, `Cambio de confianza`
- `Apelaciones que llegan` (DELAY3), `Apelaciones resueltas`
- `Denuncias que llegan` (DELAY1), `Denuncias resueltas`
- `Voluntarios nuevos`, `Moderadores graduados`, `Moderadores que renuncian`

**Retrasos vistos en clase:**
- `DELAY3`: llegada de apelaciones (tercer orden, material).
- `DELAY1`: llegada de denuncias (primer orden, material).
- `DELAY FIXED`: `Reputacion externa` (6 semanas, información pura).
- `SMOOTH`: `Carga percibida` (4 semanas, información/percepción).

**Configuraciones de niveles:**
- **Niveles en serie:** Voluntarios → Entrenamiento → Moderadores activos → Renuncias.
- **Niveles en paralelo:** Apelaciones y denuncias comparten `Capacidad de revision` (tragedia de los comunes).
- **Niveles heterogéneos acoplados:** Confianza (índice) modula flujos de usuarios (personas) y de voluntarios.

### 1.2 Ciclos de retroalimentación

Notación: `A →(±) B`. Número par de "−" = refuerzo (R); número impar = balance (B).

#### Ciclos de refuerzo (R)

| Ciclo | Recorrido | Enlaces "−" | Tipo |
|---|---|---:|---|
| **R1 Crecimiento de la comunidad** | Usuarios activos →(+) Usuarios que llegan →(+) Usuarios activos | 0 | Refuerzo |
| **R2 Espiral de agotamiento de moderadores** | Moderadores activos →(+) Capacidad de revision →(−) Carga percibida →(+) Moderadores que renuncian →(−) Moderadores activos | 2 | Refuerzo |
| **R3 Voluntariado y confianza** | Confianza →(+) Voluntarios nuevos →(+) Moderadores en entrenamiento →(+) Moderadores graduados →(+) Moderadores activos →(+) Capacidad de revision →(+) Denuncias resueltas →(−) Denuncias pendientes →(+) Molestia por contenido nocivo →(−) Confianza deseada →(+) Cambio de confianza →(+) Confianza | 2 | Refuerzo |

#### Ciclos de balance (B)

| Ciclo | Recorrido | Enlaces "−" | Tipo |
|---|---|---:|---|
| **B1 Abandono de usuarios** | Usuarios activos →(+) Usuarios que se van →(−) Usuarios activos | 1 | Balance |
| **B2 Ajuste de la confianza** | Confianza →(−) Cambio de confianza →(+) Confianza | 1 | Balance |
| **B3 Drenaje de cola de apelaciones** | Apelaciones pendientes →(+) Apelaciones resueltas →(−) Apelaciones pendientes | 1 | Balance |
| **B4 Drenaje de cola de denuncias** | Denuncias pendientes →(+) Denuncias resueltas →(−) Denuncias pendientes | 1 | Balance |
| **B5 Daño visible / límites al crecimiento** | Usuarios activos →(+) Contenido nocivo →(+) Nocivo que se escapa →(+) Denuncias que llegan →(+) Denuncias pendientes →(+) Molestia por contenido nocivo →(−) Confianza deseada →(+) Cambio de confianza →(+) Confianza →(+) Reputacion externa →(+) Usuarios que llegan →(+) Usuarios activos | 1 | Balance |
| **B6 Bloqueos injustos / falsos positivos** | Usuarios activos →(+) Bloqueos por error →(+) Molestia por bloqueos injustos →(−) Confianza deseada →(+) Cambio de confianza →(+) Confianza →(−) Usuarios que se van →(−) Usuarios activos | 3 | Balance |
| **B7 Sensibilidad adaptativa** (solo mejora) | Presion de cola →(−) Sensibilidad efectiva del filtro →(+) Bloqueos por error →(+) Apelaciones que llegan →(+) Apelaciones pendientes →(+) Presion de cola | 1 | Balance |

### 1.3 Arquetipos sistémicos (los tres vistos en clase)

| Arquetipo | Estructura en el modelo |
|---|---|
| **Límites al crecimiento** | R1 (usuarios atraen usuarios) choca con B5 (más usuarios → más nocivo que escapa → más denuncias → más molestia → menos confianza → menos llegada). Factor limitante: `Capacidad de revision` (Moderadores × Productividad). |
| **Desplazamiento de la carga** | Solución sintomática: subir `Sensibilidad del filtro IA` reduce los falsos negativos de inmediato. Efecto secundario: suben los `Bloqueos por error` (no lineal S/(1−S)), suben las apelaciones, sube la `Carga percibida`, se activa R2 (renuncias) y se debilita la solución de fondo. |
| **Tragedia de los comunes** | `Apelaciones pendientes` y `Denuncias pendientes` comparten `Capacidad de revision`. Cuando la carga total supera 1, el recurso se degrada para ambas colas (espera más larga, más renuncias). |

### 1.4 No linealidades

- `Bloqueos por error = ... × Sensibilidad / (1 − Sensibilidad)`: crece explosivamente cuando la sensibilidad se acerca a 1.
- `Moderadores que renuncian = ... × MIN(4, MAX(1, Carga percibida) ^ 2)`: por encima de carga 1, el agotamiento se acelera (tope de 4× la tasa normal).
- `Confianza deseada = MAX(0, 1 − Molestia nocivo − Molestia bloqueos)`: umbral en 0.

### 1.5 Propiedades emergentes, variabilidad, incertidumbre y comportamiento contraintuitivo

- **Propiedad emergente:** bajo sensibilidad fija alta (0,99), el sistema colapsa (usuarios caen a ~4.780, confianza ≈ 0). Con sensibilidad adaptativa y triage, el mismo estrés deja a la comunidad en ~86.194 usuarios y confianza 0,69. El sistema entero se comporta distinto a lo que sugieren las partes por separado.
- **Comportamiento contraintuitivo:** endurecer el filtro (subir sensibilidad) no siempre reduce el daño visible; a corto plazo reduce los falsos negativos, pero a medio plazo dispara los falsos positivos, satura las colas, provoca renuncias de moderadores y vuelve a subir el daño visible. Es el arquetipo de desplazamiento de la carga.
- **Variabilidad:** la fracción de contenido dañino y los tiempos de retraso son supuestos con rango de sensibilidad. La confianza es un índice supuesto (no mide en los informes); se usa la reversión de apelaciones y los indicadores DSA como medida indirecta del error.
- **Incertidumbre:** los datos DSA son de la UE y mezclan spam con no-spam; no hay informe general 2026; la confianza no se observa directamente.

---

## 2. Modelo con mejora (dos intervenciones)

Se mantuvo solo con las dos mejoras originales. **No se incluye la zona gris** (tercera cola de revisión humana previa) porque no mejoraba el caso base, rompía el límite de 50 variables exigido por el enunciado y dificultaba la defensa individual en la sustentación.

| Mejora | Qué cambia | Justificación |
|---|---|---|
| **1. Sensibilidad adaptativa del filtro** | `Sensibilidad efectiva del filtro` baja cuando la `Presion de cola` supera 1 (ciclo B8 de auto-regulación) | Evita que el filtro sature la capacidad de revisión cuando hay mucho trabajo pendiente |
| **2. Triage asistido por IA** | `Productividad por moderador` sube de 120 a 160 piezas/(moderador·semana) | Alivia el factor limitante (capacidad de revisión) sin contratar más moderadores |

---

## 3. Validación del modelo

| Prueba | Actual | Mejora |
|---|---|---|
| Check Model (Vensim PLE 10.5.2) | Model is OK | Model is OK |
| Units Check | Units are OK | Units are OK |
| Simulación 104 semanas, TIME STEP 0,25 | Sin avisos | Sin avisos |
| Precisión del filtro en t=0 | 0,551 (DSA 2025, p. 9) | 0,551 |
| Sensibilidad (recall) en t=0 | 0,973 (DSA 2025, p. 9) | 0,973 |
| Fracción que apela en t=0 | 0,155 (mediana 2022–2023) | 0,155 |
| Reversión en t=0 | 0,0239 (mediana 2022–H1 2024) | 0,0239 |
| Polaridades coincidentes | 49 de 66 | 53 de 66 |
| Polaridades no verificables en t=0 | 16 (retrasos o ramas inactivas) | 18 |
| Polaridades contradictorias | 1 (convención de tiempo de ajuste) | 1 |

Evidencia de capturas: `datos/figuras/evidencia_vensim_actual_units_ok.jpg` y `datos/figuras/evidencia_vensim_mejora_units_ok.jpg`.

---

## 4. Resultados de simulación (104 semanas, Python/Euler dt=0,25)

### 4.1 Caso base (sensibilidad fija 0,973)

| Semana | Usuarios actual | Usuarios mejora | Confianza actual | Confianza mejora | Carga actual | Carga mejora |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 100.000 | 100.000 | 0,80 | 0,80 | 0,80 | 0,60 |
| 26 | 105.333 | 105.333 | 0,80 | 0,80 | 0,83 | 0,62 |
| 52 | 110.949 | 110.949 | 0,80 | 0,80 | 0,85 | 0,64 |
| 78 | 116.865 | 116.865 | 0,80 | 0,80 | 0,86 | 0,65 |
| 104 | 123.096 | 123.096 | 0,80 | 0,80 | 0,87 | 0,65 |

En condiciones normales, ambos modelos se comportan prácticamente igual. La mejora 1 no se activa porque la presión de cola nunca supera 1. La mejora 2 mantiene la carga más baja (0,65 vs 0,87 al final), pero sin impacto visible en usuarios ni confianza.

### 4.2 Prueba de estrés (sensibilidad sube a 0,99 en la semana 26)

| Semana | Usuarios actual | Usuarios mejora | Confianza actual | Confianza mejora | Moderadores actual | Moderadores mejora |
|---|---:|---:|---:|---:|---:|---:|
| 26 | 105.333 | 105.333 | 0,80 | 0,80 | 6,05 | 6,05 |
| 52 | 62.202 | 102.382 | 0,08 | 0,73 | 0,07 | 6,01 |
| 78 | 17.652 | 95.259 | 0,00 | 0,72 | 0,42 | 5,78 |
| 104 | **4.780** | **86.194** | **0,00** | **0,69** | **0,05** | **5,42** |

---

## 5. Interpretación de los resultados

### 5.1 ¿Qué nos dice el caso base?

En condiciones normales (sensibilidad 0,973, el valor calibrado con los datos reales de DSA 2025), el sistema es estable. La comunidad crece moderadamente (de 100.000 a 123.096 usuarios en 104 semanas) y la confianza se mantiene en 0,80. Esto indica que el filtro actual de Discord, con sus tasas de precisión y recall reportadas, no genera un colapso inmediato bajo los supuestos del modelo.

La diferencia entre el modelo actual y el de mejora es mínima en el caso base porque la sensibilidad adaptativa solo se activa cuando la presión de cola supera 1, y eso no ocurre en condiciones normales. La mejora 2 (triage) reduce la carga percibida de 0,87 a 0,65, lo cual es positivo pero no transformador.

### 5.2 ¿Qué nos dice la prueba de estrés (S099)?

Aquí es donde la mejora demuestra su valor. Cuando el filtro se endurece a 0,99 (una política tentadora para reducir falsos negativos), ocurre lo siguiente:

**Modelo actual:** el endurecimiento del filtro dispara los falsos positivos de forma no lineal (curva S/(1−S)). Las colas de apelaciones y denuncias se saturan, la carga percibida se dispara, los moderadores renuncian en cascada (ciclo R2), la confianza colapsa a 0,00 y la comunidad se reduce a 4.780 usuarios (una pérdida del 95 %). Este es un comportamiento **contraintuitivo**: intentar mejorar la detección de contenido nocivo termina destruyendo la comunidad.

**Modelo con mejora:** la sensibilidad adaptativa detecta que la presión de cola supera 1 y baja automáticamente la sensibilidad efectiva del filtro, evitando que los falsos positivos saturen el sistema. El triage asistido por IA mantiene la capacidad de revisión por encima de la demanda. Resultado: la comunidad se mantiene en 86.194 usuarios (una pérdida del 14 %), la confianza se mantiene en 0,69 y los moderadores apenas se reducen a 5,42.

---

## 6. Comparación actual versus mejora

| Dimensión | Modelo actual | Modelo con mejora | Ganador |
|---|---|---|---|
| Estabilidad en caso base | Estable | Estable | Empate |
| Resiliencia ante filtro agresivo (0,99) | Colapso (4.780 usuarios) | Resistencia (86.194 usuarios) | Mejora |
| Carga percibida en caso base | 0,87 | 0,65 | Mejora |
| Confianza bajo estrés | 0,00 | 0,69 | Mejora |
| Moderadores bajo estrés | 0,05 | 5,42 | Mejora |
| Complejidad para defensa individual | Menor | Menor (solo 2 cambios) | Empate |
| Cumple límite de 50 variables | Sí (48) | Sí (51) | Empate |

**Conclusión de la comparación:** la mejora no transforma el sistema en condiciones normales, pero lo vuelve **resiliente ante el arquetipo de desplazamiento de la carga**. Si Discord decide endurecer su filtro de IA para reducir falsos negativos, debe acompañar esa decisión con capacidad humana suficiente (triage) y un mecanismo de autoregulación (sensibilidad adaptativa), de lo contrario el sistema colapsa por el agotamiento de moderadores y la pérdida de confianza de los usuarios.

---

## 7. Evaluación de alternativas

Durante el diseño del modelo se consideraron las siguientes alternativas, descritas originalmente en `PLANTEAMIENTO_MODELO.md` (sección 9):

| Alternativa | Qué proponía | Decisión | Motivo del descarte o adopción |
|---|---|---|---|
| E0: Actual | Sin cambios | Base de comparación | Necesaria como referencia |
| E1: Sensibilidad baja vs. alta | 0,90 frente a 0,99 | Adoptada en prueba S099 | Permite observar el arquetipo de desplazamiento de la carga |
| E2: Dos umbrales (zona gris) | 5 % de decisiones a revisión humana previa | **Descartada** | No mejoraba el caso base, rompía el límite de 50 variables, dificultaba la defensa individual |
| E3: Triage asistido por IA | Productividad 150 → 200 | **Adoptada** (ajustada a 160) | Alivia el factor limitante sin contratar más moderadores |
| E4: Sensibilidad adaptativa | Bajar sensibilidad cuando la cola presiona | **Adoptada** | Evita la saturación de colas bajo estrés (ciclo B8) |
| E5: Combinado (E2 + E3 + E4) | Zona gris + triage + adaptativa | **Descartada** | La zona gris no aportaba valor suficiente para justificar su complejidad |

**Justificación del descarte de la zona gris:** en pruebas preliminares, el modelo con zona gris mostraba curvas idénticas al modelo actual en el caso base y no mejoraba significativamente bajo estrés. Además, agregaba 8 variables nuevas y una tercera cola que competía por la misma capacidad, dificultando la explicación en la sustentación individual (35 % de la rúbrica).

---

## 8. Recomendaciones finales

1. **No endurecer el filtro de IA sin aumentar capacidad humana.** Subir la sensibilidad de 0,973 a 0,99 sin cambios adicionales lleva al colapso del sistema en menos de 2 años simulados. Cualquier política de mayor detección debe ir acompañada de más moderadores o herramientas de triage.

2. **Implementar sensibilidad adaptativa como política de gobernanza.** Un mecanismo que relaje automáticamente el filtro cuando la presión de cola supera la capacidad evita la espiral de agotamiento de moderadores (R2) y protege la confianza de la comunidad.

3. **Invertir en triage asistido por IA.** Aumentar la productividad de los moderadores de 120 a 160 piezas/semana (+33 %) es una mejora concreta y defendible que alivia el factor limitante del sistema sin requerir más personal.

4. **Monitorear la presión de cola como indicador clave.** La presión de cola ((apelaciones + denuncias) / tiempo mínimo de revisión ÷ capacidad) es una señal temprana de riesgo de colapso. Cuando supera 1, el sistema entra en zona de peligro.

5. **Defender los supuestos con sensibilidad.** Los supuestos más sensibles son: fracción de contenido nocivo (0,02 piezas/usuario/semana), productividad por moderador (120 actual / 160 mejora), número de moderadores iniciales (6), y los tiempos de retraso (reputación 6 semanas, entrenamiento 4, percepción de carga 4). El equipo debe preparar pruebas de sensibilidad para cada uno en la sustentación individual.

---

## 9. Instrucciones de uso

1. Abrir el `.mdl` en Vensim PLE 10 o superior.
2. View > Fit to Screen para ver el diagrama completo.
3. Model > Check Model y Model > Units Check (ambos deben pasar sin errores).
4. Simulate con FINAL TIME = 104, TIME STEP = 0,25.
5. Para probar la mejora, cambiar `Productividad por moderador` a 160 y activar `Sensibilidad efectiva del filtro`.
6. Para probar el arquetipo de desplazamiento de la carga, subir `Sensibilidad del filtro IA` de 0,973 a 0,99 y observar el colapso del modelo actual frente a la resiliencia del modelo con mejora.

---

## 10. Archivos relacionados

- `datos/MODELO_VENSIM.md`: explicación variable por variable, ecuaciones, ciclos y arquetipos.
- `datos/PLANTEAMIENTO_MODELO.md`: delimitación, parámetros, supuestos y escenarios (E0–E5).
- `datos/RESUMEN_DATOS.md`: evidencia y limitaciones de los datos de Discord.
- `datos/processed/simulacion_*.csv`: resultados de simulación en Python.
- `datos/figuras/sim_*.png`: gráficos de niveles y flujos.
- `simulacion/`: página web con PySD + FastAPI que ejecuta estos mismos `.mdl`.
