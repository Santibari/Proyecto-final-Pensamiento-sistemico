# Bitácora de aprendizaje: modelo en Vensim de la moderación con IA en Discord

Proyecto final PSO 2026-2 · Universidad de La Sabana Equipo: \[Nombres y apellidos de los integrantes\] Fecha: noviembre de 2026 Fuente única de datos: https://discord.com/safety-transparency

## 1. Alcance y uso de IA

Esta bitácora registra el proceso seguido para construir el modelo de dinámica de sistemas en Vensim (modelo actual y modelo con mejora) sobre la moderación automatizada con IA en una comunidad de Discord. Para cada etapa se documentan las consultas realizadas (incluido el uso de IA), la información obtenida, las decisiones tomadas (qué se acepta, qué se descarta y por qué) y los ajustes frente al plan de aprendizaje.

Usamos IA (Claude Code) como asistente a lo largo del proyecto: lectura del plan y del enunciado, extracción y validación de cifras de los informes de Discord, redacción del planteamiento del modelo y construcción y verificación de los archivos .mdl. Las decisiones finales sobre qué aceptar o descartar las tomó el equipo, y la interpretación de los resultados se redacta en el informe final. Regla de trabajo: ninguna cifra entra al modelo si no se puede rastrear a un informe y una página.

## 2. Fase 1: de los informes de Discord a los insumos del modelo

### 2.1 Fuentes

| Consulta o acción (herramienta) | Información obtenida | Decisión | Justificación |
| --- | --- | --- | --- |
| Revisar la carpeta del proyecto, el plan de implementación y el enunciado del caso final (Claude Code) | Faltaban el plan y el enunciado. El enunciado exige simulación de mínimo 70 unidades de tiempo, bitácora, supuestos explícitos, modelos en Vensim y entrega solo por la plataforma universitaria | Acepta ambos documentos como rectores; no se trabaja sin ellos | Definen el alcance y los requisitos de la entrega |
| Consultar la página oficial de transparencia de Discord (Claude Code) | 15 enlaces a .pdf y .zip en cdn.discordapp.com; coinciden con la tabla del plan más un ECA en portugués | Acepta los enlaces; descarta el ECA en portugués | Tiene el mismo contenido que la versión en inglés y solo sirve de contexto; se deja registrado por trazabilidad |
| Obtener los informes | La descarga automática no fue posible porque la red cortaba la conexión con el CDN. Se descargaron a mano 10 .zip: Q1 a Q3 2022, Q1 a Q4 2023, H1 2024, DSA 2024 y DSA 2025. Faltan el informe general 2026, el TCO 2026 y el ECA Brasil (EN) | Acepta la descarga manual con hash SHA-256 y método registrados en MANIFIESTO.csv; descarta usar espejos o cachés | Se conserva la trazabilidad a la fuente oficial |
| Revisar el contenido de los .zip | Cada informe general trae PDF más CSV; los DSA traen 8 CSV temáticos más PDF; el DSA 2025 incluye la tabla de medios automatizados | Acepta los CSV oficiales como fuente primaria y los PDF para verificar y citar la página | Evita errores de lectura de tablas en PDF |
| Cifras de trimestres sin informe propio (Q4 2021 y Q4 2022) | Aparecen como “trimestre anterior” en informes posteriores. Q4 2022: 153.883 no-spam y 36.825.143 spam. Q4 2021: 1.127.220 y 19.794.949 | Acepta, marcadas como “(citado)” | Son cifras publicadas por Discord, aunque su informe no está en la página |
| Cuentas de spam deshabilitadas y reportes de spam, que no están en los CSV (Claude Code) | Se extrajeron del texto de los PDF, por ejemplo 35.456.553 cuentas de spam en H1 2024 | Acepta, con la página de cada cifra | Permite citar la fuente exacta |

### 2.2 Validación y problemas de la fuente

| Consulta o acción (herramienta) | Información obtenida | Decisión | Justificación |
| --- | --- | --- | --- |
| Comparar H1 2024 con las 8 cifras de control del plan | Las 8 coinciden: 35.813.609 cuentas deshabilitadas (35.456.553 spam y 357.056 no-spam), 41.002 servidores, 29.495.313 reportes, 1,85 % apelan, 1.705 restauradas (2,59 %) | Acepta | Coincidencia exacta con CSV y PDF |
| Sumar categorías y compararlas con el total publicado | De 92 combinaciones periodo–métrica, las 92 cuadran | Acepta | Los CSV son internamente consistentes tras corregir Q3 2023 |
| Tabla “Accounts Disabled” del CSV de Q3 2023 | Los valores estaban corridos una fila. El PDF muestra Child Safety 128.153 (p. 13) y extremismo violento 8.300 (p. 19) | Ajusta: se usan las cuentas por categoría de la tabla Appeals del mismo CSV (suma 260.461) | Esa tabla sí cuadra con el PDF |
| Revisar anomalías de la fuente | Advertencias de Q3 2022 idénticas a las de Q1 2023; en DSA 2025, confirmadas más revertidas suman 638 de 334.874 quejas; las medidas automatizadas por iniciativa propia (35.731) superan el total (30.740); reinstalación de Q2 2022 en 0,60 % | Ajusta: se documentan en validacion.md y no se usan para calibrar sin advertencia | Son cifras internamente inconsistentes |
| Revisar cambios de definición entre informes | Reportes: formulario web (2022 a Q2 2023) y luego app con spam incluido. Base de apelación: cuentas deshabilitadas (2022–2023) y luego cuentas sancionadas distintas (H1 2024). Reversión: cuentas restauradas y luego intervenciones retiradas (2026) | Ajusta: se reportan por separado y no se comparan de forma directa | Evita mezclar medidas distintas |
| Normalizar todo a tasa semanal | Semanas = días del periodo ÷ 7 (trimestre ≈ 12,9 a 13,1; H1 2024 = 26; DSA 2024 = 45,6; DSA 2025 = 52,1). Ejemplo H1 2024: 13.733 cuentas no-spam deshabilitadas por semana y 1.363.714 de spam | Acepta | La semana es la unidad de tiempo del modelo |
| Calcular 88 indicadores clave | Apelación no-spam de 10,3 % a 21,9 % (2022–2023); reversión de 0,6 % a 4,6 % (mediana ≈ 2,4 %); restauradas sobre deshabilitadas de 0,10 % a 0,72 %; DSA 2024: 16,4 % de quejas revertidas; DSA 2025: precisión 55,1 % y recall 97,3 % (p. 9) | Acepta, con fórmula, informe y página por indicador | Son la base de calibración del modelo |
| Graficar los datos (6 gráficos) | Spam y no-spam difieren unas 100 veces en escala; hay un cambio de canal de reportes en Q2 2023 | Acepta paneles separados y línea de corte en Q2 2023 | Evita el doble eje y mezclar definiciones |
| Cifras de control del informe general 2026 | No se encontró el PDF; se trataba de 6 cifras (47.832.832; 34.304.587; 26.174.231; 585.307; 60.686; 10,37 %) | Descarta | No se pueden rastrear a un informe ni a una página |

## 3. Fase 1B: planteamiento del modelo

Antes de abrir Vensim, redactamos el planteamiento del modelo con apoyo de IA. Delimitación: comunidad representativa de 100.000 usuarios, contenido dañino no-spam (el spam queda como contexto), unidad de tiempo semana, horizonte de 104 semanas y TIME STEP de 0,25.

| Consulta o acción (herramienta) | Información obtenida | Decisión | Justificación |
| --- | --- | --- | --- |
| Parámetros sin dato en la fuente | Los informes no publican prevalencia de contenido dañino, volumen de mensajes, plantilla de moderadores ni confianza. Valores propuestos: fracción dañina 0,001; 20 mensajes por usuario por semana; productividad 150 piezas por moderador por semana; 6 moderadores; confianza inicial 0,8; renuncia 0,02 por semana; ajuste de confianza en 8 semanas | Acepta como SUPUESTO, con rango de sensibilidad | No existe dato; cada parámetro queda marcado como DATO, CALIBRADO o SUPUESTO |
| Calibrar la tasa base de falsos positivos con DSA 2025 | Precisión 55,1 % y recall 97,3 % (p. 9) dan una tasa base de falsos positivos de 0,000794 | Acepta con advertencia | Es el único indicador publicado de precisión de la IA, pero es de la UE y mezcla spam con no-spam |
| Forma de la curva de falsos positivos (prueba numérica fuera de Vensim) | Con la primera forma (potencia 3 de la sensibilidad), subir la sensibilidad casi no aumentaba los falsos positivos | Ajusta: curva sobre los momios S/(1−S), con elasticidad 1 (SUPUESTO) | Es más realista cuando la sensibilidad se acerca a 1 |
| Meta de reversión de apelaciones | El plan pedía cerca de 10 % (cifra de 2026, no verificable). El rango verificado va de 2,39 % (mediana 2022–2024) a 16,36 % (DSA 2024) | Primero se calibró a 10 %; al descartar 2026 se recalibró a 2,39 % (probabilidad de corregir error 0,0333; castigo injusto de referencia 0,0157). Se dejan 0,60 %, 4,64 % y 16,36 % como sensibilidad | El 2,39 % es dato verificado, solo no-spam y con la misma definición que la variable del modelo; el 16,36 % mezcla spam, por eso solo sirve de sensibilidad |
| Efecto de la recalibración | En t=0: precisión 0,551, apelación 0,156, reversión 0,024. Los escenarios se comportan igual: base estable, colapso con S = 0,99 y contención con sensibilidad adaptativa | Acepta | Las apelaciones aceptadas (cerca de 13 por semana) son pequeñas frente a los falsos positivos (cerca de 1.586 por semana) |
| Escenario de sensibilidad del plan (0,7 frente a 0,9) | El recall real es 0,973 | Ajusta: se propone 0,90 frente a 0,99 | El rango del plan quedaba lejos del valor actual |
| Redactar el planteamiento del modelo | 4 niveles, 7 flujos, ecuaciones en sintaxis Vensim con unidades, tabla DATO/CALIBRADO/SUPUESTO, ciclos R1, R2 y B1 a B5, arquetipos candidatos (límites al crecimiento, desplazamiento de la carga, tragedia de los comunes), metas de calibración, escenarios, 10 supuestos y limitaciones | Acepta | Es la fase 1B del plan y no incluye interpretación de resultados |
| Redactar el resumen descriptivo de los datos | Datos disponibles y vacíos, evolución 2022–2024, evidencia de falsos positivos (8 fuentes) y 7 limitaciones | Acepta | Sin conclusiones, como pide el plan |

## 4. Fase 2: construcción del modelo en Vensim

### 4.1 Versión 1 (modelo complejo)

| Consulta o acción (herramienta) | Información obtenida | Decisión | Justificación |
| --- | --- | --- | --- |
| Ejecutar la fase 2 con apoyo de IA | El plan reservaba esta fase al equipo; hubo instrucción explícita de hacerla con IA | Acepta | Prevalece la instrucción directa; la interpretación de resultados sigue siendo del equipo |
| Comparar el planteamiento con el contenido de clase (pensamiento sistémico) | Faltaban retrasos (DELAY1, DELAY3, DELAY FIXED, SMOOTH), niveles en serie y en paralelo, el arquetipo tragedia de los comunes, el desplazamiento de la carga como arquetipo principal y la variabilidad que pide el enunciado | Ajusta: se rehace la estructura | Se exige al menos un elemento de cada tipo visto en clase |
| Estructura nueva de la versión 1 | Moderadores en Formación (serie); Cola de Apelaciones y Cola de Casos (paralelo); DELAY1I, DELAY3I, DELAY FIXED, SMOOTHI, RANDOM NORMAL y STEP. Modelo actual de 91 variables, modelo con mejora de 99, 5 vistas | Acepta | Cubre todo el contenido de clase; los tiempos de retraso son SUPUESTOS |
| Errores al revisar la versión 1 en Vensim | (a) Inicialización simultánea de SMOOTH y de la Cola de Casos. (b) Aviso ACTIVE\_INITIAL por el ruido aleatorio. (c) Diagrama con ids desordenados, vistas sin encabezado y flechas con punto (0,0) | Ajusta: (a) SMOOTHI con valores iniciales constantes; (b) DELAY1I y DELAY3I con valor inicial; (c) diagrama corregido | Check Model debía pasar sin errores |
| La sensibilidad adaptativa respondía poco | Con S = 0,99 el modelo con mejora también colapsaba, porque la carga percibida apenas pasaba de 1 | Ajusta: se usa Presión de cola (trabajo acumulado ÷ capacidad) | Refleja el atraso real de la cola |
| Check Model y Units Check en Vensim PLE 10.5.2 | Ambos modelos: 0 errores, 4 avisos USE FLAG, “Units are OK”; simulan 104 semanas | Acepta | Es requisito del enunciado la validación del modelo y de las unidades |

### 4.2 Versión 2 (simplificada, vigente)

| Consulta o acción (herramienta) | Información obtenida | Decisión | Justificación |
| --- | --- | --- | --- |
| Pedido de simplificar el modelo | La versión 1 tenía 91 y 99 variables y 5 vistas. El equipo pidió máximo 50 variables, una sola vista, flechas curvas con polaridad en todas, nombres comprensibles y conservar los arquetipos | Acepta | Un modelo más pequeño es más fácil de defender en la sustentación individual |
| Rediseño de la versión 2 | Modelo actual con 48 variables: 6 niveles, 10 flujos, 12 auxiliares y 20 constantes. Se mantienen serie, paralelo, DELAY1, DELAY3, DELAY FIXED, SMOOTH y los tres arquetipos | Acepta; descarta el ruido aleatorio, los valores iniciales auxiliares, los indicadores aparte y la reducción de reportes | Cumple el límite sin perder el contenido de clase |
| Nombres en lenguaje común | “Bloqueos por error” (falsos positivos), “Nocivo que se escapa” (falsos negativos), “Nocivo bloqueado” (verdaderos positivos), “Apelaciones pendientes” y “Denuncias pendientes” | Acepta | Pedido del equipo; facilita la sustentación |
| Tolerancia a bloqueos injustos con error de factor 10 | Se usó 0,01573 en lugar de 0,1573; la confianza deseada daba 0 en t=0 y la comunidad colapsaba en el escenario base | Ajusta: se corrige a 0,1573 (molestia inicial 0,1) | La verificación numérica detectó el error |
| Explosión numérica con sensibilidad 0,99 | Renuncias multiplicadas por la carga al cuadrado sin tope: moderadores negativos y valores de 1e50 | Ajusta: se limita el multiplicador con MIN(4, carga²) (SUPUESTO) | Evita valores sin sentido |
| Revisión de polaridades (efecto directo, todo lo demás fijo) | De 66 relaciones, 49 coinciden, 16 no son verificables en t=0 (retrasos o ramas MIN/MAX inactivas) y 1 depende de la convención (tiempo de ajuste) | Acepta; las 16 se fijaron por razonamiento y la convención queda escrita (“−” significa respuesta más lenta) | Queda documentado en MODELO\_VENSIM.md |
| Check Model y Units Check de la versión 2 en Vensim | Modelos actual y con mejora: “Model is OK” sin avisos y “Units are OK”; simulan 104 semanas. En t=0: precisión 0,551, apelación 0,155, reversión 0,0239 y carga 0,80; el escenario base es estable | Acepta | Coincide con los datos de DSA 2025 y de los informes 2022–2024 |

### 4.3 Modelo con mejora y decisión de quitar la zona gris

El modelo con mejora queda con exactamente dos mejoras:

1. Sensibilidad adaptativa del filtro: la sensibilidad efectiva baja cuando la Presión de cola supera 1 (ciclo B8 de autorregulación).
2. Triage asistido por IA: la productividad por moderador sube de 120 a 160 piezas por moderador por semana.

En la revisión final detectamos que el modelo con mejora aún incluía una tercera mejora, la “zona gris” (revisión humana previa), que no estaba documentada en MODELO\_VENSIM.md ni en el planteamiento del modelo.

| Consulta o acción    | Información obtenida                                                                                                                                                                       | Decisión                                                                                                                                                                                                                                                               | Justificación                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Evaluar la zona gris | No mejoraba el caso base (curvas idénticas a las del modelo actual), llevaba el modelo a unas 58 variables frente al límite de 50 y dificultaba la defensa individual (35 % de la rúbrica) | Descarta. Se eliminan 7 variables (casos en zona gris, revisión previa, revisiones previas resueltas, fracción zona gris, enriquecimiento de la zona gris, acierto de la revisión previa y bloqueos injustos aplicados) y se revierten las referencias en 6 ecuaciones | Aporta complejidad sin mejora visible y no estaba documentada |

## 5. Resultados de las simulaciones finales

Se corrieron ambos modelos ya sin la zona gris y se verificaron con una simulación numérica independiente. Estos son los datos observados; la interpretación completa la redacta el equipo en el informe final.

- Modelo actual (48 variables): sin valores negativos ni NaN. En t=0, precisión 0,551, apelación 0,155, reversión 0,0239 y carga 0,80. El caso base es estable durante 104 semanas.
- Modelo con mejora (51 variables): sin valores negativos ni NaN, con la misma calibración en t=0.
- Prueba de estrés (la sensibilidad sube a 0,99 en la semana 26):
  - Modelo actual: en la semana 104 quedan 4.780 usuarios, la confianza cae a 0,00 y los moderadores a 0,05 (colapso).
  - Modelo con mejora: en la semana 104 hay 86.194 usuarios, confianza 0,69 y 5,42 moderadores (resistencia).
- Verificación cruzada con PySD sobre la versión 2: usuarios activos en la semana 52 = 110.949,88 y en la semana 104 = 123.096,97, idénticos a la verificación propia.
- Lectura preliminar: la mejora no cambia el caso base, pero vuelve al sistema resiliente frente al arquetipo de desplazamiento de la carga.

## 6. Simulación web de apoyo (fuera de la rúbrica)

Construimos una simulación web como apoyo para la sustentación (cambiar de escenario en vivo). Lee los .mdl oficiales de Vensim y no sustituye al modelo.

| Consulta o acción (herramienta) | Información obtenida | Decisión | Justificación |
| --- | --- | --- | --- |
| Elegir cómo hacer la simulación | Opciones: PySD con FastAPI, o una página solo en JavaScript | Acepta PySD con FastAPI | Mantiene el .mdl de Vensim como modelo oficial y funciona sin internet el día de la sustentación |
| Rediseñar la página porque no se entendía | Se agregan escenarios con un clic, diagrama de Vensim en vivo, comparación actual frente a mejora, frases en lenguaje común con el dato real al lado y una ciudad 3D ilustrativa | Acepta | Pedido del equipo |
| Mapa 3D por país | Los informes no tienen datos de moderación por país: los generales son globales, el DSA es un agregado de la UE y el ECA no se obtuvo | Descarta el mapa por país; se acuerda una ciudad 3D ilustrativa sin datos por servidor ni por país | Exigiría inventar cifras |
| Re-simulación a mitad de la corrida | Reiniciar los retrasos (DELAY y SMOOTH) hacía que difiriera un poco de Vensim | Ajusta: todos los escenarios se simulan desde la semana 0 | Cualquier escenario se reproduce exactamente en Vensim cambiando una constante |

## 7. Resumen de lo descartado y por qué

| Descartado | Motivo |
| --- | --- |
| Cifras de control del informe general 2026 | No hay PDF ni página a la que rastrearlas |
| ECA en portugués | Duplica la versión en inglés |
| Espejos y cachés para descargar informes | La fuente única es la página oficial de Discord |
| Meta de reversión de 10 % | Se basaba en una cifra de 2026 sin verificar |
| Escenario de sensibilidad 0,7 frente a 0,9 | Quedaba lejos del recall real (0,973) |
| Usar cifras con anomalías para calibrar | Son inconsistentes entre sí o con el total publicado |
| Comparar directamente periodos con definiciones distintas | Mide cosas diferentes |
| Modelo de la versión 1 (91 y 99 variables, 5 vistas, ruido aleatorio) | Demasiado complejo para defender individualmente y por encima del límite de 50 variables |
| Reducción de reportes y zona gris en el modelo con mejora | No mejoraban el caso base, subían el número de variables y no estaban documentadas |
| Mapa 3D por país | Los informes no tienen datos por país |

## 8. Ajustes frente al plan de aprendizaje

- Medición de la confianza: no hubo medición directa ni encuesta. La confianza se modela como un índice SUPUESTO porque los informes no la miden, y se usan la reversión de apelaciones y los indicadores DSA como medida indirecta del error.
- Escenario de sensibilidad: el plan sugería 0,7 frente a 0,9; se ajustó a 0,90 frente a 0,99 alrededor del valor actual, porque el recall real es 0,973.
- Meta de reversión: pasó de cerca de 10 % a 2,39 % al no poder verificar el informe 2026, con sensibilidades de 0,60 %, 4,64 % y 16,36 %.
- Fuentes: se trabajó con 10 de los 13 informes previstos, sin el informe 2026, y las tablas DSA por categoría quedaron sin procesar.
- Contenido de clase: al comparar el planteamiento con la materia, incorporamos retrasos, niveles en serie y en paralelo y los tres arquetipos que no estaban en la primera estructura.
- Complejidad del modelo: pasamos de 91 y 99 variables a 48 y 51 para poder defender el modelo de forma individual.
- Modelo con mejora: queda con dos mejoras (sensibilidad adaptativa y triage asistido por IA); se descartó la zona gris.
- Rol de la IA: el plan reservaba al equipo la construcción de los modelos en Vensim; se hizo con apoyo de IA por instrucción directa. Se mantiene que la interpretación de resultados, la comparación entre modelos y la defensa de supuestos son del equipo.
- Simulación web: se agregó como apoyo a la sustentación, aunque no está en la rúbrica.
