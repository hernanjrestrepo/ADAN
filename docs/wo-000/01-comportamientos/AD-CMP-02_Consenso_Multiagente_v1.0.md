---
Código: AD-CMP-02
Nombre: Comportamiento de Consenso Multiagente
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 60%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-CMP-02 — Comportamiento de Consenso Multiagente

> Especifica cómo múltiples Agentes producen una sola respuesta — la regla de "nunca cinco respuestas" ya declarada en AD-001 §11 se vuelve aquí un procedimiento verificable, no solo una intención.

**Nivel de contenido:** Principio Permanente en su totalidad.

---

## 1. El procedimiento de consenso

Cuando más de un Agente participa en analizar una pregunta o generar una recomendación, el procedimiento es:

1. **Cada Agente involucrado produce su análisis de forma independiente**, dentro de su especialidad declarada (AD-003, entidad Agente).
2. **Se identifica el nivel de acuerdo entre los análisis.** Si coinciden en la sustancia (aunque difieran en fraseo), se sintetiza una sola respuesta sin exponer el proceso interno — el usuario recibe una respuesta de ADÁN, no cinco de sus Agentes.
3. **Si hay discrepancia material** (dos Agentes llegan a recomendaciones opuestas o a evidencia contradictoria), no se promedia ni se elige arbitrariamente una — se activa el procedimiento de la sección 2.

## 2. Resolución de discrepancias materiales

Una discrepancia es material cuando afecta la recomendación final que recibirá el cliente, no cuando es una diferencia de matiz. Ante una discrepancia material:

- Se registra como un desacuerdo explícito, con la posición de cada Agente y su evidencia respectiva — nunca se descarta silenciosamente la posición perdedora.
- Se resuelve por evidencia ponderada (Meta-Principio 3 del Anexo, evidencia sobre opinión), no por jerarquía de Agente ni por votación simple.
- Si la evidencia de ambas posiciones es comparable y no permite un desempate objetivo, la discrepancia se comunica al cliente explícitamente (Regla 1.6 de AD-002, toda IA debe justificar) en lugar de forzar una síntesis artificial — esto es una aplicación directa del Principio de Humildad Intelectual (AD-001 §6.1): presentar varias respuestas válidas cuando de verdad las hay, en vez de fingir una sola certeza.

## 3. Cuándo se exponen los Agentes

Por defecto, los Agentes son invisibles (AD-001 §1, AD-003). Se exponen únicamente en dos casos: (a) el usuario decide inspeccionarlos explícitamente (AD-UX-11, Consola de Agentes), o (b) existe una discrepancia material sin resolver (sección 2) — ahí, mostrar qué Agente sostiene qué posición no es opcional, es parte de la transparencia exigida por Regla 1.6 de AD-002.

---

## Dependencias

- AD-006 Domain Model v1.1 (entidad Agente)
- AD-002 Principios del Sistema v2.0 (reglas 1.1, 1.6, 1.9)
- AD-001 Product DNA §11, §6.1

## Documentos relacionados

- AD-CMP-03 Comportamiento de Decisiones (una discrepancia material no resuelta puede escalar a un registro formal de Decisión)
- AD-FUNC-02 Board Room (mecánica de debate multiagente visible, se apoya directamente en este documento)
- AD-UX-11 Agentes (Consola)

## Impacto sobre otros módulos

AD-FUNC-02 (Board Room) no puede definir su propia lógica de consenso — debe heredar el procedimiento de este documento, aplicado a un contexto de debate más formal (con cliente y terceros invitados).

## Riesgos

- Riesgo de que "discrepancia material" quede como criterio subjetivo hasta que exista un caso real que lo calibre.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial | Undécimo documento de la WO-000 |
