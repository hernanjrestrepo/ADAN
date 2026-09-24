---
Código: AD-003
Nombre: Product Language
Versión: v1.2
Estado: Construido. Cambio menor sobre v1.1 — no reabre la aprobación del Board sobre el resto del documento, solo la entrada "Score"
Confidence Level: 65%
Fecha: 2026-07-17
Responsable (autor): Célula D (Claude Code), WO-000 Sprint 2
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-003 — Product Language (v1.2)

> Este documento no es un glosario. Un glosario define palabras; esto define un **lenguaje controlado**: cada término tiene una definición oficial, una definición explícitamente prohibida, sinónimos aceptados y prohibidos, contexto de uso, dependencias con otros términos, y un responsable identificable.

**Qué cambia en v1.2:** una sola entrada, "Score" (sección 1). AD-FUNC-07 (Sistema de Scoring), al escribirse, encontró que el ejemplo "Founder Score" usado en v1.0/v1.1 colisiona exactamente con la razón por la que AD-006 ya había renombrado "Fundador" a "Usuario Principal" — el mismo hallazgo que AD-FUNC-06 ya había corregido para su escalera de Identidad Progresiva. Se reemplaza el ejemplo por "Score del Responsable" y se completa el campo "Responsable del concepto", que en v1.0/v1.1 estaba marcado como *(pendiente)* a la espera de que AD-FUNC-07 se escribiera. El resto del documento (los otros 20 términos, la entrada "Motor (de Capacidad)" de v1.1) permanece sin cambios.

**Nivel de contenido de este documento:** sin cambios respecto a v1.0 — mixto por naturaleza.

---

## 1. Vocabulario del Producto

*(Los términos "Ecosistema Paradixe", "ADÁN", "Orquestador", "Motor (de Capacidad)", "Gemelo Digital", "Empresa", "Proyecto", "Nivel", "Card", "Workspace", "Decisión", "Evidencia", "Entregable", "Agente", "Board Room" no cambian respecto a v1.0/v1.1 — no se repiten aquí.)*

### Score — entrada actualizada en v1.2

- **Definición oficial:** la cuantificación objetiva del estado de una dimensión evaluable de una Empresa o de su Usuario Principal (ej. Score del Responsable, Business Score), siempre acompañada de su nivel de confianza (AD-002 regla 1.9). Especificación completa de significado de producto en AD-FUNC-07; de cálculo en AD-ARQ-10.
- **Definición prohibida:** no es una opinión estética del sistema — todo Score debe ser trazable a la evidencia que lo produjo (AD-002 reglas 1.1, 1.2). No es un noveno concepto de "confianza" separado — el nivel de confianza es un atributo de cada Score, nunca un Score aparte (AD-FUNC-07 §6).
- **Sinónimos aceptados:** el nombre calificado específico ("Score del Responsable", "Venture Score") es preferible a "el score" genérico si hay ambigüedad.
- **Sinónimos prohibidos:** "calificación", "nota" — connotan evaluación escolar, no evidencia de negocio. "Founder Score" — nombre retirado por AD-FUNC-07 §0, colisionaba con el mismo sesgo de "solo startups" que AD-006 ya había corregido al renombrar "Fundador" a "Usuario Principal".
- **Contexto de uso:** siempre calificado por tipo cuando exista ambigüedad de cuál se discute.
- **Documentos donde aparece:** Chat 1.docx (origen); AD-FUNC-01 (los 6 Scores de diagnóstico secuencial); formalización completa en AD-FUNC-07.
- **Responsable del concepto:** AD-FUNC-07 *(completado en esta versión — antes pendiente)*.
- **Fecha de creación:** origen del proyecto; completado 2026-07-17 en esta v1.2.
- **Nivel de estabilidad:** Estable.
- **Dependencias:** Evidencia, Confidence Level.

---

## 2. Vocabulario del Proceso de Documentación (WO-000)

Sin cambios respecto a v1.0/v1.1.

---

## Dependencias

- AD-000 Paradixe Ecosystem Vision
- AD-001 Product DNA
- AD-002 Principios del Sistema (v2.0)

## Documentos relacionados

- Todo lo heredado de v1.0/v1.1 permanece vigente.
- AD-FUNC-07 Sistema de Scoring — motivo de esta versión (misma relación unidireccional que AD-FUNC-05: AD-003 no depende de AD-FUNC-07, fue quien motivó completar este término)

## Impacto sobre otros módulos

1. Cualquier documento futuro que use "Founder Score" como ejemplo debe corregirse a "Score del Responsable".

## Riesgos

Heredados de versiones anteriores, sin cambios.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Heredadas de v1.1, sin cambios.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial: lenguaje controlado de 21 términos | Cuarto documento de la WO-000 |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal del Board | Cierre del ciclo de revisión de AD-003 |
| v1.1 | 2026-07-14 | Ampliación de "Motor (de Capacidad)" para cubrir Capacidad del cliente | Requerido por AD-FUNC-05 |
| v1.1 — Corrección Editorial Final | 2026-07-14 | Referencia a AD-FUNC-05 movida de Dependencias a Documentos relacionados | Hallazgo de la Architectural Consistency Review de AD-FUNC-05 |
| v1.2 | 2026-07-17 | Entrada "Score" actualizada: ejemplo "Founder Score" reemplazado por "Score del Responsable"; "Responsable del concepto" completado de *(pendiente)* a "AD-FUNC-07" | Hallazgo H-3 de la auditoría de WO-000 Sprint 1; corrección aplicada al escribir AD-FUNC-07 |
