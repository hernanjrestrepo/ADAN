# Blueprint consolidado de ADÁN — v1.1

**Fecha:** 2026-09-24 · **WO:** WO-096 · **Redacción:** Claude Code
**Parte de:** `adan-platform/docs/blueprint/v1.0/BLUEPRINT_ADAN_v1.0.md` (Build A, WO-000 Sprint 5, 2026-07-17).
**Qué es:** el mapa de lectura del blueprint. Dice qué versión de cada documento está vigente, qué fija cada uno y dónde está. No repite el contenido de los documentos (Regla de No Duplicación, AD-002).

> **Qué cambió respecto a v1.0.** La v1.0 se declaraba "fuente única de verdad funcional". Esta versión retira esa frase, porque la Regla 6 de `AD-GOV-0001` prohíbe que un documento se la dé a sí mismo. Qué documentos son canónicos lo fija `AD-ROOT-0001 §5`. Además, esta versión:
> - incorpora AD-000 v2.0 (AD-DEC-0002);
> - apunta todas las rutas a `docs/wo-000/`;
> - agrega el estado de implementación en Build C según la auditoría de 2026-09.

---

## 1. Fundamentos (`docs/wo-000/00-fundamentos/`)

| Doc | Nombre | Vigente | Qué fija |
|---|---|---|---|
| AD-000 | Paradixe Ecosystem Vision | **v2.0** | Lugar de ADÁN en el ecosistema. Desde AD-DEC-0002: EVA (antes ARQAI) = ventas y marketing; Genexis interno; Comunidad; agentes por tiempo |
| AD-001 | Product DNA | v1.1 | Misión, qué no es ADÁN, qué nunca hará, Principio de Emoción Reflejada |
| AD-002 | Principios del Sistema | v2.0 | 10 reglas de sistema: trazabilidad, versión, confianza declarada, Economía Conceptual… |
| AD-003 | Product Language | **v1.2** | Lenguaje controlado: 21 términos, con "Score" actualizado |
| AD-004 | Product Evolution | v1.1 | Qué puede y qué no puede cambiar; Criterio de Existencia; Regla de Entidades |
| AD-005 | Enterprise Domain Model | v1.0 | 26 entidades del dominio empresarial y 10 Leyes Dinámicas |
| AD-006 | Domain Model (Software) | **v1.2** | 38 entidades: las 26 de negocio y 12 operativas |
| AD-007 | Gemelo Digital | v1.1 | Límite de agregación Empresa + Proyecto (no es una entidad nueva) |
| AD-008 | Objetos del Sistema | v1.0 | 4 patrones de estado. A: Ciclo de Aprobación · B: Progreso Secuencial · C: Registro Permanente · D: Contenedor Continuo |

## 2. Comportamientos (`docs/wo-000/01-comportamientos/`)

| Doc | Nombre | Qué fija |
|---|---|---|
| AD-CMP-01 | Progresión entre Niveles | Avance por evidencia, Patrón B |
| AD-CMP-02 | Consenso Multiagente | Convergencia entre agentes y escalación de discrepancias materiales |
| AD-CMP-03 | Comportamiento de Decisiones | Ciclo de vida de la Decisión, Patrón A |
| AD-CMP-04 | Memoria y Contexto | 5 capas (Global → Proyecto → Nivel → Card → Conversación) y regla de no repetición |
| AD-CMP-05 | Evidencia y Scoring | Jerarquía de validez de la evidencia; de la conversación al Score |
| AD-CMP-06 | Digital Twin Lifecycle | El Gemelo nace, crece, cambia, se divide, se fusiona y se archiva |

## 3. Funcionalidades (`docs/wo-000/02-funcionalidades/`)

| Doc | Nombre | Qué fija |
|---|---|---|
| AD-FUNC-01 | Los 7 Niveles | Del Dolor al Escalamiento, 3 preguntas por Nivel. 7 Niveles confirmados en AD-DEC-0002 (decisión 9) |
| AD-FUNC-02 | Board Room | Autoridad de ejecución frente a fundamentación; Master Orchestration Flow |
| AD-FUNC-03 | Experience Engine | 7 emociones objetivo, una por Nivel |
| AD-FUNC-04 | Gamification Engine | 7 ritmos psicológicos y Regla Anti-Manipulación |
| AD-FUNC-05 | Motor de Estrategias Empresariales (el archivo se llama "Recomendación de Recursos") | Flujo de 11 pasos, 16 tipos de estrategia en 6 grupos, recursos internos primero |
| AD-FUNC-06 | Onboarding | Identidad Progresiva, multicanal, Prueba del Minuto Cero |
| AD-FUNC-07 | Sistema de Scoring | 8 Scores en 2 familias: 6 de diagnóstico y 2 continuos |
| AD-FUNC-08 | User Journey Map | 7 etapas, mapeadas 1 a 1 con la Identidad Progresiva |
| AD-FUNC-09 | Learning Engine | 3 ciclos de aprendizaje, Playbook y 6 salvaguardas |

## 4. Motores

| Motor | Especificación | Cálculo o implementación |
|---|---|---|
| Estrategias Empresariales | AD-FUNC-05 | WO-117 |
| Experience Engine | AD-FUNC-03 | WO-116 |
| Gamification Engine | AD-FUNC-04 | WO-116 |
| Scoring | AD-FUNC-07 (qué significa cada Score) | AD-ARQ-10 (la fórmula) no se escribió; se construye en WO-107 |
| Learning Engine | AD-FUNC-09 | WO-118 |

## 5. Estado de implementación en Build C

Según la auditoría `docs/auditoria/AUDITORIA_ADAN_2026-09.md`, actualizada con WO-094 y WO-095.

| Pieza del blueprint | En Build C | WO que la completa |
|---|---|---|
| Nivel 1 (AD-FUNC-01) | Chat, Board Room de 4 roles, diagnóstico, Gate con aprobación del cliente | WO-107 (Gate por evidencia) y WO-108 |
| Niveles 2–7 | No existen | WO-110 → WO-115 |
| Board Room de 7 roles (AD-FUNC-02) | Existe en `/board`, separado del Nivel 1 | WO-099 |
| Patrón A (AD-008, AD-CMP-03) | Propuesta del Board y aprobación del cliente (WO-095) | WO-098 (todas las decisiones) |
| Gemelo Digital (AD-007) | Parcial: proyecto, niveles, documentos, scores y eventos | WO-098 |
| Memoria de 5 capas (AD-CMP-04) | Ventana y resumen de conversación (WO-095); EMS por empresa | WO-099 |
| Scoring de 8 Scores (AD-FUNC-07) | Un Score de problema calculado por palabras clave | WO-107 |
| Experience, Gamification, User Journey, Estrategias, Learning | No existen | WO-116 (incluye AD-FUNC-08), WO-117, WO-118 |
| Onboarding (AD-FUNC-06) | Registro simple | WO-108 |
| Agentes por tiempo, Marketplace, Comunidad (AD-000 v2.0) | No existen | WO-109, WO-120, WO-121 |

## 6. Modelo de entidades

38 entidades: 26 de negocio (AD-005) y 12 operativas (AD-006 §4). Build C implementa un subconjunto en SQLite. La migración a las 38 entidades en PostgreSQL es WO-091, partiendo de la migración Alembic de Build A (37 tablas).

## 7. Knowledge Graph

`docs/wo-000/knowledge-graph/kg.json`: 9 fundamentos, 6 comportamientos, 9 funcionalidades, 39 conceptos, 26 principios y 106 relaciones (2026-09-24). Tiene una referencia pendiente, a AD-ARQ-10.

## 8. Contradicciones y su estado

| Hallazgo | Estado | Dónde |
|---|---|---|
| H-1: dos taxonomías de Score | Resuelto: 8 nombres en 2 familias | AD-FUNC-07 §0 |
| H-2: falta integrar ATO y Marketplace (AD-INT) | Diferido. Con AD-000 v2.0 las integraciones son cuatro: EVA, ATO, Genexis y CSI | AD-000 v2.0 §4 |
| H-3: "Founder Score" obsoleto | Resuelto | AD-003 v1.2, AD-006 v1.2 |
| H-4: "Capacidad Operativa" sin resolver | Diferido | AD-005 §6 |
| H-5: Comunidad como entidad propia | **Resuelto como concepto** en AD-000 v2.0. Si además es entidad se decide en WO-121 (Regla de Entidades) | AD-000 v2.0 §3 |
| H-6 *(nuevo)*: EVA y ATO se solapan en generación de demanda | Abierto | AD-000 v2.0, Riesgos |
| H-7 *(nuevo)*: ERP, contabilidad y facturación sin dueño en el ecosistema | Abierto | AD-000 v2.0, Preguntas abiertas; AD-001 v1.1 §1.1 |
| H-8 *(nuevo)*: el concepto `playbook-empresarial` está duplicado en `kg.json` | Abierto (menor) | `kg.json`, `concepts` |

## 9. Qué falta especificar

- **AD-UX:** la categoría completa.
- **AD-ARQ-10:** la fórmula del Scoring (WO-107).
- **AD-INT:** los contratos con EVA, ATO, Genexis y CSI (WO-119).
- **Mecanismos de negocio:** precios, billing, Marketplace, red de comisiones y AAA. Van en WO-100, con AD-DEC-0002 como insumo.

---

## Historial

| Versión | Fecha | Cambio |
|---|---|---|
| v1.0 | 2026-07-17 | Consolidación de Build A (WO-000 Sprint 5), en `adan-platform/docs/blueprint/v1.0/` |
| v1.1 | 2026-09-24 | Se trae a `docs/wo-000/`. Además: se retira la autodeclaración de fuente única (Regla 6), AD-000 pasa a v2.0, se agrega el estado de implementación en Build C y se suman los hallazgos H-6 a H-8 |
