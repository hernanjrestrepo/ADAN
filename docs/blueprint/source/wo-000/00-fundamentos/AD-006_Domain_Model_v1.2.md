---
Código: AD-006
Nombre: Domain Model (Software)
Versión: v1.2
Estado: Aprobado y congelado (v1.1). Cambio menor en esta versión — no reabre la aprobación del Board, solo la fila "Score" de la sección 4
Confidence Level: 66%
Fecha de aprobación: 2026-07-17
Responsable (autor): Célula D (Claude Code), WO-000 Sprint 2
Aprobador: Hernán / Junta Directiva
Supersede a: AD-006_Domain_Model_v1.1.md (aprobado y congelado — ver su Historial de cambios)
---

# AD-006 — Domain Model (Software) — v1.2

> AD-005 respondió qué es una empresa. Este documento responde cómo la representa el software de ADÁN.

**Qué cambia en v1.2:** una sola fila, "Score" (sección 4). AD-FUNC-07 (Sistema de Scoring), al construirse, encontró que el **Score del Responsable** (antes "Founder Score", renombrado por la misma colisión ya corregida en AD-FUNC-06) es N:1 con **Usuario Principal**, no con Empresa — la definición de v1.0/v1.1 solo contemplaba "N:1 con Empresa". Se amplía la cardinalidad para cubrir ambos casos. No es una entidad nueva — es la generalización de una relación ya existente de una entidad ya existente, aplicando el mismo principio de Economía Conceptual que ya rigió cada cambio anterior de este árbol. El resto del documento (secciones 0-3, Hallazgos 1-3, las 38 entidades) permanece exactamente igual que v1.1.

**Nivel de contenido:** sin cambios respecto a v1.1.

---

## 0. Los Dos Dominios de AD-006

*(Sin cambios respecto a v1.1 — ver ese documento para el detalle completo: restricción de "no crear entidades nuevas" aplica solo al dominio empresarial, no a la totalidad del documento.)*

## 1. Principio de Traducción sin Pérdida

*(Sin cambios respecto a v1.1.)*

## 2. Contrato Base

*(Sin cambios respecto a v1.1 — 7 atributos heredados por las 38 entidades, implementando las 10 reglas de AD-002.)*

## 3. Traducción del Dominio de Negocio (26 de 26, sin adición ni omisión)

*(Sin cambios respecto a v1.1 — ver ese documento para la tabla completa de las 26 entidades de AD-005 traducidas a software.)*

---

## 4. Entidades Operativas de ADÁN

Sin cambios salvo la fila **Score**, actualizada en esta versión:

| Entidad | Definición | Relación principal |
|---|---|---|
| Usuario | Persona con acceso a ADÁN | N:M con Proyecto |
| Usuario Principal *(renombrado de "Fundador" — Hallazgo 1)* | El Usuario responsable de un Proyecto ante ADÁN | 1:N con Proyecto; N:1 con Empleado cuando es parte formal de la Empresa |
| Proyecto | El contenedor de software donde ADÁN acompaña a una Empresa | 1:1 con Empresa |
| Workspace | La interfaz que envuelve un Proyecto | 1:1 con Proyecto |
| Nivel | Etapa del acompañamiento | 1:N con Proyecto |
| Card | Unidad de trabajo dentro de un Nivel | 1:N con Nivel |
| Conversación | Sesión de chat dentro de una Card | 1:N con Card |
| Agente | Rol interno especializado | N:M con Conversación |
| Tarea | Unidad operativa de trabajo dentro de un Nivel | 1:N con Nivel o Card |
| Decisión *(de ADÁN)* | Registro de una recomendación aprobada por el cliente | Puede originarse en o producir una Decisión de Negocio |
| **Score** *(actualizado en v1.2)* | Evaluación que ADÁN hace de una Empresa **o de su Usuario Principal** (Score del Responsable, Business Score...) — distinta de Indicador | **N:1 con Empresa o con Usuario Principal** (ampliado en v1.2 — antes solo "N:1 con Empresa"); declara Confidence Level (Contrato Base) |
| Evento | Registro técnico append-only | Puede generarse a partir de un Suceso Empresarial |

---

## 5. Hallazgos

*(Hallazgos 1, 2 y 3 sin cambios respecto a v1.1 — ver ese documento.)*

**Hallazgo 4 — Score no era solo N:1 con Empresa (nuevo en v1.2).** AD-FUNC-07, al especificar el significado de producto de cada Score, encontró un caso real —Score del Responsable— que evalúa a la persona, no a la Empresa. Ampliar la cardinalidad de una relación ya existente no es lo mismo que crear una entidad nueva: Score sigue siendo una sola entidad de datos, con una relación ahora polimórfica (Empresa o Usuario Principal), igual que Riesgo ya es polimórfico sobre varias entidades en AD-005 §3. Mismo patrón, aplicado aquí por primera vez a una entidad operativa de AD-006.

---

## Dependencias

*(Sin cambios respecto a v1.1.)*

## Documentos relacionados

- AD-007 Gemelo Digital
- AD-CMP-01 a AD-CMP-06
- Todo documento de AD-FUNC y AD-UX
- **AD-FUNC-07 Sistema de Scoring — motivo de esta versión**

## Impacto sobre otros módulos

1. AD-ARQ (Fase 2), al implementar Score en base de datos, debe modelar la relación como polimórfica (Empresa o Usuario Principal), no como clave foránea fija a Empresa.
2. Resto de impactos heredados de v1.1 sin cambios.

## Riesgos

Heredados de v1.1, sin cambios. Ninguno nuevo — es una generalización de cardinalidad, no una entidad ni una regla nueva.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Heredadas de v1.1, sin cambios.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial | Séptimo documento de la WO-000 |
| v1.0 — Aprobada | 2026-07-14 | Aprobación formal, congelada | Cierre del ciclo de revisión |
| v1.1 | 2026-07-14 | Reescritura de la sección 0 (restricción de entidades solo al dominio empresarial) | Aclaración metodológica del Board |
| v1.2 | 2026-07-17 | Fila "Score" actualizada: cardinalidad ampliada de "N:1 con Empresa" a "N:1 con Empresa o con Usuario Principal"; ejemplo "Founder Score" reemplazado por "Score del Responsable" | Requerido por AD-FUNC-07 (Sistema de Scoring), hallazgo H-3 de la auditoría de WO-000 Sprint 1 |
