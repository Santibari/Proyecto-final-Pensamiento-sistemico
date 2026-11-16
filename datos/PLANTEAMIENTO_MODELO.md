# Planteamiento del modelo – Moderación automatizada con IA en Discord

> Insumo para que el equipo construya los modelos en Vensim (fase 2). **No es el modelo final ni su interpretación.**
> Cada parámetro está marcado como **DATO** (sale de los informes de transparencia de Discord, con informe y página),
> **CALIBRADO** (se ajusta para reproducir un DATO) o **SUPUESTO** (no está en la fuente; debe justificarse y probarse con sensibilidad).
> Cifras de soporte: `processed/indicadores_clave.csv`, `processed/serie_semanal.csv`, `processed/validacion.md`.

---

## 1. Delimitación

| Elemento | Decisión |
|---|---|
| Sistema | Una comunidad representativa de Discord de **100.000 usuarios activos** (un conjunto de servidores con su equipo de moderación) |
| Problema | El filtro automático de IA bloquea contenido dañino, pero también contenido legítimo (**falsos positivos**) y deja pasar contenido dañino (**falsos negativos**). Ambos errores llegan a una cola de revisión humana con capacidad limitada y afectan la confianza de los usuarios |
| Contenido modelado | Contenido dañino **no-spam** (acoso, odio, seguridad infantil, contenido violento, etc.) |
| Spam | Solo contexto: es el 94,6 %–99,6 % de las cuentas deshabilitadas (`indicadores_clave.csv`, fraccion_spam_deshabilitadas_pct) y el 99 % se elimina de forma proactiva (informes Q1 2023 – Q4 2023). No entra en las ecuaciones |
| Fuera del alcance | Solicitudes legales y de gobiernos, NCMEC, reglas específicas de cada servidor, economía de la plataforma |

## 2. Tiempo

| Parámetro | Valor | Justificación |
|---|---|---|
| Unidad de tiempo | **Week** | La confianza de los usuarios y el agotamiento de los moderadores cambian en semanas. La mediana de respuesta a una queja es de 57,34 h (DSA 2024) a 352,68 h (DSA 2025), es decir, entre 0,34 y 2,1 semanas. Las series se normalizaron a tasas semanales (`serie_semanal.csv`) |
| INITIAL TIME | 0 | |
| FINAL TIME | **104** (2 años; el mínimo exigido es 70) | Cubre varios ciclos de ajuste de la confianza (8 semanas) y de rotación de moderadores (≈ 50 semanas) |
| TIME STEP | **0,25** | Menor que la constante de tiempo más corta (0,34 semanas de revisión), para que la integración sea estable |

## 3. Variables

**Nombres:** se recomienda escribirlos en Vensim **sin tildes ni ñ** (por ejemplo `Contenido danino no spam`) para evitar problemas de codificación.

| Tipo | Variables |
|---|---|
| **Niveles (4)** | Usuarios Activos · Cola de Revision · Moderadores · Confianza de Usuarios |
| **Flujos (7)** | Nuevos usuarios · Abandono · Entrada a revision · Revisiones resueltas · Incorporacion de moderadores · Renuncias · Cambio en confianza |
| **Auxiliares** | Mensajes publicados · Contenido danino no spam · Contenido legitimo · Sensibilidad efectiva · Tasa de falsos positivos · Verdaderos positivos · Falsos positivos · Falsos negativos · Revision humana previa · Apelaciones de falsos positivos · Apelaciones de verdaderos positivos · Apelaciones · Reportes · Capacidad de revision · Carga relativa · Presion de cola · Apelaciones aceptadas · Tiempo de espera · Dano visible por usuario · Castigo injusto por usuario · Efecto dano · Efecto falsos positivos · Confianza objetivo · Efecto carga en renuncias · Efecto carga en reclutamiento · indicadores de calibración (Precision del filtro, Tasa de reversion, Fraccion que apela, Fraccion de reportes accionados) |
| **Constantes** | Sensibilidad del filtro (**palanca de política**) · Tasa base de falsos positivos · Elasticidad de falsos positivos · Fraccion danina · Mensajes por usuario · Fraccion que apela FP / VP · Fraccion reportada de FN · Tasa de reporte erroneo · Probabilidad de corregir error · Productividad de moderadores · Tiempo minimo de revision · Tasa de crecimiento base · Tasa de abandono base · Sensibilidad del abandono a la desconfianza · Confianza de referencia · Tasa de voluntariado · Tasa base de renuncia · Tiempo de ajuste de confianza · Pesos y referencias de la confianza · Interruptores de la mejora (Fraccion zona gris, Interruptor sensibilidad adaptativa, Ajuste por carga, Sensibilidad minima y maxima) |

## 4. Tabla de parámetros

| Variable | Valor | Unidad | Tipo | Fórmula o cálculo | Fuente (informe, página) |
|---|---|---|---|---|---|
| Sensibilidad del filtro | **0,973** | Dmnl | DATO | Recall de los medios automatizados = 97,3 % | DSA 2025, p. 9; CSV "7. Automated Means" |
| Precisión objetivo del filtro | 0,551 | Dmnl | DATO (meta de calibración) | Precisión de los medios automatizados = 55,1 % (por tanto 44,9 % de las decisiones automáticas positivas son falsos positivos) | DSA 2025, p. 9 |
| Tasa base de falsos positivos | **0,000794** | Dmnl | CALIBRADO | Con precisión P y recall R: tasa = (1−P)/P · R · f/(1−f) = 0,8149 · 0,973 · 0,001/0,999 | Deriva de DSA 2025, p. 9 + Fraccion danina (SUPUESTO) |
| Elasticidad de falsos positivos | 1 | Dmnl | SUPUESTO | Los falsos positivos crecen con los *momios* de la sensibilidad, S/(1−S): subir de 0,973 a 0,99 multiplica los FP por ≈ 2,75 | Forma típica de una curva ROC; no está en la fuente |
| Fraccion danina | 0,001 | Dmnl | SUPUESTO | 1 de cada 1.000 piezas de contenido es dañina no-spam | Los informes no publican prevalencia. Probar entre 0,0005 y 0,005 |
| Mensajes por usuario | 20 | piezas/(usuarios·Week) | SUPUESTO | — | Los informes no publican volumen de mensajes |
| Fraccion que apela (total) | **0,155** | Dmnl | DATO (meta de calibración) | Mediana de la tasa de apelación no-spam entre Q1 2022 y Q4 2023 (rango 10,31 %–21,95 %) | Informes generales 2022–2023, tablas Appeals (CSV); p. ej. Q3 2022, p. 6 |
| Fraccion que apela FP | 0,25 | Dmnl | CALIBRADO | Con FP = 1.586 y VP = 1.946 piezas/semana: (0,25·1.586 + 0,08·1.946)/3.532 = 0,156 | Reproduce 0,155 |
| Fraccion que apela VP | 0,08 | Dmnl | CALIBRADO / SUPUESTO | Quien fue sancionado con razón apela menos que quien fue sancionado por error | Supuesto de comportamiento |
| Probabilidad de corregir error | **0,0333** | Dmnl | CALIBRADO | Tasa de reversión del modelo = (fracción de apelaciones que son FP ≈ 0,718) × 0,0333 = **0,0239** | Meta: 2,39 %, mediana de cuentas restauradas / apelaciones no-spam, Q1 2022 – H1 2024 (tablas Appeals; H1 2024 p. 9). La cifra 2026 (10,37 %) se descartó: el PDF no se pudo obtener |
| — rango de la tasa de reversión para sensibilidad | 0,006 – 0,164 | Dmnl | DATO | Mínimo trimestral: 0,60 % (Q2 2022); máximo trimestral: 4,64 % (Q3 2022); cota alta: 16,36 % de quejas revertidas (DSA 2024: 43.715 de 267.137; mezcla spam). Probabilidad de corregir error = 0,0084 / 0,0646 / 0,2278 respectivamente | Generales 2022–2024 (H1 2024 p. 9); DSA 2024 p. 12 |
| Fraccion reportada de FN | 0,5 | Dmnl | SUPUESTO | La mitad del contenido dañino que pasa el filtro es reportado por usuarios | No publicado |
| Tasa de reporte erroneo | 0,000077 | Dmnl | CALIBRADO | Reportes sobre contenido legítimo, ajustados para que la fracción de reportes con acción sea ≈ 0,15 | Meta: 12,6 %–24,6 % de reportes web con acción (Q1 2022 – Q2 2023, CSV Reports) |
| Tiempo minimo de revision | **0,34** | Week | DATO | 57,34 h ÷ 168 h/semana (mediana de resolución de quejas) | DSA 2024, CSV "6. Overall Figures". Alternativa: 352,68 h = 2,1 semanas (DSA 2025) |
| Productividad de moderadores | 150 | piezas/(moderadores·Week) | SUPUESTO | ≈ 30 casos por día durante 5 días | No publicado |
| Moderadores (inicial) | 6 | moderadores | SUPUESTO | Carga inicial ≈ 0,81: capacidad suficiente pero sin holgura | No publicado (el DSA marca "n/a" en recursos humanos) |
| Cola de Revision (inicial) | 250 | piezas | CALIBRADO | Entrada (≈ 732) × Tiempo mínimo (0,34): arranca en equilibrio | — |
| Usuarios Activos (inicial) | 100.000 | usuarios | SUPUESTO | Delimitación | — |
| Confianza de Usuarios (inicial) | 0,8 | Dmnl | SUPUESTO | Los informes no miden confianza | Probar entre 0,6 y 0,9 |
| Tasa de crecimiento base | 0,012 | 1/Week | SUPUESTO | ≈ +23 % en 2 años en el escenario base | No publicado |
| Tasa de abandono base | 0,008 | 1/Week | SUPUESTO | — | — |
| Sensibilidad del abandono a la desconfianza | 1,25 | Dmnl | SUPUESTO | Con confianza 0,8 el abandono es 0,01/semana | — |
| Confianza de referencia | 0,8 | Dmnl | SUPUESTO | Igual a la confianza inicial | — |
| Tasa de voluntariado | 1,5e-6 | moderadores/(usuarios·Week) | CALIBRADO | Igual a las renuncias iniciales: 6 · 0,02 = 100.000 · v · 0,8 | — |
| Tasa base de renuncia | 0,02 | 1/Week | SUPUESTO | Permanencia media de un moderador ≈ 50 semanas | — |
| Tiempo de ajuste de confianza | 8 | Week | SUPUESTO | Retraso de percepción | Probar entre 4 y 16 |
| Peso del dano / Peso de FP | 0,1 / 0,1 | Dmnl | SUPUESTO | Con ambos efectos = 1, Confianza objetivo = 0,8 | — |
| Dano de referencia | 0,00054 | piezas/(usuarios·Week) | CALIBRADO | Falsos negativos iniciales / usuarios = 54/100.000 | — |
| Castigo injusto de referencia | 0,0157 | piezas/(usuarios·Week) | CALIBRADO | (FP − apelaciones aceptadas) iniciales / usuarios = (1.586 − 13) / 100.000 | — |
| Tiempo de espera de referencia | 0,34 | Week | DATO | = Tiempo minimo de revision | DSA 2024 |

**Valores iniciales calculados** (S = 0,973):
- Mensajes publicados: 2.000.000 piezas/semana.
- Contenido dañino: 2.000; verdaderos positivos (VP): 1.946; falsos negativos (FN): 54; falsos positivos (FP): 1.586.
- Apelaciones: 552; reportes: 181; entrada a la cola: 732 piezas/semana.
- Capacidad: 900; carga: 0,81.

## 5. Ecuaciones propuestas (sintaxis Vensim, con unidades)

```
{************ USUARIOS ************}
Usuarios Activos = INTEG(Nuevos usuarios - Abandono, 100000)
	~	usuarios
	~	Nivel. Comunidad representativa (SUPUESTO).
	|
Nuevos usuarios = Usuarios Activos * Tasa de crecimiento base * Confianza de Usuarios / Confianza de referencia
	~	usuarios/Week
	|
Abandono = Usuarios Activos * Tasa de abandono base * (1 + Sensibilidad del abandono a la desconfianza * (1 - Confianza de Usuarios))
	~	usuarios/Week
	|
Tasa de crecimiento base = 0.012
	~	1/Week
	|
Tasa de abandono base = 0.008
	~	1/Week
	|
Sensibilidad del abandono a la desconfianza = 1.25
	~	Dmnl
	|
Confianza de referencia = 0.8
	~	Dmnl
	|

{************ CONTENIDO Y FILTRO DE IA ************}
Mensajes publicados = Usuarios Activos * Mensajes por usuario
	~	piezas/Week
	|
Mensajes por usuario = 20
	~	piezas/(usuarios*Week)
	|
Contenido danino no spam = Mensajes publicados * Fraccion danina
	~	piezas/Week
	|
Contenido legitimo = Mensajes publicados * (1 - Fraccion danina)
	~	piezas/Week
	|
Fraccion danina = 0.001
	~	Dmnl
	|
Sensibilidad del filtro = 0.973
	~	Dmnl [0.5, 0.999, 0.001]
	~	Palanca de política. DATO: recall DSA 2025 (p. 9).
	|
Sensibilidad efectiva = IF THEN ELSE(Interruptor sensibilidad adaptativa = 1,
	MAX(Sensibilidad minima, MIN(Sensibilidad maxima, Sensibilidad del filtro - Ajuste por carga * MAX(0, Presion de cola - 1))),
	Sensibilidad del filtro)
	~	Dmnl
	|
Verdaderos positivos = Contenido danino no spam * Sensibilidad efectiva
	~	piezas/Week
	|
Falsos negativos = Contenido danino no spam * (1 - Sensibilidad efectiva)
	~	piezas/Week
	|
Tasa de falsos positivos = Tasa base de falsos positivos *
	((Sensibilidad efectiva / (1 - Sensibilidad efectiva)) / (Sensibilidad de referencia / (1 - Sensibilidad de referencia))) ^ Elasticidad de falsos positivos
	~	Dmnl
	|
Falsos positivos = Contenido legitimo * Tasa de falsos positivos
	~	piezas/Week
	|
Tasa base de falsos positivos = 0.000794
	~	Dmnl
	~	CALIBRADO con la precisión del 55,1 % (DSA 2025, p. 9).
	|
Sensibilidad de referencia = 0.973
	~	Dmnl
	|
Elasticidad de falsos positivos = 1
	~	Dmnl
	|

{************ APELACIONES, REPORTES Y COLA ************}
Revision humana previa = Fraccion zona gris * (Verdaderos positivos + Falsos positivos)
	~	piezas/Week
	~	0 en el modelo actual (mejora: sistema de dos umbrales).
	|
Apelaciones de falsos positivos = Falsos positivos * (1 - Fraccion zona gris) * Fraccion que apela FP
	~	piezas/Week
	|
Apelaciones de verdaderos positivos = Verdaderos positivos * (1 - Fraccion zona gris) * Fraccion que apela VP
	~	piezas/Week
	|
Apelaciones = Apelaciones de falsos positivos + Apelaciones de verdaderos positivos
	~	piezas/Week
	|
Reportes = Falsos negativos * Fraccion reportada de FN + Contenido legitimo * Tasa de reporte erroneo
	~	piezas/Week
	|
Entrada a revision = Apelaciones + Reportes + Revision humana previa
	~	piezas/Week
	|
Cola de Revision = INTEG(Entrada a revision - Revisiones resueltas, 250)
	~	piezas
	|
Capacidad de revision = Moderadores * Productividad de moderadores
	~	piezas/Week
	|
Revisiones resueltas = MIN(Cola de Revision / Tiempo minimo de revision, Capacidad de revision)
	~	piezas/Week
	|
Tiempo minimo de revision = 0.34
	~	Week
	~	DATO: 57,34 h (DSA 2024).
	|
Fraccion que apela FP = 0.25
	~	Dmnl
	~	CALIBRADO: junto con la de VP reproduce el 15,5 % de apelación (generales 2022-2023).
	|
Fraccion que apela VP = 0.08
	~	Dmnl
	|
Fraccion reportada de FN = 0.5
	~	Dmnl
	~	SUPUESTO.
	|
Tasa de reporte erroneo = 7.7e-005
	~	Dmnl
	~	CALIBRADO: fracción de reportes con acción de aproximadamente 0,15 (rango 12,6 %-24,6 %).
	|
Probabilidad de corregir error = 0.0333
	~	Dmnl
	~	CALIBRADO: tasa de reversión 2,39 % (mediana de cuentas restauradas / apelaciones, Q1 2022 - H1 2024).
	~	Sensibilidad: 0.2278 reproduce 16,36 % (quejas revertidas DSA 2024, mezcla spam).
	|
Apelaciones aceptadas = Revisiones resueltas * ZIDZ(Apelaciones de falsos positivos, Entrada a revision) * Probabilidad de corregir error
	~	piezas/Week
	|
Tiempo de espera = ZIDZ(Cola de Revision, Revisiones resueltas)
	~	Week
	|
Carga relativa = XIDZ(Entrada a revision, Capacidad de revision, 10)
	~	Dmnl
	|
Presion de cola = XIDZ(Cola de Revision / Tiempo minimo de revision, Capacidad de revision, 10)
	~	Dmnl
	~	Basada en el nivel (no en los flujos) para no crear un ciclo algebraico con la sensibilidad adaptativa.
	|

{************ MODERADORES ************}
Moderadores = INTEG(Incorporacion de moderadores - Renuncias, 6)
	~	moderadores
	|
Incorporacion de moderadores = Usuarios Activos * Tasa de voluntariado * Confianza de Usuarios * Efecto carga en reclutamiento
	~	moderadores/Week
	|
Renuncias = Moderadores * Tasa base de renuncia * Efecto carga en renuncias
	~	moderadores/Week
	|
Efecto carga en renuncias = WITH LOOKUP(Carga relativa, ([(0,0)-(3,6)], (0,1), (1,1), (1.5,2), (2,4), (3,6)))
	~	Dmnl
	~	SUPUESTO: por encima de carga 1 el agotamiento acelera las renuncias.
	|
Efecto carga en reclutamiento = WITH LOOKUP(Carga relativa, ([(0,0)-(3,2)], (0,0.8), (1,1), (2,1.5), (3,1.7)))
	~	Dmnl
	~	SUPUESTO: con más carga se buscan más voluntarios, con rendimientos decrecientes.
	|
Productividad de moderadores = 150
	~	piezas/(moderadores*Week)
	|
Tasa de voluntariado = 1.5e-006
	~	moderadores/(usuarios*Week)
	|
Tasa base de renuncia = 0.02
	~	1/Week
	|

{************ CONFIANZA ************}
Confianza de Usuarios = INTEG(Cambio en confianza, 0.8)
	~	Dmnl
	|
Cambio en confianza = (Confianza objetivo - Confianza de Usuarios) / Tiempo de ajuste de confianza
	~	1/Week
	|
Confianza objetivo = MAX(0, 1 - Peso del dano * Efecto dano - Peso de FP * Efecto falsos positivos)
	~	Dmnl
	|
Dano visible por usuario = Falsos negativos / Usuarios Activos
	~	piezas/(usuarios*Week)
	|
Efecto dano = (Dano visible por usuario / Dano de referencia) * (Tiempo de espera / Tiempo de espera de referencia)
	~	Dmnl
	~	El daño se ve más tiempo cuando la cola tarda en resolverse.
	|
Castigo injusto por usuario = MAX(0, Falsos positivos * (1 - Fraccion zona gris) - Apelaciones aceptadas) / Usuarios Activos
	~	piezas/(usuarios*Week)
	|
Efecto falsos positivos = Castigo injusto por usuario / Castigo injusto de referencia
	~	Dmnl
	|
Tiempo de ajuste de confianza = 8 ~ Week |
Peso del dano = 0.1 ~ Dmnl |
Peso de FP = 0.1 ~ Dmnl |
Dano de referencia = 0.00054 ~ piezas/(usuarios*Week) |
Castigo injusto de referencia = 0.0157 ~ piezas/(usuarios*Week) |
Tiempo de espera de referencia = 0.34 ~ Week |

{************ PALANCAS DE LA MEJORA (en el modelo actual: 0) ************}
Fraccion zona gris = 0 ~ Dmnl [0, 0.5, 0.01] |
Interruptor sensibilidad adaptativa = 0 ~ Dmnl [0, 1, 1] |
Ajuste por carga = 0.1 ~ Dmnl |
Sensibilidad minima = 0.7 ~ Dmnl |
Sensibilidad maxima = 0.99 ~ Dmnl |

{************ INDICADORES DE CALIBRACIÓN ************}
Precision del filtro = ZIDZ(Verdaderos positivos, Verdaderos positivos + Falsos positivos) ~ Dmnl |
Fraccion que apela = ZIDZ(Apelaciones, (Verdaderos positivos + Falsos positivos) * (1 - Fraccion zona gris)) ~ Dmnl |
Tasa de reversion = ZIDZ(Apelaciones aceptadas, Revisiones resueltas * ZIDZ(Apelaciones, Entrada a revision)) ~ Dmnl |
Fraccion de reportes accionados = ZIDZ(Falsos negativos * Fraccion reportada de FN, Reportes) ~ Dmnl |
```

> En el archivo `.mdl` las constantes de una sola línea (`X = valor ~ unidad |`) deben quedar en el formato de tres partes de Vensim (ecuación, `~` unidad, `~` comentario, `|`). Antes de simular, revise con **Model > Units Check** que `Week` esté definido como unidad de tiempo en *Model Settings* y que `piezas`, `usuarios` y `moderadores` aparezcan como unidades básicas.

## 6. Diagrama causal en texto

### Relaciones con polaridad

| Origen → Destino | Polaridad |
|---|---|
| Usuarios Activos → Nuevos usuarios | + |
| Nuevos usuarios → Usuarios Activos | + |
| Usuarios Activos → Mensajes publicados | + |
| Mensajes publicados → Contenido danino / Contenido legitimo | + |
| Sensibilidad efectiva → Verdaderos positivos | + |
| Sensibilidad efectiva → Falsos negativos | − |
| Sensibilidad efectiva → Falsos positivos (no lineal) | + |
| Falsos positivos → Apelaciones | + |
| Falsos negativos → Reportes | + |
| Apelaciones, Reportes → Entrada a revision → Cola de Revision | + |
| Cola de Revision → Tiempo de espera | + |
| Capacidad de revision → Revisiones resueltas | + |
| Revisiones resueltas → Cola de Revision | − |
| Moderadores → Capacidad de revision | + |
| Capacidad de revision → Carga relativa | − |
| Entrada a revision → Carga relativa | + |
| Carga relativa → Renuncias | + |
| Renuncias → Moderadores | − |
| Carga relativa → Incorporacion de moderadores | + |
| Incorporacion → Moderadores | + |
| Confianza → Incorporacion de moderadores | + |
| Tiempo de espera, Falsos negativos → Efecto dano | + |
| Falsos positivos → Castigo injusto | + |
| Apelaciones aceptadas → Castigo injusto | − |
| Efecto dano, Efecto FP → Confianza objetivo | − |
| Confianza objetivo → Confianza de Usuarios | + |
| Confianza de Usuarios → Nuevos usuarios | + |
| Confianza de Usuarios → Abandono | − |
| Abandono → Usuarios Activos | − |
| Presion de cola → Sensibilidad efectiva (solo en la mejora) | − |

### Ciclos

Notación: `A →(±) B` es el signo del enlace de A hacia B.

| Ciclo | Recorrido | Enlaces negativos | Tipo |
|---|---|---|---|
| **R1 Crecimiento de usuarios** | Usuarios →(+) Nuevos usuarios →(+) Usuarios | 0 | Refuerzo |
| **B1 Daño visible** | Usuarios →(+) Mensajes →(+) Contenido dañino →(+) Falsos negativos →(+) Reportes →(+) Cola →(+) Tiempo de espera →(+) Efecto daño →(−) Confianza objetivo →(+) Confianza →(+) Nuevos usuarios →(+) Usuarios | 1 | Balance |
| **B2 Falsos positivos** | Usuarios →(+) Mensajes →(+) Contenido legítimo →(+) Falsos positivos →(+) Castigo injusto →(+) Efecto FP →(−) Confianza objetivo →(+) Confianza →(−) Abandono →(−) Usuarios | 3 | Balance |
| **R2 Espiral de agotamiento de moderadores** | Carga relativa →(+) Renuncias →(−) Moderadores →(+) Capacidad →(−) Carga relativa | 2 | Refuerzo |
| **B3 Voluntariado** | Carga relativa →(+) Incorporación →(+) Moderadores →(+) Capacidad →(−) Carga relativa | 1 | Balance |
| **B4 Drenaje de la cola** | Cola →(+) Revisiones resueltas →(−) Cola (mientras no se llegue a la capacidad) | 1 | Balance |
| **B5 Sensibilidad adaptativa** (solo en la mejora) | Cola →(+) Presión de cola →(−) Sensibilidad efectiva →(+) Falsos positivos →(+) Apelaciones →(+) Entrada a revisión →(+) Cola | 1 | Balance |

La regla de clase es: número par de enlaces negativos, refuerzo; número impar, balance.

La corrección por apelación (Falsos positivos →(+) Apelaciones →(+) Cola →(+) Revisiones resueltas →(+) Apelaciones aceptadas →(−) Castigo injusto) es una **cadena**, no un ciclo cerrado. Atenúa B2, y su efecto depende de la capacidad de revisión (Moderadores × Productividad).

## 7. Arquetipos candidatos

| Arquetipo | Estructura en el modelo |
|---|---|
| **Soluciones que fallan** | Subir la *Sensibilidad del filtro* reduce los falsos negativos de inmediato (solución sintomática al daño visible, B1). Con retraso, los falsos positivos crecen de forma no lineal, suben las apelaciones y la carga, se activa R2 (renuncias) y aumentan el tiempo de espera y el daño visible: el síntoma original vuelve |
| **Límites al crecimiento** | R1 (crecimiento de usuarios) choca con la capacidad de revisión: más usuarios generan más reportes y apelaciones hasta que la carga supera 1 y se activan B1/B2 y R2. El factor limitante son los *Moderadores × Productividad* |
| Desplazamiento de la carga (alternativo) | Confiar en la IA (sensibilidad alta) en vez de fortalecer la capacidad humana (moderadores, productividad) |

## 8. Objetivos de calibración y validación

| Comportamiento real | Valor de la fuente | Indicador del modelo en t = 0 |
|---|---|---|
| Precisión de los medios automatizados | 55,1 % (DSA 2025, p. 9) | Precision del filtro = 0,551 |
| Recall de los medios automatizados | 97,3 % (DSA 2025, p. 9) | Sensibilidad del filtro = 0,973 |
| Fracción de sancionados que apela | 10,3 %–21,9 %, mediana 15,5 % (generales 2022–2023) | Fraccion que apela = 0,156 |
| Tasa de reversión de apelaciones (no-spam) | mediana 2,39 % (rango 0,60 %–4,64 %, Q1 2022 – H1 2024); UE con spam: 16,36 % (DSA 2024) | Tasa de reversion = 0,024 |
| Reportes con acción | 12,6 %–24,6 % (formulario web 2022–Q2 2023) | Fraccion de reportes accionados ≈ 0,15 |
| Tiempo de resolución | 0,34 semanas (DSA 2024) – 2,1 semanas (DSA 2025) | Tiempo de espera = 0,34 |

**Pruebas sugeridas para la validación:**
- Con Fraccion danina = 0, no debe haber FN, reportes por daño ni efecto daño.
- Con Moderadores = 0, la cola crece sin límite.
- Units Check sin errores.
- Sensibilidad (Vensim *Sensitivity*) en los SUPUESTOS de la tabla 4.

**Prueba numérica previa:** se hizo en Python, fuera del proyecto y sin Vensim, solo para revisar que las ecuaciones sean estables y cumplan las metas de calibración.
- Con los valores de la tabla 4, en el escenario base los cuatro niveles evolucionan suavemente durante 104 semanas: usuarios 100.000 → ≈ 123.000; carga 0,81 → 0,90.
- Los indicadores de calibración quedan constantes en 0,551 / 0,156 / 0,024.
- La simulación oficial y su análisis los hace el equipo en Vensim.

## 9. Escenarios para la propuesta de mejora (solo planteados)

| Escenario | Cambio de parámetros | Qué observar |
|---|---|---|
| E0 Actual | Sensibilidad 0,973; Fraccion zona gris 0; Interruptor 0; Productividad 150 | Base de comparación |
| E1 Sensibilidad baja vs. alta | Sensibilidad 0,90 frente a 0,99 (el plan sugería 0,7 frente a 0,9; con el recall real de 0,973 se proponen valores alrededor del actual) | FN, FP, carga, moderadores, confianza |
| E2 Dos umbrales (zona gris) | Fraccion zona gris = 0,05–0,20: una parte de las decisiones automáticas pasa a revisión humana antes de aplicarse | La carga sube: combinarlo con E3 o con más moderadores |
| E3 Triage asistido por IA | Productividad de moderadores 150 → 200 (+33 %) | Carga relativa, renuncias |
| E4 Sensibilidad adaptativa | Interruptor = 1; Ajuste por carga 0,1; límites 0,7–0,99 | La sensibilidad baja cuando la cola presiona |
| E5 Combinado | E2 (0,05) + E3 + E4 | Comparar con E0 en los cuatro niveles |

## 10. Supuestos y limitaciones

| # | Supuesto o limitación | Justificación | Impacto |
|---|---|---|---|
| 1 | Los indicadores DSA (recall, precisión) son de la **UE** y **mezclan spam y no-spam**; se aplican a una comunidad no-spam | Es el único dato publicado sobre precisión de la IA | Si el no-spam tiene una precisión distinta, cambia la Tasa base de FP. Hacer sensibilidad |
| 2 | El informe general 2026 no se pudo obtener; su 10,37 % de "intervenciones retiradas" (cifra del plan) **no se usa**. La reversión se calibra con la mediana verificada de 2022–2024 (2,39 %), que es de 2022–2024 y no del periodo actual | Regla 4: no usar cifras no rastreables | Probar 0,60 %, 4,64 % y 16,36 %. Una reversión más alta reduce el castigo injusto percibido |
| 3 | Inconsistencias de la fuente: en DSA 2025 las quejas confirmadas y revertidas (638) no suman el total (334.874), y las medidas automatizadas de iniciativa propia (35.731) superan el total (30.740) | Ver `validacion.md` | No se usan esas cifras para calibrar |
| 4 | La prevalencia de contenido dañino, los mensajes por usuario, la productividad y el número de moderadores no se publican | Fuente única | Son SUPUESTOS con rango de sensibilidad |
| 5 | La confianza no se mide en ningún informe; se modela como índice de 0 a 1 | No hay encuesta (ajuste frente al plan de aprendizaje) | La reversión de apelaciones se usa como medida indirecta |
| 6 | Los falsos positivos que no se apelan no se observan en la fuente: las apelaciones aceptadas son una **cota inferior** del error | Restauradas/deshabilitadas: 0,10 %–0,72 % frente a 44,9 % de FP entre positivos automatizados (DSA 2025) | Esta brecha la debe interpretar el equipo |
| 7 | La cola se trata como homogénea (la mezcla de apelaciones y reportes es proporcional a sus entradas) | Simplificación | Se pierde el detalle de prioridades |
| 8 | La fuente es un informe escrito por la propia empresa | Única fuente permitida | Posible sesgo de presentación |
| 9 | La periodicidad es irregular y hay vacíos (Q4 2022 solo con totales citados; julio 2024 – febrero 2025 sin informe general) | Ver `validacion.md` | Las series semanales son promedios del periodo, no valores semana a semana |
| 10 | La curva FP–sensibilidad (elasticidad 1 sobre los momios) es una forma supuesta | Típica de clasificadores | Define cuán fuerte es "soluciones que fallan"; probar 0,5–2 |

---

## 11. Fase 2 – Modelos de Vensim construidos (14-11-2026)

> **SUPERADO:** esta sección describe la versión 1 (91/99 variables, 5 vistas). El equipo pidió simplificarla; la versión vigente está en `MODELO_VENSIM.md` (48/50 variables, una vista).

Archivos en `Modelos Vensim/`, generados por `scripts/06_modelos_vensim.py` y verificados con `scripts/07_verificacion_modelos.py`:

| Archivo | Variables | Check Model | Units Check | Simulación 104 semanas |
|---|---|---|---|---|
| `Discord_moderacion_actual.mdl` | 91 | 0 errores (4 avisos USE FLAG de los indicadores de calibración, que no alimentan otras variables) | **Units are OK** | Corre sin avisos |
| `Discord_moderacion_mejora.mdl` | 99 | 0 errores (los mismos 4 avisos) | **Units are OK** | Corre sin avisos |

Evidencia: `figuras/evidencia_vensim_actual_units_ok.jpg` y `figuras/evidencia_vensim_mejora_units_ok.jpg`.

> **Los `.mdl` son la versión vigente de las ecuaciones.** Las secciones 4 y 5 son el planteamiento inicial; los cambios están en la tabla 11.2.
> Los archivos deben renombrarse con los nombres de los integrantes, como exige el enunciado.

### 11.1 Cobertura del contenido visto en clase

| Contenido de clase | Dónde está en el modelo |
|---|---|
| Niveles, flujos, auxiliares y constantes | 6 niveles: Usuarios Activos, Confianza de Usuarios, Cola de Apelaciones, Cola de Casos, Moderadores en Formacion, Moderadores |
| **Niveles en serie** | Incorporacion de voluntarios → **Moderadores en Formacion** → Graduacion → **Moderadores** → Renuncias |
| **Niveles en paralelo** | **Cola de Apelaciones** y **Cola de Casos** comparten la Capacidad de revision (Fraccion de capacidad a apelaciones) |
| **Niveles heterogéneos acoplados** | Confianza de Usuarios (índice, información) modula los flujos de Usuarios Activos (personas) y la incorporación de moderadores |
| **Retraso material de 1.er orden** | `Llegada de reportes = DELAY1I(...)` (0,5 semanas) y el nivel explícito Moderadores en Formacion (4 semanas) |
| **Retraso material de 3.er orden** | `Llegada de apelaciones = DELAY3I(...)` (1 semana) |
| **Retraso de información puro** | `Reputacion externa = DELAY FIXED(Confianza de Usuarios, 6, 0.8)` |
| **Retraso de información / percepción** | `Carga percibida = SMOOTHI(Carga relativa, 4, 0.8)` y la Confianza de Usuarios como ajuste de primer orden (8 semanas) |
| Ciclos de refuerzo | R1 crecimiento de usuarios; R2 espiral de agotamiento (Carga percibida → Renuncias → Moderadores → Capacidad → Carga) |
| Ciclos de balance | B1 daño visible; B2 falsos positivos; B3 voluntariado; B4 drenaje de colas; B5 sensibilidad adaptativa (solo en la mejora) |
| No linealidad | `WITH LOOKUP` (efectos de la carga), `MIN` (capacidad), curva de falsos positivos sobre los momios S/(1−S) |
| Variabilidad e incertidumbre | `RANDOM NORMAL` en la fracción dañina (±10 %, semilla fija 1234); los SUPUESTOS tienen rango de sensibilidad |
| Prueba de política | `STEP(Incremento de sensibilidad, 26)`: ponga 0.017 para llevar la sensibilidad a 0,99 en la semana 26 |
| **Arquetipo: límites al crecimiento** | R1 (usuarios) frente a la capacidad de revisión (Moderadores × Productividad), que activa B1 |
| **Arquetipo: desplazamiento de la carga** | Solución sintomática: subir la sensibilidad de la IA (efecto inmediato sobre los falsos negativos). Solución de fondo: capacidad humana (formación con 4 semanas de retraso). Efecto secundario: los falsos positivos sobrecargan la cola y erosionan la solución de fondo por R2 |
| **Arquetipo: tragedia de los comunes** | Las dos colas paralelas (apelaciones y reportes, más la revisión previa en la mejora) consumen un recurso común, la capacidad de revisión. Cuando la carga pasa de 1, el recurso se degrada para todos (R2) |
| Soluciones que fallan (complementario, no visto en clase) | El mismo `STEP` de sensibilidad muestra el efecto de corto plazo frente al de largo plazo |

### 11.2 Cambios frente a las secciones 4 y 5

| Cambio | Motivo |
|---|---|
| La cola única se dividió en **Cola de Apelaciones** y **Cola de Casos** | Configuración en paralelo y tragedia de los comunes; además elimina el supuesto 7 (cola homogénea) |
| Nuevo nivel **Moderadores en Formacion** (Tiempo de formacion = 4 semanas, SUPUESTO) | Configuración en serie y retraso material explícito |
| Nuevas variables Reputacion externa (DELAY FIXED, 6 semanas), Carga percibida (SMOOTHI, 4 semanas), Llegada de apelaciones (DELAY3I, 1 semana) y Llegada de reportes (DELAY1I, 0,5 semanas) | Retrasos vistos en clase. Todos son SUPUESTOS de tiempo |
| Las renuncias y el reclutamiento responden a la **Carga percibida**, no a la carga instantánea | Retraso de percepción |
| Fraccion danina efectiva con `RANDOM NORMAL` | Variabilidad que pide el enunciado |
| Valores iniciales constantes para colas y retrasos (`Cola de apelaciones inicial` = 188, `Cola de casos inicial` = 61 / 106, `Apelaciones iniciales` = 552 / 525, `Reportes iniciales` = 181 / 135, `Carga percibida inicial` = 0,8) | Evitan la inicialización simultánea, que Vensim marca como error, y el aviso ACTIVE_INITIAL causado por el ruido aleatorio |
| La sensibilidad adaptativa (mejora) responde a la **Presion de cola** = (colas ÷ tiempo mínimo) ÷ capacidad | En la verificación, la versión basada en la carga percibida casi no reaccionaba frente al trabajo acumulado |
### 11.3 Modelo con mejora: cambios de parámetros y estructura

| Mejora                      | Variable                                    | Actual                    | Mejora                                                                       |
| --------------------------- | ------------------------------------------- | ------------------------- | ---------------------------------------------------------------------------- |
| 1. Sensibilidad adaptativa  | Sensibilidad efectiva del filtro            | = Sensibilidad del filtro | Se reduce 0,1 por cada unidad de Presion de cola sobre 1 (límites 0,70–0,99) |
| 2. Triage asistido por IA   | Productividad por moderador                 | 120                       | 160 piezas/(moderador·semana) (+33 %, SUPUESTO)                              |

### 11.4 Verificación numérica (no es el análisis de resultados)

Corrida con `07_verificacion_modelos.py` (Euler, dt = 0,25). El ruido usa el generador de Python, así que las cifras pueden diferir un poco de las de Vensim.
- Ninguna corrida tiene niveles negativos ni valores NaN.
- **t = 0 (modelo actual):** precisión 0,576 (la primera muestra aleatoria; sin ruido, 0,551), apelación 0,152, reversión 0,0232, reportes accionados 0,162, carga 0,81.
- **Series:** `processed/simulacion_actual.csv`, `simulacion_mejora.csv`, `simulacion_actual_S099.csv`, `simulacion_mejora_S099.csv`.
- **Gráficos de niveles y flujos:** `figuras/sim_niveles_base.png`, `sim_flujos_base.png`, `sim_niveles_S099.png`, `sim_flujos_S099.png`.

La **interpretación de estas simulaciones y la comparación entre modelos las redacta el equipo** (exigencia del curso). Para el informe se recomienda usar los gráficos generados en Vensim (Graph / Causes Strip) de su propia corrida.
