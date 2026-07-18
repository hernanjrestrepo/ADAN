# Matriz de Trazabilidad — Blueprint ADÁN v1.0

**Producido por:** Célula D, WO-000 Sprint 6 · **Fecha:** 2026-07-17
Cada requisito recibe un ID único `BP-####`. Cobertura: 100% de los documentos del blueprint tienen al menos un BP asignado.

## Fundamentos

| BP | Requisito | Documento | WO destino |
|---|---|---|---|
| BP-0001 | Ecosistema Paradixe, ADÁN como componente | AD-000 | WO-001 (config de entorno), Fase 2 (AD-INT) |
| BP-0002 | Misión, qué NO es ADÁN, qué nunca hará | AD-001 | Toda WO — principio rector transversal |
| BP-0003 | 10 reglas de sistema (trazabilidad, versión, confianza) | AD-002 | WO-001 Sprint 3-4 (Contrato Base en modelos) |
| BP-0004 | Lenguaje controlado (21 términos) | AD-003 v1.2 | WO-001 (naming en código), WO-010 (UX en español) |
| BP-0005 | Criterio de Existencia, Regla de Entidades | AD-004 | Todo AD-FUNC — ya verificado en cada uno |
| BP-0006 | 26 entidades de dominio empresarial | AD-005 | WO-001 Sprint 4 |
| BP-0007 | 38 entidades de software (26+12), Score N:1 Empresa/Usuario Principal | AD-006 v1.2 | WO-001 Sprint 4 |
| BP-0008 | Gemelo Digital — límite de agregación | AD-007 | WO-004 |
| BP-0009 | 4 Patrones de estado (A/B/C/D) | AD-008 | WO-001 Sprint 4, WO-004 Sprint 2 (motor de eventos) |

## Comportamientos

| BP | Requisito | Documento | WO destino |
|---|---|---|---|
| BP-0010 | Avance por evidencia (Patrón B) | AD-CMP-01 | WO-002, WO-007 |
| BP-0011 | Consenso multiagente, escalación de discrepancia | AD-CMP-02 | WO-002 Sprint 3, WO-005 Sprint 2 |
| BP-0012 | Ciclo de vida del objeto Decisión (Patrón A) | AD-CMP-03 | WO-005 |
| BP-0013 | 5 capas de memoria, no repetición | AD-CMP-04 | WO-003 |
| BP-0014 | Jerarquía de evidencia, conversación→Score | AD-CMP-05 | WO-006 Sprint 1 |
| BP-0015 | Ciclo de vida del Gemelo Digital | AD-CMP-06 | WO-004 |

## Funcionalidades

| BP | Requisito | Documento | WO destino |
|---|---|---|---|
| BP-0016 | Los 7 Niveles, 3 preguntas por Nivel | AD-FUNC-01 | WO-007 |
| BP-0017 | Board Room, autoridad ejecución/fundamentación | AD-FUNC-02 | WO-005 |
| BP-0018 | 7 Emociones objetivo por Nivel | AD-FUNC-03 | WO-006 Sprint 2 |
| BP-0019 | 7 Ritmos psicológicos, Regla Anti-Manipulación | AD-FUNC-04 | WO-006 Sprint 3 |
| BP-0020 | Flujo de 11 pasos del Motor de Estrategias | AD-FUNC-05 §2 | WO-005 Sprint 3 |
| BP-0021 | 16 tipos de Estrategia en 6 clusters | AD-FUNC-05 §5 | WO-005 Sprint 3 |
| BP-0022 | Recursos internos primero | AD-FUNC-05 §4 | WO-005 Sprint 3 |
| BP-0023 | Identidad Progresiva (7 etiquetas) | AD-FUNC-06 §3.1 | WO-007 Sprint 1 |
| BP-0024 | Onboarding multicanal, recuperación, minuto cero | AD-FUNC-06 §3.2-3.3 | WO-007 |
| BP-0025 | 8 Scores en 2 familias | AD-FUNC-07 | WO-006 Sprint 1 |
| BP-0026 | 7 etapas de User Journey | AD-FUNC-08 | WO-010 |
| BP-0027 | 3 loops de aprendizaje | AD-FUNC-09 §3 | WO-008 Sprint 2 |
| BP-0028 | Playbook Empresarial (mecanismo, sin construir) | AD-FUNC-09 §5 | Diferido — no construir sin evidencia real |
| BP-0029 | 6 Salvaguardas del Learning Engine | AD-FUNC-09 §6 | WO-008 — restricciones obligatorias del diseño |

## Estado especial

| BP | Requisito | Estado |
|---|---|---|
| BP-0030 | AD-FUNC-05 marcado formalmente **APPROVED** | Cumplido — ver frontmatter de AD-FUNC-05, "APPROVED FOR GATE REVIEW", aprobación explícita del Board registrada en su Historial de cambios |

## Cobertura

**29 requisitos de contenido + 1 de gobernanza = 30 BP.** 100% de los documentos del blueprint (9 Fundamentos + 6 Comportamientos + 9 Funcionalidades) tienen al menos un BP asignado. Ningún BP queda sin WO destino, salvo BP-0028 (Playbook), diferido explícitamente por diseño, no por omisión.
