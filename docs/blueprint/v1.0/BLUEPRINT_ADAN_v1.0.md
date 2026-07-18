# BLUEPRINT CONSOLIDADO ADÁN — v1.0

**Producido por:** Célula D, WO-000 Sprint 5 · **Fecha:** 2026-07-17
**Fuente única de verdad funcional** de la cadena WO-000 → WO-012 (Plan Maestro de Ejecución ADÁN v1.0, §0.3).

Este documento no repite el contenido de cada AD-XXX — sería duplicación directa, prohibida por la Regla de No Duplicación (AD-002 v3.1 §1). Unifica el árbol, resuelve las contradicciones detectadas en la auditoría de Sprint 1, y da el mapa completo para cualquier célula que necesite ubicar una pieza del dominio.

---

## 1. Fundamentos (AD-000 a AD-008) — completos, aprobados

| Doc | Nombre | Versión vigente | Qué fija |
|---|---|---|---|
| AD-000 | Paradixe Ecosystem Vision | v1.0 | ADÁN como componente de un ecosistema mayor (EVA, ARQAI, ATO, Genexis, CSI, Marketplace, Paradixe Capital), nunca aislado |
| AD-001 | Product DNA | v1.1 | Misión ("diseñar, validar, construir, operar, transformar y escalar"), qué NO es ADÁN, qué nunca hará, Principio de Emoción Reflejada |
| AD-002 | Principios del Sistema | v2.0 | 10 reglas de sistema (trazabilidad, versión, confianza declarada, Economía Conceptual...) |
| AD-003 | Product Language | **v1.2** | Lenguaje controlado — 21 términos + Score actualizado en esta WO |
| AD-004 | Product Evolution | v1.1 | Qué puede/no puede cambiar; Criterio de Existencia §3.1; Regla de Entidades |
| AD-005 | Enterprise Domain Model | v1.0 | 26 entidades del dominio empresarial, 10 Leyes Dinámicas |
| AD-006 | Domain Model (Software) | **v1.2** | Traducción a 38 entidades (26+12) + Score actualizado en esta WO |
| AD-007 | Gemelo Digital | v1.1 | Límite de agregación Empresa+Proyecto, no entidad nueva |
| AD-008 | Objetos del Sistema | v1.0 | 4 Patrones de estado (A: Ciclo de Aprobación, B: Progreso Secuencial, C: Registro Permanente, D: Contenedor Continuo) |

## 2. Comportamientos (AD-CMP-01 a 06) — completos, aprobados

| Doc | Nombre | Qué fija |
|---|---|---|
| AD-CMP-01 | Progresión entre Niveles | Avance por evidencia, Patrón B |
| AD-CMP-02 | Consenso Multiagente | Procedimiento de convergencia entre Agentes, escalación de discrepancia material |
| AD-CMP-03 | Comportamiento de Decisiones | Ciclo de vida del objeto Decisión, Patrón A |
| AD-CMP-04 | Memoria y Contexto | 5 capas (Global→Proyecto→Nivel→Card→Conversación), Regla de no repetición |
| AD-CMP-05 | Evidencia y Scoring | Jerarquía de validez de evidencia, proceso conversación→Score |
| AD-CMP-06 | Digital Twin Lifecycle | Nace/crece/cambia/se divide/se fusiona/se archiva |

## 3. Funcionalidades (AD-FUNC-01 a 09) — completas en esta WO

| Doc | Nombre | Estado | Qué fija |
|---|---|---|---|
| AD-FUNC-01 | Los 7 Niveles | Aprobado, congelado definitivamente | El Dolor → Escalamiento, 3 preguntas por Nivel |
| AD-FUNC-02 | Board Room | Aprobado | Autoridad de ejecución vs. fundamentación, Master Orchestration Flow |
| AD-FUNC-03 | Experience Engine | Aprobado | 7 Emociones objetivo, una por Nivel |
| AD-FUNC-04 | Gamification Engine | Construido, autoauditado | 7 Ritmos psicológicos, Regla Anti-Manipulación |
| AD-FUNC-05 | Motor de Estrategias Empresariales | **APPROVED FOR GATE REVIEW** | Flujo de 11 pasos, 16 tipos de Estrategia en 6 clusters, recursos internos primero |
| AD-FUNC-06 | Onboarding | **APPROVED FOR GATE REVIEW** | Identidad Progresiva, multicanal, recuperación, Prueba del Minuto Cero |
| AD-FUNC-07 | Sistema de Scoring | Construido, autoauditado (esta WO) | 8 Scores en 2 familias (6 diagnóstico + 2 continuos) |
| AD-FUNC-08 | User Journey Map | Construido, autoauditado (esta WO) | 7 etapas mapeadas 1:1 contra Identidad Progresiva |
| AD-FUNC-09 | Learning Engine | Construido, autoauditado (esta WO) | 3 loops de aprendizaje, Playbook especificado, 6 Salvaguardas |

## 4. Motores (referencia cruzada rápida)

- **Motor de Estrategias Empresariales** — AD-FUNC-05
- **Experience Engine** — AD-FUNC-03
- **Gamification Engine** — AD-FUNC-04
- **Motor de Scoring (cálculo)** — AD-ARQ-10, Fase 2, no construido (AD-FUNC-07 fija el significado, no la fórmula)

## 5. Modelo de entidades — 38 totales, ninguna nueva en esta WO

26 de dominio de negocio (AD-005) + 12 operativas de ADÁN (AD-006 §4). Ver AD-006 v1.2 para la tabla completa. Ningún documento de esta WO creó una entidad nueva — Sprint 2-4 verificaron explícitamente contra la Regla de Entidades en cada autoauditoría.

## 6. Knowledge Graph

`docs/blueprint/source/wo-000/knowledge-graph/kg.json` — 91 nodos, 101 edges, 1 referencia hacia adelante esperada (AD-ARQ-10, Fase 2, no bloqueante).

## 7. Contradicciones detectadas en Sprint 1 — resolución

| Hallazgo | Resolución | Dónde |
|---|---|---|
| H-1 — Dos taxonomías de Score | Reconciliadas: 8 nombres = 2 familias (diagnóstico + continuo); "de confianza" no es score separado; "por objetivo/estrategia" es regla genérica | AD-FUNC-07 §0 |
| H-2 — Gap de integración AD-INT (ATO, Marketplace) | Diferido a Fase 2, no bloqueante | Heredado, sin cambio |
| H-3 — "Founder Score" obsoleto | Corregido: AD-003 v1.2, AD-006 v1.2 | Ver ambos documentos |
| H-4 — "Capacidad Operativa" sin resolver en AD-005 §6 | Diferido, no bloqueante | Heredado, sin cambio |
| H-5 — Comunidad como entidad propia | Diferido, no bloqueante | Heredado, sin cambio |

**Ninguna contradicción bloquea el cierre de WO-000.**

---

## 8. Qué falta explícitamente (Fase 2, fuera del alcance de este blueprint)

- AD-UX (categoría completa) — Fase 2 de la WO-000 original, no de esta cadena de ejecución.
- AD-ARQ (Motor de Scoring, integraciones técnicas) — se construye como código en WO-001 a WO-006 de esta cadena, no como documento de especificación adicional.
- AD-INT (integraciones con ATO y Marketplace del Ecosistema) — gap heredado, Fase 2.
- Mecanismos de negocio (Renovación/suscripción, Embajador/referidos) — explícitamente fuera de esta especificación de producto, materia de WO-100 (Business Architecture).

Este blueprint es la fuente de verdad **funcional**. El código de WO-001 en adelante debe poder trazarse a un requisito de este blueprint (ver `TRACEABILITY.md`, Sprint 6).
