---
Código: AD-FUNC-06
Nombre: Onboarding
Versión: v1.0
Estado: **APPROVED FOR GATE REVIEW.** Aprobado por el Board (2026-07-14) tras incorporar la Prueba del Minuto Cero a la autoauditoría. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 45%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-06 — Onboarding

> Especifica el tramo entre el registro de un usuario nuevo y la primera pregunta real de ADÁN dentro de Nivel 1 (AD-FUNC-01). Por aplicación directa del mismo principio que ya rige AD-FUNC-03/04/05 (diseñar la emoción, el ritmo o la estrategia antes que su implementación): Onboarding no es un formulario, es la primera pregunta real llegando lo antes posible.

**Nivel de contenido:** el principio rector (sección 0); la creación progresiva de entidades (sección 3); la herencia de emoción/ritmo sin dimensiones nuevas (sección 4); la independencia de canal (sección 3.2); y "nada se pierde, se retoma desde el último paso real" (sección 3.3) son Principio Permanente. Los campos mínimos capturados antes de la primera pregunta (sección 2), la escalera específica de 7 etiquetas de Identidad Progresiva y sus hitos de confianza asociados (sección 3.1), y el objetivo de tiempo máximo (sección 3.4) son Decisión de Diseño, sujetos a AD-004 §1.

---

## 0. Principio rector: llegar a la primera pregunta real, no llenar un formulario

Un formulario largo antes de cualquier interacción real produce exactamente la anti-emoción que AD-FUNC-03 fijó para Nivel 1: **Juzgado**, no Comprendido — a nadie se le hace sentir escuchado pidiéndole que complete quince campos antes de poder decir una palabra sobre su problema. El principio de este documento es el inverso: capturar lo mínimo indispensable para poder dirigirse a la persona, y llegar a la primera pregunta real de Nivel 1 tan rápido como sea posible. Todo lo demás —perfil completo, detalles de la Empresa, estructura organizacional— se difiere para después de que la persona ya haya recibido valor real (la sensación de ser entendida), no antes.

**Verificación contra el Criterio de Existencia (AD-004 §3.1) de este mismo principio:** un formulario estático, por sí solo, no modifica el Gemelo Digital ni produce evidencia — es exactamente el tipo de paso que AD-004 §3.1 no admitiría como Funcionalidad si existiera aislado. Lo que hace que Onboarding pase el Criterio de Existencia es que su output real es el comienzo del Diagnóstico de Nivel 1 (AD-FUNC-01) — la conversación, no el formulario, es lo que cuenta.

**Nota de colisión de nombre (menor, no requiere renombre):** "Onboarding" aparece también en el Enterprise Taxonomy Workshop (cluster "Personas — Capital Humano") en el sentido de incorporación de un Empleado nuevo *dentro de la Empresa cliente* — un concepto de dominio de negocio, nunca formalizado como atributo explícito de Empleado en AD-005 §2.2. Es una colisión de bajo riesgo (los dos usos casi nunca aparecen en la misma frase: uno es la incorporación de un founder a ADÁN, el otro la incorporación de un empleado a la empresa del founder) y no se resuelve aquí — se señala para que una futura versión de AD-005 decida si el Onboarding/Offboarding de Empleado necesita atributo propio, sin bloquear este documento.

---

## 1. Qué es esta Funcionalidad, y dónde termina

Cubre exactamente el tramo "desde registro hasta la primera pregunta de ADÁN en Nivel 1" (mandato original del índice, v3.1). No es un Nivel separado ni un "Nivel 0" — **Los 7 Niveles quedaron congelados de forma definitiva por AD-FUNC-01** ("no volvería a discutir si son 6 o 7"), y este documento no reabre esa cuenta. Onboarding es el ritual de entrada *hacia* Nivel 1, no un octavo Nivel: termina en el instante exacto en que ADÁN formula su primera pregunta real sobre el Dolor del emprendedor, momento en el que el acompañamiento ya está dentro de Nivel 1 propiamente.

Lo que NO es:

- No es una pantalla de configuración de cuenta ni un cuestionario de perfil completo antes de empezar.
- No introduce un Nivel adicional ni una etapa previa con su propia numeración.
- No crea todas las entidades del dominio de una sola vez "por si acaso" — las crea progresivamente, a medida que hay evidencia real que las justifica (sección 3).

---

## 2. Qué se captura antes de la primera pregunta real

Mínimo indispensable para poder dirigirse a la persona y empezar la conversación — todo lo demás se difiere:

| Se captura antes de la primera pregunta | Se difiere para después |
|---|---|
| Nombre o forma de dirigirse a la persona | Estructura organizacional completa (Departamento, Cargo, Rol Funcional — AD-005 §2.2) |
| Medio de contacto (correo u otro) | Detalle financiero (Activo, Pasivo, Ingreso, Gasto — AD-005 §2.6) |
| Una señal mínima de que existe una Empresa o intención de crearla (no más) | Nombre legal, Razón Social, Jurisdicción, Tipo Societario (AD-005 §2.1) — se completan cuando la conversación los produce de forma natural, no antes |

Ninguno de estos campos es una entidad nueva — Usuario y Usuario Principal (AD-006 §4) ya existen para representar exactamente a la persona que se registra; Empresa (AD-005 §2.1) recién se instancia formalmente en la sección 3.

---

## 3. Creación progresiva de entidades

Ninguna entidad de AD-005/AD-006 se crea de golpe al registrarse — se crean en el momento en que hay evidencia real que las justifica, nunca antes por conveniencia de formulario:

1. **Usuario** (AD-006 §4) nace en el instante del registro — es lo mínimo indispensable para que exista una sesión.
2. **Usuario Principal** se confirma cuando la persona indica que es responsable de una Empresa (no antes) — puede coincidir con el paso 1 en el caso más común (un founder solo).
3. **Proyecto** y **Workspace** (AD-006 §4) nacen junto con la primera respuesta real sobre el Dolor — no antes, porque antes de esa respuesta no hay todavía nada que acompañar.
4. **Empresa** (AD-005 §2.1) se instancia con lo mínimo real disponible en ese momento (a veces solo una intención, si la Empresa todavía no existe formalmente — Ley 1, Origen) y se completa progresivamente vía versionado (AD-002 §1.7), nunca exigiendo todos sus atributos de una vez.

Esta secuencia es, en sí misma, la aplicación operativa de "recursos internos primero" y "diagnóstico antes que formulario" — el mismo tipo de disciplina que AD-FUNC-05 ya aplicó a estrategias, aplicada aquí a la creación de entidades.

### 3.1 Identidad progresiva y construcción de confianza

La relación entre una persona y ADÁN madura por etapas — no son entidades nuevas, son **etiquetas de relación derivadas**, calculadas sobre evidencia que ya existe en entidades ya definidas, exactamente el mismo tratamiento que AD-005 §4 ya le dio a "Etapa del Ciclo de Vida" (derivada de Edad×Madurez, nunca almacenada como campo propio). Ninguna de las siete etiquetas se guarda como estado independiente — se leen, en cualquier momento, de lo que el Gemelo Digital ya contiene.

**Verificación de colisión de nombre, antes de fijar la escalera:** dos de las etiquetas propuestas por el Board colisionan con términos ya fijados en documentos congelados, y se ajustan aquí antes de adoptarlas:

- **"Founder"** colisiona con la razón exacta por la que AD-006 renombró esa misma palabra a "Usuario Principal" (Hallazgo 1 de AD-006): la Declaración de Misión de AD-001 cubre empresas de cualquier edad, no solo startups en fundación, y "Founder" reintroduce ese sesgo. Se reemplaza por **"Responsable de Empresa"** — describe exactamente lo mismo (quien confirma responsabilidad sobre una Empresa) sin la connotación de "solo está empezando".
- **"CEO"** colisiona con el **CEO Agent** ya definido en AD-FUNC-02 (el Agente que preside el Board Room y es cómo ADÁN mismo habla ahí) — usar "CEO" para una etiqueta del humano generaría ambigüedad real entre "el CEO Agent de ADÁN" y "el humano en etapa CEO". Se reemplaza por **"Líder Activo"** — conserva la idea de alguien que ya no solo está fundando sino dirigiendo con evidencia real detrás, sin la colisión.

La escalera resultante, y el hito de confianza (evidencia ya existente, no nueva) que habilita cada transición — aplicando el mismo principio de Patrón B (Progreso Secuencial, AD-CMP-01/AD-008) que ya gobierna el avance entre Niveles, ahora a un conjunto de etiquetas distinto, sin inventar un mecanismo de avance nuevo:

| Etiqueta | Hito de confianza que la habilita |
|---|---|
| Anónimo | — (estado inicial, sin registro) |
| Visitante | Primer contacto — cualquier interacción, incluso sin registro completo |
| Usuario | Registro mínimo completado (sección 2) |
| Responsable de Empresa | Confirma responsabilidad sobre una Empresa (sección 3, paso 2) |
| Líder Activo | Primer valor entregado y primera promesa cumplida — el primer Entregable/Diagnóstico real de Nivel 1 (AD-FUNC-01) llega tal como se prometió |
| Cliente Activo | Primera Decisión de Negocio real registrada (AD-FUNC-02 §2.5 / AD-FUNC-05 §10) |
| Embajador | Primera recomendación de ADÁN aceptada y sostenida en el tiempo — **el mecanismo concreto de referido/incentivo queda explícitamente fuera de este documento**, es materia de WO-100 (Business Architecture), no de esta especificación de producto |

### 3.2 Onboarding conversacional — independiente del canal

Ninguna parte de este documento asume texto como único canal. La primera pregunta real, y la respuesta del cliente, pueden llegar por voz, texto, documento, audio, video o imagen — lo que importa es el contenido (evidencia), no el medio. Esto no requiere una entidad nueva: un documento que el cliente sube durante Onboarding (ej. un Plan de Negocios ya existente) es simplemente un **Documento** (AD-005 §2.4) con `Origen: recibido de un tercero`; una respuesta por voz es, para efectos de este documento, el mismo contenido de una **Conversación** (AD-006 §4) capturado por un canal distinto. Si en el futuro ADÁN necesita capacidad de voz, el mecanismo natural es reutilizar **ARQAI** como Motor del Ecosistema ya existente (AD-000 §3) — nunca construir un runtime de voz propio, seria una duplicación directa que el Principio de No Duplicación de Capacidad (AD-000 §4) ya prohíbe. El mecanismo técnico de ingestión por canal (voz a texto, lectura de documentos, etc.) es responsabilidad de un futuro AD-ARQ, no de este documento.

### 3.3 Recuperación de Onboarding

Si alguien abandona antes de llegar a la primera pregunta real, ADÁN no reinicia desde cero — retoma exactamente desde el último paso real completado de la secuencia de la sección 3 (Usuario → Usuario Principal → Proyecto/Workspace → Empresa). No se mide el abandono en porcentajes abstractos: se lee directamente cuál de esas cuatro entidades ya existe y cuál no, lo mismo que ya se necesita para construir el resto del documento.

- **Qué faltó:** comparación directa contra la tabla de la sección 2 (qué campos mínimos no se completaron).
- **Dónde abandonó:** cuál paso de la secuencia de la sección 3 es el último real completado.
- **Cómo retomarlo:** aplicación directa de la Regla de no repetición (AD-CMP-04 §4) — se confirma lo ya sabido, nunca se vuelve a preguntar, y de la Regla 1.5 de AD-002 ("nada se pierde") — el registro parcial nunca se descarta, solo se completa.

No se introduce ningún mecanismo nuevo — este comportamiento ya estaba implícito en la secuencia de la sección 3 y en reglas ya congeladas; esta subsección solo lo hace explícito.

### 3.4 Tiempo máximo objetivo

Meta declarada: **menos de 30 segundos entre el registro mínimo (sección 2) y la primera pregunta real de Nivel 1.** Es Decisión de Diseño, no Principio Permanente — el número exacto puede ajustarse con datos reales, lo que no puede desaparecer es el principio de fondo: si el tiempo de Onboarding no se mide, no se optimiza (aplicación directa de la disciplina de evidencia de AD-002 a la propia operación de ADÁN, no a la Empresa del cliente — este objetivo es un indicador operativo de ADÁN, distinto por naturaleza del Indicador de negocio que AD-005 §2.5 define para la Empresa cliente). La instrumentación real para medir este tiempo es responsabilidad de un futuro AD-ARQ/AD-OPS — este documento solo fija la meta.

---

## 4. Emoción y ritmo — heredados, no nuevos

Onboarding no introduce una emoción ni un ritmo propios — hereda directamente los ya fijados para Nivel 1 en documentos congelados, evitando duplicar lo que ya existe (Principio de Emergencia):

- **Emoción:** Comprendido, no Juzgado (AD-FUNC-03 §1, Nivel 1) — el criterio de diseño de la sección 0 es la aplicación literal de esta emoción al primer contacto.
- **Ritmo:** Inmediato (AD-FUNC-04 §1, Nivel 1) — respuestas rápidas y ágiles desde el primer intercambio, coherente con "un Agente visible, se siente como una sola persona atenta".

Ningún AD-UX que diseñe Onboarding puede declarar una emoción o ritmo distintos a estos sin abrir una nueva versión de AD-FUNC-03/04 — Onboarding no tiene autoridad para definir los suyos propios.

---

## 5. Memoria desde el primer instante

Desde el registro, ya existen dos de las cinco capas de contexto de AD-CMP-04: **Global** (lo que ADÁN ya sabe de cualquier Proyecto anterior, si el correo coincide con un registro previo) y, en cuanto nace el Proyecto (sección 3, paso 3), la capa **Proyecto**. La Regla de no repetición de AD-CMP-04 §4 aplica desde el primer intercambio: si algo ya se sabe (ej. un registro previo abandonado), Onboarding no vuelve a preguntarlo — lo confirma.

---

## 6. Verificación contra la Regla de Entidades y el Principio de Emergencia

Ninguna entidad nueva. Usuario, Usuario Principal, Proyecto, Workspace (AD-006 §4) y Empresa (AD-005 §2.1) ya existen — este documento solo especifica el orden y el momento en que cada una se instancia, no agrega ninguna. Emoción y ritmo se heredan de AD-FUNC-03/04 sin duplicarse (sección 4). El único concepto que este documento introduce —"captura mínima antes de la primera pregunta real"— es una regla de secuencia, no una entidad ni un objeto de datos.

La Identidad Progresiva (sección 3.1) tampoco es una entidad nueva — se verificó explícitamente contra el mismo patrón que AD-005 §4 ya usó para "Etapa del Ciclo de Vida": una etiqueta derivada y calculada, nunca almacenada. Se detectaron y corrigieron dos colisiones de nombre antes de fijarla ("Founder" contra el Hallazgo 1 de AD-006; "CEO" contra el CEO Agent de AD-FUNC-02) — ninguna de las dos requirió tocar el documento de origen, solo ajustar la etiqueta nueva. Onboarding conversacional (3.2) reutiliza Documento y Conversación ya existentes, más ARQAI como Motor del Ecosistema ya definido — ninguna entidad ni motor nuevo. Recuperación de Onboarding (3.3) reutiliza AD-002 §1.5 y AD-CMP-04 §4 sin mecanismo nuevo. El objetivo de tiempo (3.4) es una meta operativa, no una entidad de dominio.

---

## 7. Verificación contra el Criterio de Existencia (AD-004 v1.1 §3.1)

| Condición | ¿Se cumple? | Cómo |
|---|---|---|
| ¿Modifica el Gemelo Digital? | Sí | Usuario Principal, Proyecto y Empresa nacen aquí, versionados desde el primer instante (AD-002 §1.7) |
| ¿Mejora el conocimiento del cliente? | Sí, aunque mínimamente | El cliente pasa de "anónimo" a "reconocido y a punto de ser escuchado" — el valor real llega en Nivel 1, que este documento acelera en vez de posponer |
| ¿Produce evidencia útil para la siguiente decisión? | Sí | El registro mínimo y el momento exacto de creación de cada entidad son, en sí mismos, la primera evidencia temporal del Proyecto (cuándo empezó, con qué información real disponible) |

---

## 8. Autoauditoría obligatoria (10 preguntas)

1. **¿Contradice AD-000, AD-001 o AD-002?** No — refuerza AD-001 §14 ("confianza calmada, nunca urgencia artificial") aplicándolo al primer contacto, antes de que exista todavía una relación.
2. **¿Todo concepto nuevo está justificado?** El único concepto nuevo es una regla de secuencia ("mínimo antes, resto después"), no una entidad — verificado en sección 6. La Identidad Progresiva (3.1) se verificó explícitamente contra el mismo patrón que "Etapa del Ciclo de Vida" (AD-005 §4) — derivada, no almacenada.
3. **¿Hay duplicación con un documento existente?** No — emoción y ritmo se heredan explícitamente de AD-FUNC-03/04 en vez de redefinirse (sección 4); se verificó explícitamente la colisión de nombre "Onboarding" contra el Enterprise Taxonomy Workshop (sección 0), y dos colisiones más en esta revisión ("Founder" contra el Hallazgo 1 de AD-006, "CEO" contra el CEO Agent de AD-FUNC-02, sección 3.1) — las tres documentadas y resueltas, ninguna ignorada.
4. **¿Qué impacto tiene sobre documentos futuros?** AD-FUNC-08 (User Journey Map, depende explícitamente de este documento en el índice original) debe construir el recorrido completo sobre esta base, incluida la Identidad Progresiva como insumo directo para marketing/gamificación futuros. AD-UX deberá diseñar la interfaz de registro respetando el mínimo de la sección 2, el soporte multicanal de 3.2, y la recuperación de 3.3, sin agregar campos por conveniencia.
5. **¿Introduce un riesgo arquitectónico nuevo?** Dos: (a) capturar "lo mínimo" puede tensionarse con futuras necesidades de verificación/anti-fraude si ADÁN alguna vez maneja pagos en Onboarding; (b) la etiqueta "Embajador" (3.1) puede presionarse comercialmente hacia un mecanismo de referidos — se declara explícitamente que ese mecanismo, si se construye, debe evitar el patrón de riesgo legal de esquema multinivel ya señalado para ADÁN en general, y queda fuera de esta especificación de producto (WO-100).
6. **¿El Confidence Level es honesto?** 45% — bajó de 48% a propósito: el alcance creció (Identidad Progresiva, multicanal, recuperación, meta de tiempo) sin un solo caso real ejecutado que lo respalde.
7. **Prueba "si este documento desapareciera":** Onboarding se diseñaría, por defecto, como un formulario de perfil completo antes de cualquier conversación, asumiría texto como único canal, y no sabría retomar un registro abandonado — perdería exactamente las cuatro capas que esta revisión agregó.
8. **Prueba "válido en 10 años":** el principio ("llegar a la primera pregunta real lo antes posible, capturar lo mínimo, diferir el resto, no perder nunca lo ya avanzado, ser indiferente al canal") no depende de qué tecnología de registro o de captura de voz/imagen exista en el mercado — es una decisión de confianza, no de interfaz.
9. **¿Se verificó contra colisiones de nombre?** Sí — "Onboarding" contra el Enterprise Taxonomy Workshop (sección 0); "Founder" contra AD-006; "CEO" contra AD-FUNC-02 (ambas en 3.1).
10. **¿La autoauditoría se entrega junto con el documento?** Sí, esta sección.
11. **Prueba del Minuto Cero** *(agregada en esta revisión, por instrucción explícita del Board):* ¿una persona completamente desconocida puede iniciar una conversación útil con ADÁN en menos de un minuto, sin leer instrucciones ni recibir capacitación? **Sí.** La secuencia completa lo garantiza por construcción, no por casualidad: la captura mínima de la sección 2 (nombre y contacto, nada más) no exige leer nada antes de empezar; el principio rector de la sección 0 obliga a llegar a la primera pregunta real sin pasos intermedios; el ritmo heredado (Inmediato, sección 4) prohíbe cualquier demora artificial; y la independencia de canal (3.2) significa que la persona puede simplemente empezar a hablar o escribir, sin que exista una única forma "correcta" de hacerlo que deba aprenderse primero. Esta prueba resume, en una sola pregunta verificable, el principio rector completo del documento — y por eso se conserva como parte permanente de la autoauditoría, no como una pregunta de una sola vez.

---

## Dependencias

- AD-FUNC-01 Los 7 Niveles (dónde termina Onboarding y empieza Nivel 1; los 7 Niveles no se reabren)
- AD-FUNC-03 Experience Engine (emoción de Nivel 1 heredada: Comprendido, no Juzgado)
- AD-FUNC-04 Gamification Engine (ritmo de Nivel 1 heredado: Inmediato)
- AD-CMP-01 Progresión entre Niveles (Onboarding no es una entidad con Patrón B propio — es previo a que cualquier Nivel comience a evaluarse)
- AD-CMP-04 Memoria y Contexto (capas Global y Proyecto activas desde el registro; Regla de no repetición)
- AD-006 §4 (Usuario, Usuario Principal, Proyecto, Workspace, Conversación)
- AD-005 §2.1, §2.4, §4 (Empresa creación progresiva; Documento con Origen; patrón de "Etapa del Ciclo de Vida" reutilizado para Identidad Progresiva)
- AD-002 §1.5, §1.7 (nada se pierde; versionado progresivo)
- AD-CMP-01 (Patrón B, Progreso Secuencial — patrón reutilizado para los hitos de confianza de 3.1)
- AD-000 §3, §4 (ARQAI como Motor del Ecosistema para voz; Principio de No Duplicación de Capacidad)
- AD-FUNC-02 §2.5 (primera Decisión de Negocio, hito de "Cliente Activo")
- AD-004 v1.1 §3.1 (Criterio de Existencia)

## Documentos relacionados

- AD-FUNC-08 User Journey Map (aún no construido) — depende explícitamente de este documento según el índice original (v3.1); hereda la Identidad Progresiva (3.1) como insumo directo
- AD-FUNC-09 Learning Engine (aún no construido) — la desviación entre el tiempo objetivo (3.4) y el tiempo real, y las etiquetas de Identidad Progresiva, son evidencia futura de aprendizaje
- AD-UX (Fase 2) — diseño visual del registro mínimo, soporte multicanal, y recuperación de Onboarding
- AD-ARQ (Fase 2, futuro) — ingestión técnica por canal (voz/documento/imagen) e instrumentación del tiempo objetivo (3.4)
- WO-100 Business Architecture (futura) — cualquier mecanismo concreto de referidos/incentivos ligado a "Embajador" (3.1)

## Impacto sobre otros módulos

1. Ningún AD-UX de registro puede exigir más campos que los listados en la sección 2 sin abrir una nueva versión de este documento.
2. AD-FUNC-08, cuando se escriba, hereda el punto de partida del User Journey ("descubrimiento hasta suscripción activa") desde el final exacto de este documento, incluida la Identidad Progresiva.
3. Ningún AD-UX puede diseñar Onboarding asumiendo un único canal de entrada (sección 3.2).
4. Cualquier mecanismo de referidos ligado a "Embajador" queda prohibido de diseñarse en esta categoría de documento (Funcionalidades) — es materia de negocio, sujeta además al riesgo ya señalado de esquema multinivel.

## Riesgos

- **Riesgo de tensión futura con verificación/anti-fraude.** Si ADÁN llega a manejar pagos o compromisos financieros desde Onboarding, "capturar lo mínimo" podría tensionarse con necesidades de verificación de identidad — no se resuelve en este documento, queda señalado para cuando exista esa necesidad real.
- **Riesgo de presión comercial futura por agregar campos de calificación de lead** ("perfilar mejor para ventas") antes de la primera pregunta real — este documento fija la barrera del principio rector explícitamente para prevenir ese sesgo, mismo patrón que AD-FUNC-04/05 ya aplicaron a sus propios riesgos comerciales.
- **Riesgo de que el mecanismo de "Embajador" (3.1) derive en un esquema de referidos multinivel** — riesgo ya señalado para ADÁN en general (evaluación inicial de negocio); este documento no diseña ningún mecanismo de incentivo, solo la etiqueta narrativa, y declara explícitamente que el mecanismo concreto (si existe) debe evitar ese patrón y vivir en WO-100, no aquí.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

- Si el Onboarding/Offboarding de Empleado (dominio de negocio, distinto de este documento) necesita un atributo propio en una futura versión de AD-005 — señalado en sección 0, no bloquea este documento.
- Mecanismo técnico de ingestión multicanal (AD-ARQ) e instrumentación del tiempo objetivo de 30 segundos (AD-ARQ/AD-OPS) — Fase 2.
- Mecanismo concreto (si lo hay) detrás de la etiqueta "Embajador" — WO-100, explícitamente fuera de esta especificación de producto.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: principio rector (llegar a la primera pregunta real, no a un formulario completo), captura mínima antes de la primera pregunta con el resto diferido, creación progresiva de Usuario/Usuario Principal/Proyecto/Empresa basada en evidencia real, emoción y ritmo heredados sin duplicar AD-FUNC-03/04, verificación de colisión de nombre contra el Enterprise Taxonomy Workshop | Sexto documento de Funcionalidades, primero construido en un solo ciclo tras el cierre de AD-FUNC-05 (Ready for Gate Review) |
| v1.0 — Revisión 2 | 2026-07-14 | Se agregó Identidad Progresiva (7 etiquetas derivadas, no entidades, con dos colisiones de nombre detectadas y corregidas: "Founder"→"Responsable de Empresa", "CEO"→"Líder Activo") unificada con un modelo de construcción de confianza vía hitos de evidencia (reutiliza Patrón B de AD-CMP-01, sin mecanismo nuevo). Se agregó Onboarding conversacional independiente del canal (voz/texto/documento/audio/video/imagen), reutilizando Documento y Conversación ya existentes más ARQAI como Motor del Ecosistema. Se agregó Recuperación de Onboarding (retomar desde el último paso real, nunca reiniciar), aplicación directa de AD-002 §1.5 y AD-CMP-04 §4. Se agregó objetivo de tiempo máximo (<30 segundos) como meta operativa medible, distinta del Indicador de negocio de AD-005 | Observaciones del Board tras revisar la v1.0: faltaba identidad progresiva, independencia de canal, recuperación de abandono, modelo de confianza explícito y una meta de tiempo medible |
| v1.0 — APPROVED FOR GATE REVIEW | 2026-07-14 | Se agregó la Prueba del Minuto Cero como pregunta 11 de la autoauditoría obligatoria (¿una persona desconocida puede iniciar una conversación útil con ADÁN en menos de un minuto, sin instrucciones ni capacitación?). Aprobación formal del Board — sin más cambios de contenido. Se congela como dependencia estable del resto del árbol | Instrucción explícita del Board: última incorporación antes de cerrar el documento, resume en una sola pregunta el principio rector completo |
