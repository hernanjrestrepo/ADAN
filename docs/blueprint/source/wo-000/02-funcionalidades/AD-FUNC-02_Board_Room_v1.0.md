---
Código: AD-FUNC-02
Nombre: Board Room
Versión: v1.0
Estado: Aprobado y congelado
Confidence Level: 58%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-02 — Board Room

> Especifica la funcionalidad de comité ejecutivo: CEO/CTO/CFO/CMO/Legal/Producto/Operaciones debatiendo con cliente y terceros invitados, votaciones y actas. Este documento resuelve, de forma explícita, algo que ningún documento anterior había respondido directamente: **quién tiene la última palabra cuando el Board, ADÁN y el cliente no coinciden.**

**Nivel de contenido:** mixto. La jerarquía de autoridad (sección 2) y el Flujo Maestro de Orquestación (sección 3) son Principio Permanente. La mecánica visual de votación es Decisión de Diseño para AD-UX.

---

## 0. Verificación contra el Principio de Emergencia

Antes de escribir el Flujo Maestro de Orquestación y el mecanismo de resolución de conflictos, se verificó si ya emergían de AD-CMP-02 (Consenso Multiagente) y AD-CMP-03 (Comportamiento de Decisiones). **Parcialmente.** AD-CMP-02 ya resuelve el consenso *interno* entre Agentes en el flujo conversacional normal — eso no se repite aquí. Lo que ni AD-CMP-02 ni AD-CMP-03 resuelven es qué ocurre cuando la discrepancia sobrevive ese proceso y llega, formalmente, a una sesión de Board Room con el cliente presente — ahí el vacío es real: hace falta una secuencia explícita (Flujo Maestro) y una jerarquía de autoridad explícita para el caso de tres posiciones distintas (Board, Agente individual, cliente). Eso es lo que este documento agrega — nada más.

---

## 1. Qué es el Board Room

Una sesión formal, visible al cliente, donde los Agentes especializados (CEO, CTO, CFO, CMO, Legal, Producto, Operaciones) deliberan sobre una decisión de peso suficiente para justificar hacerlas visibles (a diferencia de la conversación normal, donde son invisibles por defecto, AD-001 §1). El CEO Agent preside — es, dentro de esta funcionalidad, la forma concreta en que "ADÁN habla": no existe una voz de "ADÁN" separada de lo que el Board Room produce. Puede incluir terceros invitados (ej. un asesor externo del cliente) sin autoridad de voto.

**Cuándo se convoca un Board Room formal** (en vez de resolverse en la conversación normal vía AD-CMP-02): cuando la discrepancia entre Agentes es material y no se resuelve por evidencia ponderada (AD-CMP-02 §2), o cuando la decisión afecta una transición de Nivel, un compromiso financiero relevante, o un Riesgo de severidad alta (AD-005 §3).

---

## 2. Jerarquía de autoridad — quién tiene la última palabra

Se responde distinguiendo **dos autoridades distintas**, porque tratarlas como una sola es la fuente más probable de confusión:

### 2.1 Autoridad de ejecución — quién puede hacer que algo pase

**El cliente (Usuario Principal), sin excepción.** Es la aplicación literal del principio inviolable de AD-001 §12: ninguna decisión importante avanza sin su aprobación explícita. Ni el Board, ni el CEO Agent, ni la cantidad de evidencia a favor de una opción, tienen autoridad para ejecutar una Decisión (Patrón A, AD-008) sin que el cliente la mueva de `Presentada` a `Aprobada`.

### 2.2 Autoridad de fundamentación — qué tan respaldada está cada opción

**La evidencia, no la jerarquía.** El Board no vota por preferencia — vota ponderando evidencia (AD-CMP-02 §2, Meta-Principio 3 del Anexo). El resultado de esa votación es la recomendación mejor fundamentada que el Board puede producir, no una orden.

### 2.3 Por qué "el Board recomienda A, ADÁN recomienda B" no debería ocurrir

El escenario que motivó este documento asumía tres voces independientes: Board, ADÁN, cliente. Verificado contra la arquitectura ya congelada, esa premisa tiene un error estructural: **el CEO Agent no es una cuarta opinión — es cómo el Board Room produce la voz que el cliente escucha como "ADÁN".** Si el CEO Agent, personalmente, favorece una postura distinta a la que el Board vota, eso es un desacuerdo *entre Agentes* (cae bajo AD-CMP-02 y AD-CMP-03, no bajo un mecanismo nuevo) — se documenta en el acta como disenso interno, visible al cliente, nunca se presenta como una segunda recomendación de "ADÁN" compitiendo con "el Board". No existen tres voces. Existen dos: la del Board (con su disenso interno documentado si lo hay) y la del cliente.

### 2.4 El caso real: Board recomienda A, cliente quiere C

1. El Board presenta A al cliente, con su evidencia y, si existió, el disenso interno no resuelto por votación (sección 2.3) — nunca oculto (Regla 1.6 de AD-002).
2. El cliente puede aceptar A, pedir alternativas, o elegir C.
3. **Si el cliente elige C:** la Decisión avanza como Patrón A (AD-008) hacia `Aprobada` porque el cliente tiene autoridad de ejecución (sección 2.1) — nada lo bloquea. Pero ADÁN declara explícitamente el Confidence Level de C frente al de A (Regla 1.9, Principio de Humildad Intelectual, AD-001 §6.1): si C tiene menos evidencia que A, eso se registra en la propia Decisión, visible para consultas futuras — no se finge que ambas opciones estaban igual de fundamentadas.
4. La autoridad de ejecución del cliente nunca está condicionada a que su elección sea la mejor fundamentada — pero su elección siempre queda registrada con la verdad sobre qué tan fundamentada es.

**Esta es la respuesta completa a "¿quién tiene la última palabra?": el cliente tiene la última palabra sobre qué ocurre. La evidencia tiene la última palabra sobre qué tan bien fundamentado está lo que ocurre. Nunca se confunden.**

### 2.5 Qué se registra cuando el cliente decide distinto a lo recomendado

Cuando ocurre el caso de la sección 2.4, la Decisión (Patrón A, AD-008) registra seis campos, no solo el resultado final — ninguno es opcional:

1. **Opción elegida** (C).
2. **Opción recomendada por el Board** (A), con su fundamento.
3. **Nivel de evidencia** de cada una.
4. **Confidence Level** de cada una.
5. **Riesgos asumidos** — vinculados a la propiedad transversal Riesgo (AD-005 §3) cuando aplique.
6. **Responsabilidad asumida por el cliente** *(nuevo)* — una declaración explícita, dentro de la propia Decisión, de que el cliente entendió la recomendación distinta del Board y eligió proceder de todas formas.

**Por qué el sexto campo no es una cláusula legal.** No se registra para proteger a Paradixe de una reclamación — ese tipo de protección, si se necesita, es materia de WO-100/legal, fuera de esta especificación. Se registra porque es **materia prima de aprendizaje**. La Regla 1.8 de AD-002 (todo genera memoria) y la Ley de Aprendizaje de AD-005 §5 (Ley 2: Decisión de Negocio → Suceso Empresarial → Evidencia del resultado → ajuste de la siguiente Decisión) ya establecen que toda Decisión se conecta, con el tiempo, a la evidencia de lo que produjo. Una Decisión tomada en contra de una recomendación, con su Confidence Level declarado en el momento, es exactamente el tipo de dato que permite responder después: *"esta decisión fue tomada por el cliente, contra la recomendación del Board, con un Confidence Level del 41%, y produjo este resultado."* Ninguna entidad nueva hace falta para esto — es la Ley 2 ya existente, aplicada con prioridad a las decisiones que más enseñan: las que no siguieron la recomendación.

**Principio que se desprende de aquí, y que gobierna el futuro Learning Engine (AD-FUNC-09, no escrito todavía):** ADÁN no aprende solo del éxito. Aprende de las decisiones — incluidas las que resultan mal — porque lo que hace valiosa a una Decisión no es que haya acertado, es que haya quedado explícita, fundamentada y trazable antes de que su resultado se conociera. El sistema no depende de que el cliente elija siempre la opción mejor fundamentada; depende de que cada elección, sea cual sea, quede registrada con la verdad completa sobre su fundamento en el momento en que se tomó. Este documento planta esa regla; su desarrollo completo —cómo se agrega ese aprendizaje a través de muchas Empresas, cómo se detectan patrones— le corresponde a AD-FUNC-09.

---

## 3. Master Orchestration Flow (Flujo Maestro de Orquestación)

Sección interna de esta Funcionalidad — no es un documento independiente, por instrucción explícita del Board. Responde, en secuencia, las ocho preguntas que gobiernan una sesión de Board Room:

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | ¿Quién habla primero? | El CEO Agent, abriendo con el objetivo de la sesión y qué decisión está en juego — nunca un Agente especializado sin contexto previo |
| 2 | ¿Cuándo interviene ADÁN? | Siempre — el CEO Agent preside toda la sesión (sección 1) |
| 3 | ¿Cuándo deliberan los Agentes? | Cuando la pregunta convocada toca más de una especialidad (AD-CMP-02 §1) |
| 4 | ¿Cuándo participa el cliente? | Desde el inicio de forma visible (a diferencia de la conversación normal); activamente cuando se le solicita evidencia o cuando debe aprobar (Patrón A) |
| 5 | ¿Cuándo se solicita evidencia? | Antes de que cualquier posición del Board pase de `Propuesta` a presentarse formalmente (AD-CMP-05) |
| 6 | ¿Cuándo una decisión escala al Board? | Cuando AD-CMP-02 no resuelve una discrepancia material, o la decisión toca Nivel, capital, o Riesgo alto (sección 1) |
| 7 | ¿Cuándo cambia el Gemelo Digital? | Solo cuando la Decisión llega a `Ejecutada` (Patrón A completo) — nunca durante la deliberación |
| 8 | ¿Cuándo termina una sesión? | Cuando la Decisión alcanza un estado terminal (`Ejecutada` o `Rechazada`) y se genera el resumen que asciende a la Card/Nivel correspondiente (AD-CMP-04 §3) |

---

## Dependencias

- AD-CMP-02 Comportamiento de Consenso Multiagente (consenso interno, no se repite aquí)
- AD-CMP-03 Comportamiento de Decisiones (Patrón A aplicado a la Decisión que produce el Board)
- AD-008 Objetos del Sistema (Patrón A, modelo de permisos)
- AD-001 Product DNA §12 (autoridad de ejecución del cliente), §6.1 (Humildad Intelectual)
- AD-006 Domain Model v1.1 (entidades Agente, Decisión)
- AD-005 Enterprise Domain Model §5 (Ley 2, Aprendizaje — fundamento de la sección 2.5)

## Documentos relacionados

- AD-UX (vista de Board Room, mecánica visual de votación — Decisión de Diseño, no resuelta aquí)
- AD-FUNC-01 (las decisiones de transición de Nivel son un disparador típico de escalamiento a Board, sección 1)
- AD-FUNC-09 Learning Engine (no escrito todavía) — hereda directamente el principio de la sección 2.5: ADÁN aprende de las decisiones, no solo del éxito

## Impacto sobre otros módulos

1. Todo AD-UX que represente Board Room debe mostrar el disenso interno del Board cuando exista (sección 2.3) — nunca puede simplificarlo a una sola recomendación limpia si hubo desacuerdo real.
2. Toda Decisión que documente una elección del cliente contraria a la recomendación mejor fundamentada debe registrar el Confidence Level comparativo (sección 2.4) — esto es un requisito para AD-ARQ cuando implemente el objeto Decisión.

## Riesgos

- **Riesgo de que "el CEO Agent no es una cuarta voz" resulte contraintuitivo para el equipo de producto o los usuarios** — es una simplificación deliberada de la arquitectura, justificada en la sección 2.3, pero merece explicarse con cuidado en cualquier material de cara al cliente para no generar la expectativa de "hablar con el CEO aparte del Board".
- **Riesgo de que el umbral de "decisión de peso suficiente para escalar a Board" (sección 1) sea impreciso hasta que exista un caso real que lo calibre.**

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

- Calibrar con un caso real el umbral exacto de escalamiento a Board Room (sección 1).

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 (Revisión 1) | 2026-07-14 | Creación inicial: Board Room, Flujo Maestro de Orquestación (sección interna, 8 preguntas), jerarquía de autoridad de dos dimensiones (ejecución vs. fundamentación) resolviendo explícitamente el mecanismo de resolución de conflictos Board/Agente/cliente | Segundo documento de la categoría Funcionalidades |
| v1.0 (Revisión 2 — pre-aprobación) | 2026-07-14 | Se agrega la sección 2.5: seis campos de registro cuando el cliente decide distinto a lo recomendado, incluyendo el nuevo campo "Responsabilidad asumida" — no como protección legal, sino como materia prima de aprendizaje (Ley 2 de AD-005, ya existente). Se declara el principio "ADÁN aprende de las decisiones, no solo del éxito", heredado por el futuro AD-FUNC-09 | Retroalimentación explícita del Board tras revisión de la Revisión 1 |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board. Se congela | Cierre del ciclo de revisión de AD-FUNC-02 |
