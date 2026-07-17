---
Código: AD-CMP-04
Nombre: Comportamiento de Memoria y Contexto
Versión: v1.0
Estado: Construido y autoauditado. Congelado bajo la metodología "se construye, se autoaudita, se congela, se continúa"
Confidence Level: 61%
Fecha: 2026-07-14
Responsable (autor): CC (Claude Code)
Aprobador: Hernán / Junta Directiva (validación en el próximo Gate Review)
---

# AD-CMP-04 — Comportamiento de Memoria y Contexto

> Especifica qué se recuerda, qué se resume y qué se descarta — sin el motor técnico que lo implementa (eso es AD-ARQ-04/05). La regla de fondo, ya declarada en AD-001 §1: ADÁN nunca vuelve a preguntar algo que ya sabe.

**Nivel de contenido:** Principio Permanente en su totalidad.

---

## 1. Jerarquía conceptual de contexto

Cinco capas, cada una anidada dentro de la anterior, siguiendo directamente la jerarquía de entidades ya fijada en AD-006 §4:

```
Global (todo lo que ADÁN sabe, a través de todos los Proyectos)
  └─ Proyecto (todo lo que se sabe de una Empresa específica — vive en su Gemelo Digital)
      └─ Nivel (lo relevante a la etapa actual del acompañamiento)
          └─ Card (lo relevante a un proceso específico dentro del Nivel)
              └─ Conversación (la sesión de chat actual)
```

Cada capa hereda de la que la contiene, nunca al revés — una Conversación puede consultar el contexto de su Card, Nivel, Proyecto y el conocimiento Global; el conocimiento Global nunca depende de una Conversación específica.

## 2. Qué se recuerda permanentemente

Todo lo que el Gemelo Digital (AD-007) agrega: las 26 entidades de negocio de AD-005 y su historial completo, más las Decisiones, Scores y Eventos generados por el Proyecto correspondiente. Esto no es una decisión de este documento — es la consecuencia directa de la Regla 1.5 de AD-002 (nada se pierde) aplicada a través del Gemelo Digital.

## 3. Qué se resume, y cuándo

Cuando una Card o un Nivel se completa (Patrón B, AD-008), se genera un resumen que sintetiza: qué se decidió, qué evidencia lo respalda, qué queda pendiente. Ese resumen —no la Conversación completa que lo produjo— es lo que asciende a la capa contenedora (de Card a Nivel, de Nivel a Proyecto). La Conversación original no se borra (Regla 1.5), pero deja de ser lo que otras Cards o Niveles consultan por defecto — así se evita que el contexto crezca sin control a medida que un Proyecto avanza, sin perder nada de lo ya dicho.

## 4. Regla de no repetición

Antes de que un Agente formule una pregunta al cliente, debe verificar si la respuesta ya existe en alguna capa de contexto disponible para la Conversación actual (sección 1). Si existe, no se pregunta de nuevo — se usa lo que ya se sabe, y se le comunica al cliente qué se está asumiendo, para que pueda corregirlo si cambió. Esta regla es la forma operativa exacta de la frase ya fijada en AD-001 §1: "nunca pierde contexto, nunca olvida una decisión anterior".

---

## Dependencias

- AD-007 Gemelo Digital (memoria permanente, capa Proyecto)
- AD-006 Domain Model v1.1 (jerarquía Proyecto → Nivel → Card → Conversación)
- AD-002 Principios del Sistema v2.0 (reglas 1.5, 1.8)

## Documentos relacionados

- AD-UX-07 Chat/Conversación, AD-UX-12 Memoria y RAG — consumen esta jerarquía directamente
- AD-ARQ-04 Memoria (Motor Técnico), AD-ARQ-05 Context Engineering — implementación técnica de lo que aquí se declara solo conceptualmente

## Impacto sobre otros módulos

AD-ARQ-04 y AD-ARQ-05 no pueden diseñar una jerarquía de contexto distinta a la de la sección 1 — deben implementarla, no reinventarla.

## Riesgos

- Riesgo de que "resumen" pierda matices importantes al ascender de capa — mitigado porque la Conversación original nunca se borra y sigue siendo consultable bajo demanda.

## Preguntas abiertas

Ninguna nueva.

## Decisiones pendientes

Ninguna decisión de negocio pendiente en este documento.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| v1.0 | 2026-07-14 | Creación inicial | Décimo tercer documento de la WO-000 |
