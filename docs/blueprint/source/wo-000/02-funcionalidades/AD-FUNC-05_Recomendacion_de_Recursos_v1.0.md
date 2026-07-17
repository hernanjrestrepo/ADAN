---
Código: AD-FUNC-05
Nombre: Motor de Estrategias Empresariales
Nombre anterior (Revisión 1, misma versión v1.0): Recomendación de Recursos
Nombre original en el árbol (v3.1): Marketplace
Versión: v1.0 — Revisión 3, con Corrección Editorial Final
Estado: **APPROVED FOR GATE REVIEW.** Aprobado por el Board (2026-07-14): "considero cerrado el documento, no veo valor en seguir iterándolo." Construido, autoauditado, revisado en Architectural Consistency Review (0 hallazgos Críticos, 2 Altos y 2 Medios detectados — los 4 corregidos editorialmente sin reabrir el modelo) y congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa". Disponible como dependencia estable para el resto del árbol
Confidence Level: 35%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-FUNC-05 — Motor de Estrategias Empresariales

> Por instrucción explícita del Board: este documento ya no diseña un sistema que sugiere herramientas. Diseña un sistema que ayuda a cerrar brechas empresariales reales mediante estrategias fundamentadas — de las cuales una recomendación de recurso es, en el mejor de los casos, un paso final, nunca el objetivo. Es la tercera identidad de este documento en el mismo día de trabajo (Marketplace → Recomendación de Recursos → Motor de Estrategias Empresariales), cada cambio motivado por un análisis explícito, no por preferencia estética — ver sección 0.

**Nivel de contenido:** el *invariante* del flujo de razonamiento (nunca recomendar sin diagnóstico, nunca proponer una alternativa externa sin evaluar antes lo interno, nunca ejecutar sin autoridad del cliente, nunca saltarse el aprendizaje), el principio "recursos internos primero" (sección 4), la separación Confidence/Impacto Esperado (sección 6) y la autoridad de ejecución del cliente (sección 9) son Principio Permanente. **La enumeración específica de 11 pasos con estos 11 nombres (sección 2) es Decisión de Diseño** — implementa el invariante anterior en su forma actual, pero puede fusionarse, dividirse o renombrarse en una futura versión sin tocar el invariante que representa. Los 16 tipos de estrategia (sección 5), las Estrategias Compuestas (sección 5.1), el Horizonte temporal (sección 6.1), la fórmula de valor esperado (sección 8), el mecanismo de Estrategias Adaptativas (sección 8.2) y el registro del Playbook Empresarial (sección 10.1) son también Decisión de Diseño, sujetas a AD-004 §1.

---

## 0. Evolución de este documento

Tres identidades en una misma sesión de trabajo, cada una descartada por una razón concreta, no por gusto:

1. **"Marketplace"** (árbol original, v3.1) — nombraba una implementación (un lugar para navegar y comprar), no una función. Descartado.
2. **"Recomendación de Recursos"** — corrigió lo anterior, pero seguía asumiendo que el objeto central era el *recurso* (qué SaaS, qué mentor, qué plantilla). El Board observó que ningún empresario piensa en recursos — piensa en problemas ("necesito vender más", no "necesito un CRM"). El recurso era, siempre, la respuesta a una pregunta que el documento no se hacía todavía: ¿qué capacidad hace falta, y por qué? Descartado por incompleto, no por incorrecto.
3. **"Motor de Estrategias Empresariales"** (esta versión) — el recurso deja de ser el objeto de la funcionalidad y pasa a ser, en el mejor de los casos, el último eslabón de una cadena de razonamiento que empieza en el problema real de la Empresa y termina en una secuencia de acciones concretas con impacto estimado. La recomendación es una consecuencia del análisis estratégico, no el propósito del documento.

**Verificación de nombre contra AD-003:** "Motor" ya es un término fijo — "Motor (de Capacidad)" (AD-003 §1) — pero AD-003 mismo restringe su uso a "la relación de ADÁN con el resto del ecosistema; nunca su relación con el cliente." Este documento es exactamente lo segundo (la relación de ADÁN con el cliente, ayudándolo a crecer), por lo que no colisiona — es el mismo patrón seguro que ya usan Experience Engine y Gamification Engine (AD-FUNC-03, AD-FUNC-04), ambos "Motor/Engine" internos orientados al cliente sin conflicto con el "Motor" ecosistémico. La única precaución real: dentro de este mismo documento aparecerán los dos sentidos juntos (una Estrategia puede recomendar usar un Motor del Ecosistema, ej. Genexis) — por disciplina de redacción, todo Motor del Ecosistema se nombra siempre completo ("Motor del Ecosistema", nunca "Motor" a secas) para no confundirlo con el título de este documento.

La justificación arquitectónica completa de por qué este modelo es superior al de "Recomendación de Recursos" se entrega en la sección 13, después de especificar el modelo completo — para que la comparación se haga contra algo construido, no contra una promesa.

**Sobre "Motor de Evolución Empresarial" (propuesto en la revisión más reciente del Board, no adoptado):** el argumento de fondo es correcto — crear, transformar, operar, escalar, reinventar, recuperar, fusionar e internacionalizar son todas formas de evolución, y "Estrategia" nombra el mecanismo, no el fenómeno completo. Pero el nombre propuesto se evaluó y no se adopta, por dos razones concretas, no por preferencia:

1. **Colisión de nivel con AD-004 ("Product Evolution").** AD-004 ya gobierna cómo evoluciona *el producto ADÁN mismo* (qué puede cambiar, qué no, cómo nace una Funcionalidad). "Motor de Evolución Empresarial" pondría la palabra "Evolución" a nombrar, en el mismo árbol, dos cosas distintas — la evolución del producto (AD-004) y la evolución de la empresa cliente (este documento) — exactamente el mismo patrón de colisión que ya se resolvió con Proyecto, Decisión, Evento, Documento, Ecosistema, Marketplace y Capacidad. Es resoluble (como todas las anteriores), pero no gratis.
2. **Sobre-alcance frente a la Declaración de Misión y AD-FUNC-01.** La Declaración de Misión de AD-001 ya dice "diseñar, validar, construir, operar, transformar y escalar" — eso es, literalmente, "evolución empresarial" a nivel de **todo ADÁN**, no de una sola Funcionalidad. Los 7 Niveles (AD-FUNC-01) ya llevan a una empresa desde el Dolor hasta el Escalamiento — también evolución, en otro sentido. Nombrar este documento "Motor de Evolución Empresarial" lo haría sonar como si reclamara la misión completa de ADÁN, no una Funcionalidad entre nueve.

En vez del renombre literal, se incorpora la sustancia del argumento sin el riesgo de nombre: se agrega **"Recuperación ante crisis"** como tipo de Estrategia (sección 5, cluster nuevo), conectado explícitamente a las Leyes 6 y 7 del Workshop de Comportamientos (Crisis y Recuperación) — el único verbo de la lista del Board ("recuperar") que de verdad faltaba; "crear" es territorio de AD-FUNC-01, "reinventar" ya conectaba con la Ley 9, y "fusionar"/"internacionalizar" ya estaban cubiertos desde la Revisión 2. "Motor de Estrategias Empresariales" se mantiene como nombre, ahora con cobertura completa de los ocho verbos del Board sin tocar el alcance de ningún otro documento.

---

## 1. Qué es esta Funcionalidad

Dado un problema real que enfrenta una Empresa — detectado en cualquier punto de su relación con ADÁN, dentro de cualquiera de los 7 Niveles (AD-FUNC-01) — este Funcionalidad diagnostica la brecha real detrás del problema, identifica qué capacidad falta, evalúa todas las formas razonables de cerrarla (empezando siempre por lo que la Empresa ya tiene), simula el impacto esperado de cada una, y entrega una secuencia de acciones recomendadas — nunca una lista de herramientas para explorar.

Lo que NO es, por instrucción explícita del Board:

- No es un recomendador de recursos ni un catálogo de SaaS/partners/mentores. Eso queda como el paso final de un razonamiento mayor (sección 2, pasos 5-9), nunca como el objeto del documento.
- No sustituye el juicio del dueño de la Empresa. Diseña y simula caminos posibles; el cliente decide y ejecuta (sección 9, Principio Permanente heredado de AD-001 §5 y AD-FUNC-02).
- No asume que la solución está afuera. Por defecto, evalúa primero si la Empresa ya tiene lo necesario (sección 4).
- No presenta una estrategia sin fundamento cuantificado cuando ese fundamento existe, ni lo inventa cuando no existe (sección 6 — declarar el vacío es obligatorio).

---

## 2. El flujo obligatorio

Toda estrategia diseñada por este documento sigue esta secuencia, sin excepción. El orden no se altera sin abrir una nueva versión de este documento con justificación arquitectónica explícita — cada paso depende de que el anterior haya ocurrido de verdad, no es una checklist decorativa.

| # | Paso | Qué produce | Con qué ya existente conecta |
|---|---|---|---|
| 1 | **Problema detectado** | Una señal de que algo no funciona o podría funcionar mejor — puede surgir en un Board Room (AD-FUNC-02), en una Card de cualquier Nivel (AD-FUNC-01), o de un Riesgo materializándose (AD-005 §3, Ley 6) | Board Room, Nivel, Riesgo |
| 2 | **Diagnóstico** | Síntesis formal del problema — reutiliza el objeto **Entregable/Diagnóstico** ya definido en AD-003 y ya producido en Niveles 1 y 7 (`Diagnóstico del Dolor`, `Diagnóstico de escalamiento`, AD-FUNC-01) | Entregable (AD-003), AD-FUNC-01 |
| 3 | **Brechas identificadas** | La distancia entre el estado actual y lo que la Empresa necesita — calculada, no almacenada, sobre Objetivo/Meta no alcanzada (AD-005 §2.5) o Riesgo no mitigado (AD-005 §3) | Objetivo, Meta, Indicador, Riesgo |
| 4 | **Capacidades requeridas** | Qué habilidad de producir un resultado falta — "Capacidad" (AD-003 v1.1), derivada de la Brecha, nunca almacenada como entidad propia (sección 11) | Capacidad (AD-003 v1.1) |
| 5 | **Estrategias posibles** | El conjunto de caminos razonables para cerrar esa Capacidad — sección 5 | 16 tipos de estrategia |
| 6 | **Simulación de Impacto** | Proyección de qué pasaría si cada Estrategia se ejecuta — sección 7, distinta de la Validación Simulada de Nivel 5 | — |
| 7 | **ROI esperado** | Cuantificación de beneficio contra costo y tiempo, por Estrategia — sección 6 | — |
| 8 | **Secuencia óptima** | Orden de ejecución cuando hay Estrategias con dependencias entre sí — sección 8 | — |
| 9 | **Recomendación** | La consecuencia de los ocho pasos anteriores — nunca el punto de partida | AD-FUNC-02 (Board Room la presenta) |
| 10 | **Ejecución** | Decisión y acción del cliente — nunca de ADÁN — sección 9 | Autoridad de ejecución (AD-001 §5, AD-FUNC-02) |
| 11 | **Aprendizaje** | Comparación entre lo esperado y lo real, alimentando el Learning Engine — sección 10 | AD-FUNC-09 (semilla) |

---

## 3. Capacidad — el concepto unificado

Por instrucción explícita del Board: no se crea "Capacidad Empresarial". Se usa **Capacidad**, el mismo término que AD-003 ya usaba en "Motor (de Capacidad)" — actualizado en AD-003 v1.1 para declarar explícitamente que "Capacidad" es el concepto general (una habilidad de producir un resultado), aplicable en dos niveles distinguibles por contexto:

- **Capacidad que el Ecosistema Paradixe provee a ADÁN** — sentido original de AD-003, ejecutada por un Motor del Ecosistema (Genexis, EVA, ARQAI...).
- **Capacidad que una Empresa cliente necesita desarrollar o ya posee** — el sentido que este documento trabaja.

Ambos son la misma idea en dos escalas — no dos conceptos. Y hay una relación real entre ellos, no solo lingüística: cuando la Capacidad que falta en la Empresa cliente es algo que el Ecosistema Paradixe ya sabe proveer (ej. "necesito construir software"), un Motor del Ecosistema (Genexis) es directamente una de las Estrategias posibles (sección 5) — la unificación de término no es solo económica conceptualmente, también evita modelar dos veces la misma relación.

---

## 4. Recursos internos primero (Principio Permanente)

Antes de evaluar cualquier alternativa externa, ADÁN evalúa si la Capacidad requerida ya puede cerrarse con lo que la Empresa ya tiene. Esto no es un paso opcional de cortesía — es la aplicación más literal del principio "ADÁN primero es asesor" heredado de la Revisión 1: la mejor recomendación posible es a veces "no necesitas nada nuevo."

Ninguna categoría de recurso interno necesita entidad nueva — las seis que pidió el Board ya son entidades de AD-005 de primera clase:

| Recurso interno | Entidad AD-005 | Cómo se evalúa |
|---|---|---|
| Personas | **Empleado** (§2.2) | ¿Algún Empleado, en su Cargo o Rol Funcional actual, puede asumir esto? |
| Activos | **Activo** (§2.6) | ¿La Empresa ya posee algo (financiero o de otro tipo) que cierra la brecha sin adquirir nada nuevo? |
| Procesos | **Proceso** (§2.4) | ¿Existe ya un Proceso que solo necesita ajustarse o madurar, en vez de crear uno desde cero? |
| Tecnología instalada | **Proveedor** + **Contrato** ya vigentes (§2.3, §2.4) | ¿Una herramienta ya contratada puede usarse de forma distinta o más completa antes de contratar otra? |
| Proveedores actuales | **Proveedor** ya vinculado (§2.3) | ¿Un Proveedor existente puede ampliar su alcance antes de buscar uno nuevo? |
| Conocimiento interno | **Documento** con `Origen: generado internamente` (§2.4) + experiencia tácita de **Empleado** | ¿Ya existe conocimiento documentado o vivido dentro de la Empresa que resuelve esto? |

Solo cuando ninguna fila de esta tabla cierra la Capacidad requerida, este documento evalúa alternativas externas (Estrategias de la sección 5 que involucran contratar, tercerizar, comprar, o traer un socio).

---

## 5. Estrategias posibles

Una Estrategia es un camino candidato para cerrar una Capacidad — no una entidad almacenada (verificación completa en sección 11), sino una opción evaluada que, si el cliente la elige, se convierte en una Decisión de Negocio y en la entidad AD-005 que le corresponda según su tipo. Ninguna Estrategia se limita a software — el listado que seguía "SaaS/agentes/servicios" en la Revisión 1 queda subordinado a esta lista más amplia, agrupada en seis clusters (16 tipos, el sexto cluster agregado en Revisión 3):

| Cluster | Estrategia | Al ejecutarse, se convierte en |
|---|---|---|
| **Personas** | Capacitar | Iniciativa; puede actualizar el Rol Funcional o Cargo de un Empleado |
| | Contratar | Nuevo Empleado + Contrato (laboral) |
| | Despedir | Cambio de estado de un Empleado existente (versionado, AD-002 §1.7) — **sensible, ver Riesgos** |
| **Operación** | Automatizar | Nueva versión de un Proceso existente |
| | Cambiar procesos | Nueva versión de un Proceso existente |
| **Tecnología** | Comprar software | Nuevo Proveedor + Contrato (mismo mecanismo que "adoptar un Recurso" de la Revisión 1) |
| | Desarrollar software | Iniciativa interna, o Proveedor si se terceriza a un Motor del Ecosistema (ej. Genexis) |
| **Estructura** | Cambiar estructura organizacional | Nueva versión de Departamento/Cargo/Rol Funcional |
| **Alianzas y Capital** | Tercerizar | Nuevo Proveedor + Contrato |
| | Buscar socios | Nuevo Contrato con parte "Socio" (AD-005 §2.4) |
| | Levantar inversión | Nueva relación Accionista/Inversionista (§2.1) + Contrato |
| | Adquirir empresas | Fusión de Gemelos Digitales — mecanismo ya definido en **AD-CMP-06** (Digital Twin Lifecycle) |
| | Fusionarse | Mismo mecanismo, AD-CMP-06 |
| **Expansión y Modelo** | Internacionalizarse | Nueva relación Empresa-Mercado (§2.3) |
| | Cambiar el modelo de negocio | Cambio en Producto/Servicio (§2.3); si es lo bastante profundo, puede constituir una **Reinvención** (Ley 9, Workshop de Comportamientos — cambio de Narrativa Fundacional por aprendizaje de bucle doble) |
| **Recuperación** *(nuevo en Revisión 3)* | Recuperación ante crisis | No es una entidad nueva ni un cluster con mecanismo propio — es la aplicación directa de la **Ley 7** (Recuperación, Workshop de Comportamientos: explicada por Intangibles acumulados antes de la crisis, no por Activos financieros) a un Riesgo ya materializado bajo la **Ley 6** (Crisis: Riesgo que supera la capacidad de absorción, AD-005 §3). Se resuelve con una o varias Estrategias de los clusters ya existentes (ej. "cambiar estructura" + "tercerizar" + "levantar inversión"), casi siempre como Estrategia Compuesta (sección 5.1) |

Ninguna fila requiere una entidad nueva de AD-005 — verificación completa en sección 11.

### 5.1 Estrategias compuestas (híbridas)

Por instrucción explícita del Board: la mayoría de los casos reales no se resuelven con una sola Estrategia atómica de la tabla anterior — "capacitar + automatizar + cambiar proceso + contratar" es una Estrategia distinta de cualquiera de sus cuatro partes por separado. Una **Estrategia Compuesta** es un conjunto de Estrategias atómicas agrupadas y evaluadas como una sola unidad — no es una entidad nueva (sección 11): es una agregación funcional sobre Estrategias que ya existen.

Dos reglas gobiernan su Valor Esperado (sección 6):

1. **No es la suma de las partes.** El Impacto, Costo, Tiempo y Riesgo del conjunto se estiman como unidad, porque combinar Estrategias puede generar sinergia (ej. "cambiar proceso" antes de "automatizar" cuesta menos junto que por separado) o fricción (ej. "contratar" y "despedir" en simultáneo elevan el Riesgo organizacional por encima de la suma de ambos por separado).
2. **Al ejecutarse, sigue resolviendo en las mismas entidades de la tabla anterior — una por cada Estrategia atómica que la compone.** Una Estrategia Compuesta no crea una Decisión de Negocio única para todo el paquete; crea una por componente, vinculadas entre sí por la Secuencia óptima (sección 8) que ya determina su orden interno de ejecución.

---

## 6. Valor esperado por Estrategia

Cada Estrategia declara, cuando exista evidencia suficiente para hacerlo — y declarando explícitamente el vacío cuando no exista, nunca rellenándolo con un número inventado:

| Campo | Qué mide | Distinto de |
|---|---|---|
| **Impacto esperado** | Cuánto mejora un Indicador o Meta real de la Empresa (AD-005 §2.5) si la Estrategia funciona | Confidence Level — ver nota |
| **Confidence Level** | Qué tan seguro está ADÁN de que el Impacto esperado es correcto (AD-002 §1.9) | Impacto esperado |
| **Probabilidad de éxito** | Qué tan probable es que *esta* Estrategia específica funcione, dado el contexto de *esta* Empresa — no una medida general de certeza de ADÁN, sino un juicio sobre la Estrategia misma | Confidence Level — el Confidence Level puede ser alto sobre una Probabilidad de éxito baja ("estoy seguro de que esto tiene 30% de probabilidad de funcionar aquí") |
| **ROI esperado** | Retorno cuantificado — tiempo de recuperación o beneficio neto | — |
| **Tiempo estimado** | Duración calendario de la implementación | Esfuerzo esperado |
| **Esfuerzo esperado** | Carga operativa real — horas-persona, disrupción organizacional — necesaria para ejecutar la Estrategia | Tiempo estimado (una Estrategia puede tomar poco tiempo calendario y mucho esfuerzo concentrado, o al revés) |
| **Costo estimado** | Costo monetario real, sin letra pequeña (mismo estándar que AD-001 §7) | Esfuerzo esperado |
| **Complejidad** | Cuántas partes móviles e interdependencias tiene la Estrategia — no es lo mismo que su Riesgo | Riesgo (una Estrategia puede ser compleja y de bajo riesgo, o simple y de alto riesgo) |
| **Riesgo** | Propiedad transversal de AD-005 §3 aplicada a la Estrategia: tipo, severidad, probabilidad de materializarse | Complejidad |
| **Horizonte temporal** | En qué ventana de tiempo se espera el impacto — ver tabla siguiente | Tiempo estimado (el Tiempo estimado es cuánto dura *implementarla*; el Horizonte es cuándo se espera *el resultado*) |
| **Dependencias** | Qué otras Estrategias deben ejecutarse antes o después | Secuencia óptima (sección 8, es el resultado de esto) |
| **Orden recomendado de ejecución** | Posición de esta Estrategia dentro de la Secuencia óptima | — |

**Confidence Level e Impacto Esperado nunca se fusionan en una sola cifra.** Son preguntas distintas — "¿cuánto mejora la Empresa?" no es la misma pregunta que "¿qué tan seguro estoy de esa proyección?" — y fusionarlas oculta exactamente la información que AD-002 §1.9 exige mostrar por separado. La misma disciplina aplica ahora a Riesgo/Complejidad y a Tiempo/Esfuerzo/Horizonte — cada par mide algo distinto y ninguno sustituye al otro.

### 6.1 Horizonte temporal (obligatorio por Estrategia)

| Horizonte | Ventana | Ejemplo típico |
|---|---|---|
| **Inmediato** | 0-30 días | Automatizar un Proceso ya definido |
| **Corto plazo** | 3 meses | Contratar, capacitar |
| **Mediano plazo** | 12 meses | Cambiar estructura organizacional |
| **Largo plazo** | 3 años | Internacionalizarse |
| **Transformacional** | 5-10 años | Cambiar el modelo de negocio, Reinvención (Ley 9) |

El Horizonte de cada Estrategia, junto con sus Dependencias (tabla anterior) y su posición en la Secuencia óptima (sección 8), es el insumo directo para construir un Roadmap — la construcción visual de ese Roadmap es Decisión de Diseño de un futuro AD-UX, no se resuelve aquí.

---

## 7. Simulación de Impacto

Distinta, por diseño, de la **Validación Simulada** de Nivel 5 (AD-FUNC-01): esa simulación prueba si una idea de negocio o un MVP nuevo funcionaría en el mercado. Esta simulación proyecta qué pasaría si una Empresa **ya operando** ejecuta una Estrategia concreta (contratar, automatizar, fusionarse...) — no valida una hipótesis de producto, proyecta el efecto de una acción sobre Indicadores ya existentes. Ambas son legítimas y conviven sin conflicto, pero nunca se nombran de forma intercambiable — donde haya ambigüedad, se escribe "Simulación de Impacto" completo, nunca "Simulación" a secas.

---

## 8. Secuencia óptima

Cuando varias Estrategias son candidatas a la vez, se ordenan por **valor esperado**, no por popularidad ni por cuál genera más ingreso a Paradixe:

```
Valor Esperado = (Impacto esperado × Probabilidad de éxito) ÷ Costo ÷ Tiempo ÷ Riesgo
```

Donde "Probabilidad de éxito" es, en la práctica, una lectura del Confidence Level de esa Estrategia — no una variable adicional a estimar por separado. El orden resultante es la Secuencia óptima (paso 8 del flujo), ajustada después por las Dependencias declaradas en la sección 6 (una Estrategia con menor valor esperado individual puede ir primero si otra de mayor valor depende de ella — ej. "cambiar un proceso" antes de "comprar software" que lo automatiza).

**Distinción explícita de AD-FUNC-04 §2.1:** esto no es el ranking social entre fundadores que esa sección prohíbe por defecto — es un ranking de opciones dentro del mismo fundador, para su propia Empresa. No hay conflicto entre ambas reglas, pero se nombran juntas aquí para que nunca se confundan.

### 8.1 Estrategias competidoras y el Board Room

Este documento no entrega una única recomendación aislada — entrega un conjunto de Estrategias candidatas (atómicas o compuestas), cada una con su perfil completo de la sección 6 (Impacto, Confidence, ROI, Costo, Tiempo, Esfuerzo, Complejidad, Riesgo, Horizonte), ordenadas por la Secuencia óptima. Ese conjunto se presenta como tal — no reducido a una sola opción antes de tiempo — dentro del **Board Room** (AD-FUNC-02), donde el mecanismo de debate y consenso ya está completamente especificado por **AD-CMP-02** (Consenso Multiagente) y el Master Orchestration Flow de AD-FUNC-02 §3. No se diseña un mecanismo de debate nuevo aquí — sería duplicar lo ya congelado; este documento solo garantiza que lo que llega al Board Room es un conjunto comparable, no una lista plana.

### 8.2 Estrategias Adaptativas

Por instrucción explícita del Board: no todas las Estrategias son un plan fijo — muchas son condicionales ("si ocurre A, haz B; si ocurre C, haz D; si ocurre E, abandona el plan"). Una **Estrategia Adaptativa** es una Estrategia (atómica o compuesta) cuya ejecución se ramifica según condiciones futuras observables, en vez de seguir un único camino.

**Verificación contra la Regla de Entidades:** no requiere una entidad nueva. Cada pieza ya existe:

- **La condición** ("si ocurre A") es un Suceso Empresarial ya definido (AD-005 §2.4) o un Indicador cruzando un umbral (AD-005 §2.5) — ambos ya observables por el sistema.
- **La acción** ("haz B") es otra Estrategia candidata, atómica o compuesta — ya definida en este mismo documento.
- **El abandono** ("abandona el plan") es una transición de estado de la Iniciativa o Decisión de Negocio subyacente a su estado terminal de rechazo — ya cubierta por el **Patrón A (Ciclo de Aprobación)** de AD-008, que gobierna exactamente esas entidades sin necesidad de un estado nuevo.

Lo que sí es nuevo es la **forma del contenido**: en vez de que una Iniciativa o Decisión de Negocio registre un solo camino, registra un pequeño árbol de condición→acción como parte de su contenido — un atributo más rico sobre una entidad que ya existe, no una entidad adicional.

**Lo que este documento no resuelve:** el mecanismo que *vigila* las condiciones en el tiempo real de la Empresa (detectar cuándo ocurre A, C o E) es una responsabilidad de arquitectura — de un futuro AD-ARQ, no de esta especificación de producto. Se registra como Decisión pendiente, mismo tratamiento que el contrato de integración con los Motores del Ecosistema.

---

## 9. Autoridad de ejecución — recordatorio explícito (Principio Permanente)

Este documento diseña, simula y recomienda. **Nunca ejecuta.** La autoridad de ejecución es siempre del cliente — sin excepción, sin importar cuántos datos respalden una Estrategia (AD-001 §5: "ADÁN nunca sustituye el juicio final del dueño de la empresa"; AD-FUNC-02 §2, autoridad de ejecución vs. autoridad de fundamentación). Esto se reafirma aquí con más fuerza que en la Revisión 1 porque el nombre "Motor de Estrategias Empresariales" suena más autónomo que "Recomendación de Recursos" — y no lo es. Contratar, despedir, fusionarse, levantar inversión: cada una de estas acciones ocurre en el mundo real, ejecutada por el cliente, nunca por ADÁN. Lo que ADÁN aporta es el razonamiento, la evidencia y la secuencia — nunca el acto.

---

## 10. Ciclo de aprendizaje (alimenta AD-FUNC-09)

Toda Estrategia ejecutada retroalimenta al futuro Learning Engine mediante este ciclo, más completo que la semilla original de AD-FUNC-02 §2.5:

```
Brecha → Capacidad → Estrategia elegida → Implementación → Resultado
   → ROI real → Desviación frente al ROI esperado → Aprendizaje
   → Recalibración del Confidence Level
```

La comparación entre ROI esperado (sección 6) y ROI real es, en sí misma, un mecanismo concreto de recalibración empírica — no declarativa — del Confidence Level de futuras Estrategias del mismo tipo. Se registra como dependencia explícita y obligatoria de AD-FUNC-09 (sección de Documentos relacionados).

### 10.1 El Playbook Empresarial (activo futuro, no construido aquí)

El Board señaló algo real: una vez que ADÁN acumule suficientes ciclos completos del aprendizaje anterior a través de muchas Empresas distintas, podrá reconocer patrones del tipo *"las empresas SaaS B2B de salud con menos de 10 empleados que ejecutaron esta combinación de Estrategias crecieron 2.8 veces más."* Eso es conocimiento propietario agregado — un **Playbook Empresarial** — y sería, potencialmente, uno de los activos más valiosos del ecosistema.

Este documento **no lo construye** — por la misma disciplina de evidencia que gobierna todo el proyecto (Riesgo de sobre-alcance ya declarado en la Revisión 2): no existe todavía un solo caso real ejecutado, y diseñar el mecanismo de un Playbook sin datos reales sería exactamente el tipo de complejidad prematura que la Economía Conceptual (AD-002 v2.0 §1.10) prohíbe. Lo que sí se registra, formalmente:

- El Playbook Empresarial es, conceptualmente, un **output agregado y anonimizado del ciclo de aprendizaje de AD-FUNC-09** — no una funcionalidad separada. Vive donde vive el aprendizaje, no en un documento nuevo.
- Se registra como **future_seed** en el Knowledge Graph, con destino AD-FUNC-09, para no perderse antes de que existan casos reales suficientes.
- Si en el futuro el Playbook demuestra necesitar su propia entidad de datos (ej. un "Patrón de Éxito" formal, distinto de una simple agregación de Estrategias ya ejecutadas), esa necesidad se decide entonces, contra evidencia real — abriendo una nueva versión de AD-005/AD-006, nunca aquí ni por adelantado.

---

## 11. Verificación contra la Regla de Entidades y el Principio de Emergencia

**Ninguna entidad nueva se crea. AD-005 no se modifica.** Verificación explícita de cada concepto nuevo de este documento:

| Concepto | ¿Es entidad nueva? | Por qué no |
|---|---|---|
| **Brecha** | No | Se calcula, no se almacena: distancia entre Meta/Objetivo no alcanzada o Riesgo no mitigado (ya existentes, AD-005 §2.5, §3) y el estado actual de la Empresa |
| **Capacidad** | No | Concepto ya fijado en AD-003 (ampliado en v1.1, no creado aquí); se deriva de una Brecha, no se almacena independientemente |
| **Estrategia** | No | Candidata pre-decisión — una vez elegida, se convierte en Decisión de Negocio (AD-005 §2.5) más la entidad que le corresponda por tipo (sección 5): Iniciativa, Contrato, Proveedor, Accionista/Inversionista, o el mecanismo de fusión ya definido en AD-CMP-06 |
| **Estrategia Compuesta** | No | Agregación funcional sobre Estrategias atómicas ya existentes (sección 5.1) — al ejecutarse resuelve en las mismas entidades que sus componentes, una por componente |
| **Estrategia Adaptativa** | No | Contenido más rico (un árbol condición→acción) sobre una Iniciativa o Decisión de Negocio que ya existe (Patrón A, AD-008) — las condiciones son Suceso Empresarial/Indicador ya definidos, no una entidad nueva (sección 8.2) |
| **Playbook Empresarial** | No — y no se construye todavía | Output agregado futuro del ciclo de aprendizaje de AD-FUNC-09 (sección 10.1); si algún día necesita entidad propia, esa decisión se toma contra evidencia real, no aquí |

Esto confirma, en sentido inverso, que la decisión de no crear entidades era correcta: los casos más extremos que el Board pidió cubrir — adquirir otra empresa, fusionarse, cambiar el modelo de negocio, recuperación ante crisis, estrategias compuestas, estrategias adaptativas — ya tenían dónde vivir en documentos ya congelados (AD-CMP-06 para fusión/adquisición; Ley 9 para Reinvención; Leyes 6-7 para Crisis/Recuperación; AD-008 Patrón A para el ciclo de vida de una Iniciativa/Decisión de Negocio), sin que este documento tuviera que inventar nada.

---

## 12. Verificación contra el Criterio de Existencia (AD-004 v1.1 §3.1)

| Condición | ¿Se cumple? | Cómo |
|---|---|---|
| ¿Modifica el Gemelo Digital? | Sí, con más fuerza que la Revisión 1 | Cada Estrategia ejecutada se registra como Decisión de Negocio y actualiza la entidad correspondiente (Empleado, Proceso, Proveedor, Contrato...); cada Simulación de Impacto y su resultado real quedan como evidencia |
| ¿Mejora el conocimiento del cliente? | Sí | El cliente pasa de "no sé qué hacer" a "esta es la Brecha, esta es la Capacidad que falta, estas son mis opciones reales con impacto estimado" |
| ¿Produce evidencia útil para la siguiente decisión? | Sí | El ciclo de aprendizaje (sección 10) compara ROI esperado contra ROI real y recalibra el Confidence Level de futuras Estrategias — evidencia acumulativa, no solo puntual |

---

## 13. Por qué este modelo representa mejor la misión de ADÁN que "Recomendación de Recursos"

La Declaración de Misión de AD-001 dice: *"diseñar, validar, construir, operar, **transformar** y escalar empresas extraordinarias."* El verbo "transformar" llevaba congelado desde AD-001 v1.0 sin que ninguna Funcionalidad le diera contenido real — ni Los 7 Niveles (que diseña, valida, construye, opera y escala, pero no transforma una empresa ya existente), ni Board Room, ni Experience/Gamification Engine. "Recomendación de Recursos" tampoco lo hacía: sugerir un SaaS o un mentor no transforma una empresa, la equipa marginalmente.

"Motor de Estrategias Empresariales" es la primera Funcionalidad que responde genuinamente a "transformar" — porque su objeto no es "¿qué herramienta falta?" sino "¿qué necesita cambiar en esta Empresa para que le vaya mejor, y en qué orden?" — la misma pregunta que se hace un CEO real, no un catálogo. Tres diferencias concretas sostienen esto:

1. **El objeto de razonamiento cambió de nivel.** "Recurso" es una respuesta; "Capacidad" es la pregunta correcta; "Estrategia" es el camino completo. Un sistema que razona sobre Estrategias puede, cuando corresponde, concluir "no compres nada, reorganiza tu equipo" — algo que un recomendador de recursos no puede decir por diseño, porque su vocabulario no incluye esa opción.
2. **Recursos internos primero deja de ser una cortesía y se vuelve estructural.** En el modelo de Recursos, "revisa lo que ya tienes" era una sección adicional. En el modelo de Estrategias, es el paso 4 del flujo obligatorio — no se puede proponer una Estrategia externa sin haber evaluado primero si la Capacidad ya existe dentro de la Empresa.
3. **El aprendizaje se vuelve verificable, no solo narrado.** El ciclo de la sección 10 compara un ROI esperado contra un ROI real — la Revisión 1 solo aprendía de "se aceptó o se rechazó una recomendación." Este modelo aprende de si la predicción fue correcta, que es evidencia de una calidad completamente distinta para AD-FUNC-09.

Ninguna de las tres diferencias requirió romper la Regla de Entidades, tocar AD-005, o contradecir un solo documento ya congelado — la evolución fue posible porque la arquitectura de fondo (AD-005, AD-CMP-06, la Ley 9, el Criterio de Existencia) ya estaba diseñada con suficiente generalidad para sostenerla sin cambios.

---

## 14. Autoauditoría obligatoria (10 preguntas)

1. **¿Contradice AD-000, AD-001 o AD-002?** No. Se verificó explícitamente contra AD-001 §1.1 (Qué NO es ADÁN) y §5 (Qué nunca hará) — ninguna de las ocho exclusiones ni las seis prohibiciones de §5 choca con diseñar/simular estrategias; al contrario, el documento cita y refuerza "ADÁN nunca sustituye el juicio final del dueño" con más fuerza que antes (sección 9).
2. **¿Todo concepto nuevo está justificado?** Brecha, Capacidad y Estrategia se verificaron uno por uno contra el Principio de Emergencia y la Regla de Entidades en la sección 11 — ninguno requiere entidad nueva ni versión nueva de AD-005.
3. **¿Hay duplicación con un documento existente?** No — se verificó explícitamente contra AD-FUNC-04 §2.1 (ranking social, sección 8 de este documento) y contra Nivel 5/Validación Simulada (AD-FUNC-01, sección 7 de este documento), en ambos casos con la distinción escrita explícitamente para prevenir confusión futura, no solo evitada por casualidad.
4. **¿Qué impacto tiene sobre documentos futuros?** AD-FUNC-09 (Learning Engine) hereda una dependencia explícita más rica que la semilla original (sección 10). AD-UX deberá diseñar la interfaz del flujo de 11 pasos sin saltarse ninguno. Un futuro AD-INT deberá conectar los Motores del Ecosistema como una fuente real de Estrategias de tipo "comprar/desarrollar software".
5. **¿Introduce un riesgo arquitectónico nuevo?** Sí, uno: la ambición del alcance (contratar, despedir, M&A, cambio de modelo de negocio) es mucho mayor que "sugerir un SaaS" — el Riesgo de responsabilidad legal/humana por estrategias de personal o M&A se declara explícitamente abajo, no se minimiza.
6. **¿El Confidence Level es honesto?** 35% — bajó de 38% (Revisión 2), a propósito: se agregaron Estrategias Compuestas, Estrategias Adaptativas y un cluster de Recuperación sin un solo caso real que los valide — más alcance con la misma evidencia real (ninguna) baja la confianza honesta, no la sube.
7. **Prueba "si este documento desapareciera":** ADÁN volvería a ser un recomendador de herramientas de un solo camino fijo — perdería la capacidad de decir "no necesitas comprar nada", de combinar Estrategias en un paquete coherente, y de ramificar un plan según lo que realmente ocurra, en vez de asumir que el futuro sale como se proyectó.
8. **Prueba "válido en 10 años":** el flujo, los clusters de Estrategia y el mecanismo de Estrategias Adaptativas no dependen de qué tecnología exista en el mercado — son la misma disciplina de un asesor de negocios serio en cualquier década; el propio mecanismo condición→acción es más parecido a cómo piensa un CEO real (con planes de contingencia) que a un plan fijo de consultoría.
9. **¿Se verificó contra colisiones de nombre?** Sí — "Motor" contra AD-003 (sección 0), "Capacidad" contra AD-003 (sección 3, resuelto en AD-003 v1.1), "Simulación" contra Nivel 5 (sección 7), "ranking"/secuencia contra AD-FUNC-04 §2.1 (sección 8), y "Motor de Evolución Empresarial" contra AD-004 y contra la Declaración de Misión de AD-001 (sección 0 — evaluado y explícitamente no adoptado, con razones).
10. **¿La autoauditoría se entrega junto con el documento, no después?** Sí — esta sección, entregada en el mismo ciclo de construcción, antes de que el Board la revise.

---

## Dependencias

- AD-FUNC-01 Los 7 Niveles (dónde surge el Problema detectado; Diagnóstico como Entregable ya definido)
- AD-FUNC-02 Board Room (dónde se presenta la Recomendación y compiten las Estrategias candidatas; autoridad de ejecución vs. fundamentación)
- AD-CMP-02 Consenso Multiagente (mecanismo de debate ya especificado, reutilizado sin cambios en sección 8.1)
- AD-005 Enterprise Domain Model (Objetivo, Meta, Indicador, Riesgo, Proceso, Empleado, Activo, Proveedor, Contrato, Accionista/Inversionista — ninguno nuevo, todos ya existentes)
- AD-CMP-06 Digital Twin Lifecycle (fusión/adquisición de Gemelos Digitales — landing spot de las Estrategias "Adquirir empresas" y "Fusionarse")
- AD-008 Objetos del Sistema, Patrón A (Ciclo de Aprobación — landing spot del estado "abandonado" de una Estrategia Adaptativa, sección 8.2)
- Workshop de Comportamientos, Ley 9 (Reinvención — landing spot de "Cambiar el modelo de negocio"); Leyes 6-7 (Crisis/Recuperación — landing spot de "Recuperación ante crisis")
- AD-003 v1.1 (Capacidad, actualizado en paralelo a este documento)
- AD-002 §1.9 (Confidence Level obligatorio, separado de Impacto Esperado y de Probabilidad de éxito)
- AD-004 v1.1 §3.1 (Criterio de Existencia)

## Documentos relacionados

- AD-FUNC-09 Learning Engine (aún no construido) — hereda como dependencia explícita el ciclo completo de la sección 10, más el Playbook Empresarial (sección 10.1) como su output agregado futuro
- AD-UX (Fase 2) — diseño visual del flujo de 11 pasos y de la comparación de Estrategias competidoras (sección 8.1), sin saltarse ninguno
- AD-INT (Fase 2) — contrato de integración con Motores del Ecosistema como fuente de Estrategias de software; mismo gap ya señalado en la Revisión 1 para el Marketplace del Ecosistema
- AD-ARQ (Fase 2, futuro) — mecanismo técnico de vigilancia de condiciones para Estrategias Adaptativas (sección 8.2)

## Impacto sobre otros módulos

1. El árbol documental (WO-000_INDICE_MAESTRO) debe actualizarse a v3.19: AD-FUNC-05 conserva el nombre "Motor de Estrategias Empresariales" (evaluado un tercer nombre, "Motor de Evolución Empresarial", y explícitamente no adoptado — sección 0), pero amplía su alcance con Estrategias Compuestas, Adaptativas, un cluster de Recuperación, y el registro formal del futuro Playbook Empresarial.
2. AD-003 permanece en v1.1 — sin cambios adicionales en esta revisión.
3. Todo AD-UX que diseñe esta Funcionalidad debe representar los 11 pasos del flujo, la comparación de Estrategias competidoras como un conjunto (no una sola recomendación reducida prematuramente), y la posibilidad explícita de que el resultado sea "no necesitas nada externo".
4. AD-FUNC-09, cuando se escriba, hereda el ciclo de aprendizaje de la sección 10 y el mandato explícito de eventualmente producir un Playbook Empresarial (sección 10.1) como uno de sus outputs de mayor valor, cuando exista evidencia real suficiente.

## Riesgos

- **Riesgo humano y legal en estrategias de personal.** "Despedir" y, en menor medida, "Contratar" tienen implicaciones laborales y legales reales — este documento diseña y simula, nunca ejecuta (sección 9), pero el Riesgo de que una simulación de impacto se lea como respaldo legal para una decisión de personal debe gestionarse explícitamente en AD-UX y en cualquier comunicación al cliente.
- **Riesgo de sobre-alcance sin evidencia real, ampliado en esta revisión.** Ni un solo tipo de Estrategia, Estrategia Compuesta o Estrategia Adaptativa tiene todavía un caso ejecutado real que valide el modelo de ROI/Confidence — el Confidence Level de 35% (bajó desde 38%) refleja esto honestamente; no se debe comunicar este documento como validado hasta que existan casos reales.
- **Riesgo heredado:** el Marketplace del Ecosistema (o cualquier Motor del Ecosistema) como fuente de datos real para las Estrategias de tipo software sigue sin contrato de integración (AD-INT, Fase 2); el mecanismo de vigilancia de condiciones para Estrategias Adaptativas tampoco existe todavía (AD-ARQ, Fase 2).
- **Riesgo de presión comercial futura por invertir el orden Recomendar→Ejecutar** o por sesgar la Secuencia óptima hacia Estrategias que generan ingreso a Paradixe en vez de valor esperado real para el cliente — este documento fija la fórmula de la sección 8 sobre Impacto/Costo/Tiempo/Riesgo explícitamente para prevenir ese sesgo.
- **Riesgo de que el Playbook Empresarial se construya antes de tiempo** por presión de valorización futura del ecosistema — este documento fija explícitamente que no se diseña sin evidencia real (sección 10.1), y esa barrera no debe bajarse por atractivo comercial.

## Preguntas abiertas

Ninguna nueva sobre el diseño. La integración técnica con los Motores del Ecosistema y el mecanismo de vigilancia de Estrategias Adaptativas (Decisiones pendientes) son de Fase 2.

## Decisiones pendientes

1. Contrato de integración con los Motores del Ecosistema como fuente de datos para Estrategias de software (AD-INT, Fase 2) — mismo gap heredado de revisiones anteriores.
2. Mecanismo técnico de vigilancia de condiciones para Estrategias Adaptativas (AD-ARQ, Fase 2, sección 8.2).
3. Validar el modelo de Valor Esperado (sección 8) contra al menos un caso real ejecutado antes de subir el Confidence Level por encima de 35%.
4. Decidir, cuando exista evidencia real suficiente, si el Playbook Empresarial (sección 10.1) requiere una entidad propia en una futura versión de AD-005/AD-006 — no se decide en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial bajo el nombre "Recomendación de Recursos" (renombrado desde "Marketplace" del árbol original v3.1) | Quinto documento de Funcionalidades |
| v1.0 — Revisión 2 | 2026-07-14 | Renombrado a "Motor de Estrategias Empresariales". Cambio de objeto de razonamiento: de Recurso a Capacidad a Estrategia. Flujo obligatorio de 11 pasos. 15 tipos de Estrategia en 5 clusters, cada uno mapeado a una entidad AD-005 ya existente. Recursos internos primero elevado a Principio Permanente. Separación explícita Confidence Level / Impacto Esperado. Ciclo de aprendizaje ampliado para AD-FUNC-09 | Instrucción explícita del Board: los empresarios no compran recursos, compran capacidades; la recomendación es consecuencia de una estrategia, no el objetivo |
| v1.0 — Revisión 3 | 2026-07-14 | Se evaluó y descartó un tercer nombre ("Motor de Evolución Empresarial") por colisión con AD-004 y sobre-alcance frente a la Declaración de Misión (sección 0). Se agregó el cluster "Recuperación" (Estrategia de recuperación ante crisis, ligada a Leyes 6-7). Se agregaron Estrategias Compuestas/híbridas (sección 5.1). Se agregó Horizonte temporal obligatorio (5 categorías) y los campos Probabilidad de éxito, Esfuerzo esperado y Complejidad, todos distinguidos explícitamente entre sí (sección 6). Se formalizó que las Estrategias compiten como conjunto dentro del Board Room, reutilizando AD-CMP-02 sin mecanismo nuevo (sección 8.1). Se agregaron Estrategias Adaptativas (árboles condición→acción), verificadas contra la Regla de Entidades sin crear ninguna (sección 8.2). Se registró el Playbook Empresarial como activo futuro del Learning Engine, explícitamente no construido todavía por falta de evidencia real (sección 10.1) | Observaciones del Board tras revisar la Revisión 2: faltaba horizonte temporal, estrategias híbridas, estrategias adaptativas, y el reconocimiento del Playbook Empresarial como activo futuro de alto valor |
| v1.0 — Corrección Editorial Final | 2026-07-14 | Corrección exclusiva de los 4 hallazgos de severidad Alta/Media de la Architectural Consistency Review, sin reabrir el modelo: (1) corregido "15 tipos de estrategia" a "16" en la tabla del flujo (§2, paso 5); (2) movida la referencia a AD-FUNC-05 en AD-003 v1.1 de "Dependencias" a "Documentos relacionados", restaurando unidireccionalidad; (3) clasificadas explícitamente Estrategias Compuestas, Horizonte Temporal y Playbook Empresarial como Decisión de Diseño en el encabezado; (4) separado el invariante permanente del flujo de razonamiento de su implementación actual de 11 pasos, dejando la taxonomía específica como Decisión de Diseño evolucionable. Marcado Ready for Gate Review | Instrucción explícita del Board tras la Architectural Consistency Review: corregir únicamente los hallazgos detectados, sin nueva ronda de rediseño |
| v1.0 — APPROVED FOR GATE REVIEW | 2026-07-14 | Aprobación formal del Board: documento considerado cerrado, sin valor adicional en seguir iterándolo — "el hecho de que la revisión de consistencia solo encontrara correcciones editoriales y no problemas de arquitectura es una muy buena señal." Sin cambios de contenido. Se congela como dependencia estable del resto del árbol | Cierre del ciclo de revisión de AD-FUNC-05 tras la Corrección Editorial Final |
