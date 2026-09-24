---
Código: AD-003
Nombre: Product Language
Versión: v1.1
Estado: Construido. Cambio menor sobre v1.0 (Aprobada y Congelada) — no reabre la aprobación del Board sobre el resto del documento, solo la entrada "Motor (de Capacidad)"
Confidence Level: 65%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-003 — Product Language (v1.1)

> Este documento no es un glosario. Un glosario define palabras; esto define un **lenguaje controlado**: cada término tiene una definición oficial, una definición explícitamente prohibida, sinónimos aceptados y prohibidos, contexto de uso, dependencias con otros términos, y un responsable identificable. Ningún documento posterior de la WO-000 puede redefinir un término aquí fijado — lo referencia, o propone una nueva versión de este documento si el término necesita cambiar.

**Qué cambia en v1.1:** una sola entrada, "Motor (de Capacidad)" (sección 1). Por instrucción explícita del Board, al construir AD-FUNC-05 (Revisión 2 — Motor de Estrategias Empresariales), se necesitaba que "Capacidad" cubriera tanto lo que el Ecosistema Paradixe provee a ADÁN (sentido ya fijado en v1.0) como lo que una Empresa cliente necesita desarrollar (sentido nuevo, requerido por AD-FUNC-05). Se evaluó crear un término nuevo ("Capacidad Empresarial") y se descartó explícitamente — la Regla de Economía Conceptual (AD-002 v2.0 §1.10) exige demostrar que un concepto no es expresable con lo existente antes de crear uno nuevo, y en este caso sí lo es: ambos sentidos son la misma idea (una habilidad de producir un resultado) aplicada a dos niveles distintos, ya distinguibles por contexto gramatical — exactamente el mismo patrón ya usado para "Decisión" / "Decisión de Negocio". El resto del documento (los otros 20 términos, ambos vocabularios, autoaudioría original) permanece sin cambios y sigue Aprobado y Congelado.

**Nivel de contenido de este documento:** sin cambios respecto a v1.0 — mixto por naturaleza (ver v1.0 para el detalle completo).

---

## 1. Vocabulario del Producto

*(Los términos "Ecosistema Paradixe", "ADÁN", "Orquestador" no cambian respecto a v1.0 — no se repiten aquí; ver AD-003 v1.0 para su definición completa y vigente.)*

### Motor (de Capacidad) — entrada actualizada en v1.1

- **Definición oficial:** "Capacidad" es el concepto general — **una habilidad de producir un resultado específico**, de negocio o de operación. Es aplicable en dos niveles, distinguibles siempre por contexto: (a) una capacidad que el Ecosistema Paradixe provee a ADÁN (sentido original, v1.0); (b) una capacidad que una Empresa cliente necesita desarrollar o ya posee (sentido añadido en v1.1, requerido por AD-FUNC-05 — Motor de Estrategias Empresariales). Un **Motor** es uno de los mecanismos posibles para proveer una capacidad del primer tipo: cualquier proveedor —interno o externo al Ecosistema Paradixe— que ejecuta una capacidad específica que ADÁN orquesta pero no posee en exclusiva (ej. Genexis como motor de construcción). Ver AD-000 §4, principio 3.
- **Definición prohibida:** "Motor" y "Capacidad" no son sinónimos — un Motor es un proveedor; una Capacidad es lo que ese proveedor entrega. Nombrar "el motor de X" no implica que sea el único proveedor posible de esa capacidad, ahora ni en el futuro. Cuando "Capacidad" se usa en el sentido (b) — la de una Empresa cliente — un Motor del Ecosistema es solo **una** de las alternativas posibles para cerrarla, nunca la única ni la primera por defecto (AD-FUNC-05 exige evaluar recursos internos de la Empresa antes que cualquier alternativa externa, incluidos los Motores del Ecosistema).
- **Sinónimos aceptados:** "motor de construcción" (para la capacidad de desarrollo de software específicamente, sentido a).
- **Sinónimos prohibidos:** "proveedor exclusivo", "dependencia" sin calificar que es reemplazable (sentido a); "recurso" como sinónimo genérico de Capacidad (sentido b) — un recurso es un medio posible para cerrar una Capacidad, no la Capacidad misma (ver AD-FUNC-05 §3).
- **Contexto de uso:** "Motor" se usa siempre acompañado de la capacidad que ejecuta, y siempre al describir la relación de ADÁN con el resto del Ecosistema Paradixe (sentido a) — nunca la relación de ADÁN con el cliente. "Capacidad" a secas se usa también para describir lo que una Empresa cliente necesita o posee (sentido b, AD-FUNC-05) — ahí nunca lleva la palabra "Motor" pegada salvo que se esté nombrando explícitamente a un Motor del Ecosistema como una de las alternativas evaluadas.
- **Documentos donde aparece:** AD-000 (sentido a, definición original); AD-FUNC-05 (sentido b, añadido en esta versión).
- **Responsable del concepto:** AD-000 (sentido a); AD-FUNC-05 (sentido b).
- **Fecha de creación:** 2026-07-14 (sentido a); ampliado 2026-07-14 en esta v1.1 (sentido b).
- **Nivel de estabilidad:** Estable.
- **Dependencias:** Orquestador (sentido a); Objetivo, Meta, Riesgo, Proceso — de donde se deriva una Capacidad del cliente sin ser una entidad nueva (sentido b, ver AD-FUNC-05 §11).

*(El resto de los términos de la sección 1 — Gemelo Digital, Empresa, Proyecto, Nivel, Card, Workspace, Decisión, Score, Evidencia, Entregable, Agente, Board Room — no cambian respecto a v1.0.)*

---

## 2. Vocabulario del Proceso de Documentación (WO-000)

Sin cambios respecto a v1.0 — Comportamiento, Funcionalidad, Principio Permanente, Decisión de Diseño, Confidence Level.

---

## Dependencias

- AD-000 Paradixe Ecosystem Vision
- AD-001 Product DNA
- AD-002 Principios del Sistema (v2.0)

## Documentos relacionados

- Todo lo heredado de v1.0 permanece vigente.
- AD-FUNC-05 Motor de Estrategias Empresariales — motivo de esta versión (AD-003 no depende de AD-FUNC-05 para ser entendido; fue el documento que motivó ampliar el contexto de uso de "Capacidad", relación unidireccional en el sentido opuesto: AD-FUNC-05 depende de este término, no al revés)

## Impacto sobre otros módulos

1. Cualquier documento futuro que necesite referirse a "lo que una Empresa cliente necesita desarrollar" debe usar "Capacidad" (sentido b), nunca inventar un sinónimo nuevo ("habilidad requerida", "competencia faltante") sin verificar primero si Capacidad ya lo cubre.

## Riesgos

- Heredados de v1.0, sin cambios. Ninguno nuevo introducido por esta actualización — es una ampliación de contexto de uso, no una entidad ni una regla nueva.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Heredadas de v1.0, sin cambios (colisión "Decisión"/"Decisión de Diseño"; número de Niveles — ambas ya resueltas por AD-FUNC-01 y pendientes de reflejarse formalmente aquí en una futura versión que toque esos términos directamente).

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: lenguaje controlado de 21 términos | Cuarto documento de la WO-000 |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board, sin cambios de contenido. Se congela | Cierre del ciclo de revisión de AD-003 |
| v1.1 | 2026-07-14 | Se amplía la entrada "Motor (de Capacidad)" para declarar que "Capacidad" es el concepto general —aplicable tanto a lo que el Ecosistema provee a ADÁN como a lo que una Empresa cliente necesita— y que "Motor" es solo uno de los mecanismos posibles de proveerla. No se crea un término nuevo ("Capacidad Empresarial" se evaluó y descartó) — se reutiliza el existente, desambiguado por contexto, mismo patrón que "Decisión"/"Decisión de Negocio" | Requerido por AD-FUNC-05 (Revisión 2 — Motor de Estrategias Empresariales), instrucción explícita del Board de no introducir un término nuevo cuando el existente puede ampliarse |
| v1.1 — Corrección Editorial Final | 2026-07-14 | Se movió la referencia a AD-FUNC-05 de "Dependencias" a "Documentos relacionados" — AD-003 no depende funcionalmente de AD-FUNC-05, la relación real es la opuesta | Hallazgo F2 de la Architectural Consistency Review de AD-FUNC-05: la referencia cruzada violaba la unidireccionalidad documental exigida |
