# Informe final: Moderación automatizada con IA en Discord

---

## 1. Contextualización del sistema complejo

Discord es una plataforma que permite a las personas comunicarse en tiempo real por medio de servidores. Para que las comunidades puedan funcionar de manera adecuada, la plataforma cuenta con un sistema de moderación automática apoyado en inteligencia artificial, que revisa los mensajes que publican los usuarios.

El funcionamiento general del sistema es el siguiente:

1. Los usuarios publican mensajes dentro de los servidores.
2. El filtro de IA revisa el contenido y decide si lo bloquea o permite que se publique.
3. Cuando un mensaje se bloquea, el usuario tiene la posibilidad de apelar la decisión.
4. También se pueden hacer denuncias cuando algún contenido dañino logra pasar el filtro.
5. Tanto las apelaciones como las denuncias llegan a una cola que deben revisar moderadores humanos voluntarios. Esta revisión tiene una capacidad limitada.
6. Después de revisar cada caso, los moderadores deciden si mantienen el bloqueo o si permiten que el contenido vuelva a estar disponible.
7. La confianza de los usuarios depende, en parte, de la cantidad de contenido dañino que encuentran y de los bloqueos que se hacen por equivocación.
8. Esa confianza influye en la llegada de nuevos usuarios, en la cantidad de personas que abandonan la plataforma y en quienes están dispuestos a trabajar como moderadores voluntarios.

Para el modelo se tomó como referencia una comunidad de 100.000 usuarios activos. El análisis se enfoca en contenido dañino que no corresponde a spam, como el acoso, los mensajes de odio, los riesgos para la seguridad infantil y el contenido violento.

El spam se deja como parte del contexto, ya que representa entre el 94,6 % y el 99,6 % de las cuentas deshabilitadas, pero se elimina de forma proactiva en el 99 % de los casos.

---

## 2. Identificación del problema

**Problema principal:** el filtro de inteligencia artificial de Discord busca evitar que se publique contenido dañino, pero no siempre toma las decisiones correctas. Puede cometer dos tipos de errores:

- **Falsos positivos (bloqueos por error):** sucede cuando el sistema bloquea un mensaje que realmente no incumple las reglas. Esto hace que los usuarios presenten apelaciones, aumenta el trabajo de los moderadores y puede hacer que las personas pierdan confianza en la plataforma.
- **Falsos negativos (contenido dañino que pasa el filtro):** ocurre cuando el filtro no identifica un mensaje que sí debería bloquear. Como consecuencia, el contenido dañino sigue visible, los usuarios presentan denuncias y también se afecta la confianza de la comunidad.

El problema es que los dos tipos de casos terminan llegando al mismo equipo de moderación humana, que tiene una capacidad limitada para revisarlos. Si empiezan a llegar más casos de los que los moderadores pueden atender, la carga de trabajo aumenta, algunos se agotan y terminan renunciando. Al haber menos moderadores, la capacidad de revisión disminuye todavía más y la situación empeora.

Esto representa un **arquetipo de desplazamiento de la carga**. La idea es que intentar solucionar el problema haciendo el filtro más estricto puede reducir el contenido dañino que se escapa, pero al mismo tiempo aumenta los bloqueos incorrectos. Estos generan más apelaciones y saturan la revisión humana, que es justamente la parte del sistema que se necesita fortalecer para solucionar el problema de fondo.

**Subsistema analizado:** se estudia una comunidad representativa de 100.000 usuarios, junto con el filtro de IA, las colas de apelaciones y denuncias y el grupo de moderadores humanos.

**Elementos que se relacionan dentro del sistema:** usuarios activos, contenido dañino, filtro de IA, bloqueos incorrectos, apelaciones, denuncias, moderadores, confianza de la comunidad y reputación externa.

---

## 3. Análisis sistémico

### 3.1 Propiedades emergentes

- **Colapso cuando aumenta la presión:** cuando se aumenta la sensibilidad del filtro hasta 0,99 sin darle más capacidad al equipo de moderación, el sistema termina colapsando. En la simulación, los usuarios pasan de 100.000 a solamente 4.780 en 104 semanas. Este resultado no se explica mirando únicamente el filtro o las colas, sino por la relación entre los falsos positivos, la acumulación de casos, la renuncia de moderadores y la pérdida de confianza.
- **Mayor estabilidad al aplicar mejoras:** cuando se utiliza una sensibilidad que se ajusta según la situación y se agrega triage asistido por IA, el sistema logra soportar mejor la misma prueba de estrés. Al final quedan 86.194 usuarios y la confianza se mantiene en 0,69.

### 3.2 Interacciones no lineales

- Los **bloqueos por error** aumentan de forma no lineal cuando sube la sensibilidad del filtro. Esto se representa con la expresión `Sensibilidad / (1 − Sensibilidad)`. Cuando la sensibilidad se acerca a 1, un pequeño aumento puede provocar un crecimiento bastante grande de los falsos positivos.
- Las **renuncias de moderadores** también aumentan de forma acelerada cuando la carga supera el nivel normal. Para representarlo se usa `MIN(4, MAX(1, Carga percibida) ^ 2)`. Esto significa que el agotamiento no crece siempre al mismo ritmo, sino que se vuelve mucho más fuerte cuando la carga es alta.

### 3.3 Ciclos de retroalimentación

En el modelo se identificaron 3 ciclos de refuerzo y 7 ciclos de balance. Los que tienen mayor relación con el problema son:

- **R2 (espiral de agotamiento):** cuando aumenta la carga de trabajo, también aumentan las renuncias. Esto deja menos moderadores disponibles, reduce la capacidad de revisión y termina haciendo que la carga sea todavía mayor.
- **B5 (daño visible / límites al crecimiento):** si hay más usuarios, también puede haber más contenido dañino que logra pasar el filtro. Esto genera más denuncias y molestia, reduce la confianza y hace que lleguen menos usuarios nuevos.
- **B6 (bloqueos injustos):** cuando aumentan los bloqueos por error, también crece la molestia de los usuarios. Esto disminuye la confianza, provoca que algunas personas abandonen la plataforma y, por lo tanto, reduce la cantidad de usuarios.

### 3.4 Variabilidad

La cantidad de contenido dañino que genera cada usuario es un supuesto del modelo. Se estableció en 0,02 piezas por usuario a la semana y se hicieron pruebas con diferentes valores para revisar cómo podía cambiar el resultado.

También se utilizaron valores estimados para algunos tiempos de retraso, como los relacionados con la reputación, el entrenamiento de moderadores y la percepción de la carga de trabajo.

### 3.5 Incertidumbre

Hay varios aspectos que se deben tener en cuenta al interpretar los resultados:

- Los datos del DSA corresponden a la Unión Europea y combinan información de spam con contenido que no es spam.
- No se cuenta con un informe general de 2026.
- La confianza de los usuarios no aparece medida directamente en los informes, por lo que se representa mediante un índice supuesto entre 0 y 1.
- No todos los falsos positivos se pueden identificar, porque algunos usuarios no presentan apelaciones. Por eso, las restauraciones de contenido son solamente una referencia mínima de los errores que pudo cometer el filtro.

### 3.6 Comportamiento contraintuitivo

Un resultado que puede parecer contradictorio es que hacer el filtro más estricto no necesariamente mejora el sistema a largo plazo. Al subir la sensibilidad se reduce de inmediato la cantidad de contenido dañino que logra pasar, pero también aumentan los falsos positivos.

Con el tiempo, estos bloqueos incorrectos generan más apelaciones, las colas se llenan y los moderadores empiezan a tener una carga de trabajo mayor. Esto puede provocar renuncias y reducir la capacidad de revisión. Al final, el sistema puede terminar dejando pasar más contenido dañino del que se esperaba.

Este comportamiento corresponde al arquetipo de **desplazamiento de la carga**, porque se intenta solucionar el problema de manera rápida con un filtro más estricto, pero esa decisión termina debilitando la solución de fondo: tener suficiente capacidad humana para revisar los casos.

---

## 4. Construcción del modelo en Vensim

### 4.1 Variables del sistema

El modelo se construyó en Vensim utilizando las siguientes variables:

**Niveles (6):** Usuarios activos, Confianza de la comunidad, Apelaciones pendientes, Denuncias pendientes, Moderadores en entrenamiento y Moderadores activos.

**Flujos (10):** Usuarios que llegan, Usuarios que se van, Cambio de confianza, Apelaciones que llegan, Apelaciones resueltas, Denuncias que llegan, Denuncias resueltas, Voluntarios nuevos, Moderadores graduados y Moderadores que renuncian.

**Auxiliares (12):** Apelaciones aceptadas, Bloqueos por error, Capacidad de revisión, Carga percibida, Confianza deseada, Contenido nocivo, Molestia por bloqueos injustos, Molestia por contenido nocivo, Nocivo bloqueado, Nocivo que se escapa, Precisión del filtro y Reputación externa.

**Constantes (20):** Contenido nocivo por usuario, Factor de error del filtro, Fracción de bloqueados que apela, Fracción de nocivo denunciado, Mensajes sanos por usuario, Probabilidad de corregir un error, Productividad por moderador, Retraso de la reputación, Sensibilidad del filtro IA, Tasa de abandono por desconfianza, Tasa de crecimiento base, Tasa de voluntariado, Tasa normal de renuncia, Tiempo de entrenamiento, Tiempo de reacción de los usuarios, Tiempo mínimo de revisión, Tiempo para ajustar la confianza, Tiempo para percibir la carga, Tolerancia a bloqueos injustos y Tolerancia al contenido nocivo.

**Mejoras adicionales (3):** Sensibilidad efectiva del filtro, Ajuste automático de sensibilidad y Presión de cola.

### 4.2 Relaciones causales con polaridad

A cada flecha del modelo se le asignó una polaridad positiva (+) o negativa (−), según la manera en que se relacionan las variables.

En el modelo actual se verificaron 49 de las 66 polaridades y en el modelo con mejoras se verificaron 53 de las 66. Las polaridades restantes no se podían comprobar directamente en el tiempo inicial (`t=0`), debido a los retrasos de funciones como `DELAY` y `SMOOTH`, o a ramas de `MIN/MAX` que todavía no estaban activas. En esos casos, el signo se definió teniendo en cuenta la lógica del sistema.

### 4.3 Unidad de tiempo

La unidad de tiempo utilizada es la **semana (Week)**. Se escogió porque los cambios en la confianza de los usuarios y el agotamiento de los moderadores no suelen ocurrir de un momento a otro, sino que se van dando durante varias semanas. Además, las tasas utilizadas en el modelo se ajustaron a esta unidad.

La simulación se realizó durante 104 semanas, es decir, aproximadamente dos años. El tiempo mínimo solicitado era de 70 semanas. El `TIME STEP` utilizado fue de 0,25.

### 4.4 Supuestos del modelo (explícitos y justificados)

| Supuesto | Valor | Justificación |
|---|---|---|
| Usuarios activos iniciales | 100.000 | Los informes no presentan una comunidad representativa para este ejercicio, así que se tomó un número redondo como punto de partida. |
| Confianza inicial | 0,8 | Es un valor supuesto, porque los informes no miden directamente la confianza de los usuarios. |
| Moderadores activos iniciales | 6 | El DSA no publica cuántas personas moderan Discord. |
| Moderadores en entrenamiento iniciales | 0,48 | Se ajustó este valor para que el modelo comenzara en una situación de equilibrio. |
| Contenido nocivo por usuario | 0,02 piezas/semana | Se tomó como referencia 1 mensaje dañino por cada 1.000 mensajes, considerando 20 mensajes por usuario a la semana. |
| Mensajes sanos por usuario | 19,98 piezas/semana | Corresponde a los mensajes restantes de los 20 mensajes semanales considerados. |
| Fracción de nocivo denunciado | 0,5 | Es un supuesto, ya que no se encontró publicado en los informes. |
| Fracción de bloqueados que apela | 0,155 | Dato: mediana de la tasa de apelación de 2022–2023, según los informes generales. |
| Probabilidad de corregir un error | 0,0532 | Valor calibrado a partir de una reversión inicial de 2,39 %, correspondiente a la mediana entre Q1 de 2022 y H1 de 2024. |
| Productividad por moderador (actual) | 120 piezas/moderador/semana | Es un supuesto calibrado para obtener una carga inicial de 0,8. |
| Productividad por moderador (mejora) | 160 piezas/moderador/semana | Es un supuesto que representa un aumento del 33 % gracias al triage asistido por IA. |
| Tiempo mínimo de revisión | 0,34 semanas | Dato: mediana de 57,34 horas, según el DSA 2024. |
| Tiempo de entrenamiento | 4 semanas | Valor supuesto para representar el tiempo que tarda un voluntario en prepararse. |
| Tiempo para percibir la carga | 4 semanas | Valor supuesto. |
| Tiempo para ajustar la confianza | 8 semanas | Valor supuesto. |
| Retraso de la reputación | 6 semanas | Valor supuesto. |
| Tiempo de reacción de los usuarios | 1 semana | Valor supuesto. |
| Sensibilidad del filtro IA | 0,973 | Dato: recall del DSA 2025, página 9. |
| Precisión objetivo del filtro | 0,551 | Dato: precisión del DSA 2025, página 9. |

---

## 5. Ecuaciones y unidades de medida

Las ecuaciones completas se encuentran en los archivos `.mdl` y también están documentadas en `datos/MODELO_VENSIM.md`. En la siguiente tabla se muestran las ecuaciones principales utilizadas en el modelo:

| Variable | Ecuación (Vensim) | Unidad |
|---|---|---|
| Usuarios activos | `INTEG(Usuarios que llegan - Usuarios que se van, 100000)` | usuarios |
| Usuarios que llegan | `Usuarios activos * Tasa de crecimiento base * Reputacion externa` | usuarios/Week |
| Usuarios que se van | `Usuarios activos * Tasa de abandono por desconfianza * (1 - Confianza de la comunidad)` | usuarios/Week |
| Confianza de la comunidad | `INTEG(Cambio de confianza, 0.8)` | Dmnl (0–1) |
| Cambio de confianza | `(Confianza deseada - Confianza de la comunidad) / Tiempo para ajustar la confianza` | 1/Week |
| Confianza deseada | `MAX(0, 1 - Molestia por contenido nocivo - Molestia por bloqueos injustos)` | Dmnl |
| Contenido nocivo | `Usuarios activos * Contenido nocivo por usuario` | piezas/Week |
| Nocivo bloqueado | `Contenido nocivo * Sensibilidad efectiva del filtro` | piezas/Week |
| Nocivo que se escapa | `Contenido nocivo * (1 - Sensibilidad efectiva del filtro)` | piezas/Week |
| Bloqueos por error | `Usuarios activos * Mensajes sanos por usuario * Factor de error del filtro * Sensibilidad efectiva / (1 - Sensibilidad efectiva)` | piezas/Week |
| Apelaciones pendientes | `INTEG(Apelaciones que llegan - Apelaciones resueltas, 186)` | piezas |
| Apelaciones que llegan | `DELAY3((Nocivo bloqueado + Bloqueos por error) * Fraccion de bloqueados que apela, Tiempo de reaccion de los usuarios)` | piezas/Week |
| Apelaciones resueltas | `MIN(Apelaciones pendientes / Tiempo minimo de revision, Capacidad de revision * XIDZ(Apelaciones pendientes, Apelaciones pendientes + Denuncias pendientes, 0.5))` | piezas/Week |
| Denuncias pendientes | `INTEG(Denuncias que llegan - Denuncias resueltas, 9)` | piezas |
| Denuncias que llegan | `DELAY1(Nocivo que se escapa * Fraccion de nocivo denunciado, Tiempo de reaccion de los usuarios)` | piezas/Week |
| Denuncias resueltas | `MIN(Denuncias pendientes / Tiempo minimo de revision, Capacidad de revision * XIDZ(Denuncias pendientes, Apelaciones pendientes + Denuncias pendientes, 0.5))` | piezas/Week |
| Capacidad de revision | `Moderadores activos * Productividad por moderador` | piezas/Week |
| Carga percibida | `SMOOTH(XIDZ(Apelaciones que llegan + Denuncias que llegan, Capacidad de revision, 10), Tiempo para percibir la carga)` | Dmnl |
| Moderadores activos | `INTEG(Moderadores graduados - Moderadores que renuncian, 6)` | moderadores |
| Moderadores que renuncian | `Moderadores activos * Tasa normal de renuncia * MIN(4, MAX(1, Carga percibida) ^ 2)` | moderadores/Week |
| Sensibilidad efectiva del filtro (mejora) | `Sensibilidad del filtro IA / (1 + Ajuste automatico de sensibilidad * MAX(0, Presion de cola - 1))` | Dmnl |
| Presion de cola | `XIDZ((Apelaciones pendientes + Denuncias pendientes) / Tiempo minimo de revision, Capacidad de revision, 10)` | Dmnl |

Todas las ecuaciones pasaron la comprobación **Units Check** en Vensim PLE 10.5.2.

---

## 6. Simulación del sistema actual

### 6.1 Condiciones de simulación

Para simular el funcionamiento actual del sistema se utilizaron estas condiciones:

- Horizonte de simulación: 104 semanas.
- `TIME STEP`: 0,25.
- Sensibilidad del filtro: 0,973 (valor fijo y calibrado).
- Productividad por moderador: 120 piezas por semana.

### 6.2 Resultados del caso base

| Semana | Usuarios activos | Confianza | Apelaciones pendientes | Denuncias pendientes | Moderadores activos | Carga percibida |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 100.000 | 0,80 | 186 | 9 | 6,0 | 0,80 |
| 26 | 105.333 | 0,80 | 195,6 | 9,6 | 6,05 | 0,83 |
| 52 | 110.949 | 0,80 | 206,0 | 10,2 | 6,21 | 0,85 |
| 78 | 116.865 | 0,80 | 217,0 | 10,7 | 6,45 | 0,86 |
| 104 | 123.096 | 0,80 | 228,5 | 11,3 | 6,74 | 0,87 |

 En el escenario normal, el sistema logra mantenerse estable. La cantidad de usuarios aumenta poco a poco, la confianza se mantiene en 0,80 y las colas de revisión siguen funcionando sin llegar a saturarse.

Además, el modelo reproduce desde el inicio los indicadores utilizados para la calibración: precisión de 0,551, tasa de apelación de 0,155 y reversión de 0,0239.

### 6.3 Gráficos

Los gráficos de niveles y flujos correspondientes al escenario base se encuentran en estas rutas:

- `datos/figuras/sim_niveles_base.png`
- `datos/figuras/sim_flujos_base.png`

---

## 7. Propuesta de mejora

### 7.1 Descripción de la mejora

Para mejorar el funcionamiento del modelo se plantearon dos cambios:

1. **Sensibilidad adaptativa del filtro:** en lugar de mantener siempre el mismo nivel de sensibilidad, el filtro ajusta su comportamiento cuando la presión de las colas supera el valor de 1. En ese momento reduce su sensibilidad efectiva para evitar que sigan llegando demasiados casos a revisión.
2. **Triage asistido por IA:** se aumenta la productividad de cada moderador de 120 a 160 piezas por semana. Esto representa una mejora del 33 % en la capacidad de revisión y ayuda a reducir la carga de trabajo.

### 7.2 Justificación de los cambios

- Mantener una sensibilidad alta y fija puede generar muchos falsos positivos, especialmente porque estos aumentan de forma no lineal. Al permitir que el filtro se ajuste según la presión de las colas, se busca conservar la detección cuando hay capacidad suficiente y reducirla cuando el equipo de revisión está llegando a su límite.
- El triage asistido por IA permite que los moderadores revisen más casos en el mismo tiempo, sin depender de incorporar más personas. Esto es importante porque formar a un nuevo moderador toma alrededor de cuatro semanas.

### 7.3 Simulación de la mejora (104 semanas)

**Caso base (sensibilidad 0,973):** los resultados son prácticamente iguales a los del modelo actual. Esto sucede porque la presión de las colas no llega a superar el valor de 1 y, por lo tanto, el ajuste automático de sensibilidad no necesita activarse.

**Prueba de estrés (sensibilidad 0,99 desde la semana 26):**

| Semana | Usuarios actual | Usuarios mejora | Confianza actual | Confianza mejora | Moderadores actual | Moderadores mejora |
|---|---:|---:|---:|---:|---:|---:|
| 26 | 105.333 | 105.333 | 0,80 | 0,80 | 6,05 | 6,05 |
| 52 | 62.202 | 102.382 | 0,08 | 0,73 | 0,07 | 6,01 |
| 78 | 17.652 | 95.259 | 0,00 | 0,72 | 0,42 | 5,78 |
| 104 | **4.780** | **86.194** | **0,00** | **0,69** | **0,05** | **5,42** |

**Análisis de los resultados:** cuando se aumenta la sensibilidad del filtro a 0,99, el modelo actual termina colapsando. Pierde aproximadamente el 95 % de sus usuarios y la confianza llega a cero.

En cambio, el modelo con las mejoras logra resistir mucho mejor esta situación. Después de las 104 semanas conserva 86.194 usuarios y una confianza de 0,69. La sensibilidad adaptativa evita que los falsos positivos llenen las colas de revisión (ciclo B8), mientras que el triage ayuda a mantener la capacidad de los moderadores.

### 7.4 Comparación con la situación actual

| Dimensión | Actual | Mejora | Diferencia |
|---|---:|---:|---:|
| Usuarios en semana 104 (estrés) | 4.780 | 86.194 | +81.414 |
| Confianza en semana 104 (estrés) | 0,00 | 0,69 | +0,69 |
| Moderadores en semana 104 (estrés) | 0,05 | 5,42 | +5,37 |
| Carga percibida (caso base) | 0,87 | 0,65 | −0,22 |

---

## 8. Evaluación de alternativas

Durante el desarrollo del modelo se revisaron diferentes opciones para intentar mejorar su funcionamiento:

| Alternativa | Descripción | Decisión | Motivo |
|---|---|---|---|
| E0: Actual | Mantener el sistema sin cambios. | Base | Sirve como punto de comparación para las demás pruebas. |
| E1: Sensibilidad 0,90 vs 0,99 | Probar diferentes niveles de sensibilidad del filtro. | Adoptada (S099) | Permite mostrar el arquetipo de desplazamiento de la carga. |
| E2: Zona gris (revisión humana previa) | Enviar el 5 % de las decisiones a revisión humana antes de aplicarlas. | **Descartada** | No mejoraba el caso base, superaba el límite de 50 variables y hacía más difícil explicar el modelo individualmente. |
| E3: Triage asistido por IA | Aumentar la productividad de 120 a 160 piezas por moderador. | **Adoptada** | Ayuda a reducir el factor que limita la capacidad de revisión sin tener que agregar más personal. |
| E4: Sensibilidad adaptativa | Reducir la sensibilidad cuando la presión de las colas aumenta. | **Adoptada** | Evita que las colas se saturen cuando el sistema está bajo estrés. |
| E5: Combinado (zona gris + triage + adaptativa) | Aplicar todas las mejoras al mismo tiempo. | **Descartada** | La zona gris no aportaba suficiente beneficio como para justificar su inclusión. |

**¿Por qué se descartó la zona gris?** En las primeras pruebas, esta alternativa generaba resultados prácticamente iguales a los del modelo actual en el caso base y tampoco mostraba una mejora importante durante las pruebas de estrés. Además, agregaba 8 variables y una tercera cola que también utilizaba la capacidad de los moderadores. Esto hacía que el modelo fuera más complicado de explicar durante la sustentación individual, sin ofrecer una mejora que justificara esa complejidad.

---

## 9. Recomendaciones finales

1. **No aumentar la sensibilidad del filtro sin revisar primero la capacidad de los moderadores.** Pasar de una sensibilidad de 0,973 a 0,99 sin aplicar otros cambios puede llevar al sistema a colapsar en menos de dos años de simulación.

2. **Utilizar una sensibilidad adaptativa para controlar la presión de las colas.** La idea es que el filtro pueda reducir automáticamente su sensibilidad cuando la presión de revisión supere 1. De esta forma se evita que aumenten demasiado los falsos positivos y que los moderadores terminen sobrecargados.

3. **Aprovechar la IA para apoyar el trabajo de los moderadores.** El triage asistido por IA permite aumentar la productividad de 120 a 160 piezas revisadas por semana, lo que mejora la capacidad del sistema sin necesidad de incorporar más personas.

4. **Vigilar la presión de las colas de revisión.** Esta variable sirve como una señal de alerta, ya que cuando supera el valor de 1 el sistema empieza a entrar en una situación de riesgo.

5. **Tener claros los supuestos utilizados en el modelo y explicar cómo afectan los resultados.** Los valores que más conviene revisar mediante pruebas de sensibilidad son la cantidad de contenido dañino, la productividad de cada moderador, el número inicial de moderadores y los tiempos de retraso.
