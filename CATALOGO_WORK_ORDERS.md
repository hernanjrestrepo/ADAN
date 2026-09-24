# Catálogo de Work Orders — ADÁN (WO-090, Sprint 2)

**Fecha:** 2026-07-31 · **Parte de:** WO-090 — Consolidación Oficial de ADÁN Enterprise
**Método:** cada fila proviene de evidencia directa (commit, tag, comentario `# WO-0XX` en código, o sección de documento) — donde no hay evidencia directa, se marca explícitamente en vez de inferir el tema.

---

## 1. Por qué hay tres numeraciones superpuestas

Build A/B y Build C usan el rango **WO-001 a WO-012 dos veces, para cosas distintas**. Esto ya no se corrige retroactivamente (Build A/B queda archivado/referencia, no se renumera su historial cerrado — ver `AD-DEC-0001 §5.2/5.3`), pero de aquí en adelante toda cita a un número de WO **debe indicar la línea** (A/B o C) para no repetir la ambigüedad que causó esta auditoría.

## 2. Línea Build A/B (archivada / referencia técnica) — no se toca

| WO | Tema | Evidencia |
|---|---|---|
| WO-000 | Blueprint Consolidado | tag `blueprint-v1.0` |
| WO-001 | Fundación Técnica | tag `wo-001-done` |
| WO-002 | Núcleo de Agentes y Orquestador | tag `wo-002-done` |
| WO-003 | Memoria + Knowledge Graph | tag `wo-003-done` |
| WO-004 | Gemelo Digital v1 | tag `wo-004-done` |
| WO-005 | Board Room + Estrategias + Planes | tag `wo-005-done` |
| WO-006 | Scoring + Experience + Gamification | tag `wo-006-done` |
| WO-007 | Onboarding + Diagnóstico E2E | tag `wo-007-done` |
| WO-008 | Learning Engine v1 | tag `wo-008-done` |
| WO-009 | Beta: dogfooding real de Paradixe | commit `9775ad100` |
| WO-010 | User Journey Map | `CHAIN_CLOSURE.md` |
| WO-011 | Hardening y Estabilización | tag `wo-011-done` |
| WO-012 | Producción · Baseline Certificada | tag `v1.0.0` |

## 3. Línea Build C (línea oficial desde `AD-DEC-0001`) — numeración propia, conservada tal cual

| WO | Tema | Evidencia |
|---|---|---|
| WO-000 | Blueprint (fuente compartida con A/B) | `docs/wo-000/*`, MD5 idéntico entre líneas |
| WO-001 | Vertical Nivel 1 | `WO-001_CIERRE_DEFINITIVO.md`, "CERRADA" |
| WO-002.1 | Diseño: Agent Orchestration, Cognitive Architecture, Decision Engine, Event Bus, Knowledge Graph, Memory Lifecycle, Tool Architecture | `docs/wo-002.1/*`, capacidades marcadas "Diseñada — Pendiente implementar" en `ADAN_MASTER_ARCHITECTURE_v1.0.md` a fecha 2026-07-24 |
| WO-002.3 | Arquitectura Maestra (documento que consolida y reemplaza los documentos de WO-002.1) | `ADAN_MASTER_ARCHITECTURE_v1.0.md`, "WO de Origen: WO-002.3" |
| WO-003 → WO-010 | **Sin evidencia directa de tema** — no hay comentario `# WO-0XX` en código ni sección de documento que los identifique individualmente. Los módulos `cognitive/`, `oos/`, `dka/`, `tef/`, `ems/`, `nivel1/` existen en `backend/app/` pero no están etiquetados por número de WO en ningún archivo revisado. | — |
| WO-011 | Voice | `backend/tests/test_wo011_to_wo020.py:8,36` |
| WO-012 | Omnichannel | `backend/tests/test_wo011_to_wo020.py:12,62` |
| WO-013 → WO-015 | **Ausentes** — confirmado por grep, no aparecen en ningún archivo de Build C | — |
| WO-016 | Knowledge Quality | `backend/tests/test_wo011_to_wo020.py:18,92` |
| WO-017 | Learning | `backend/tests/test_wo011_to_wo020.py:21,122` |
| WO-018 | Agent Factory | `backend/tests/test_wo011_to_wo020.py:24,156` |
| WO-019 | Plugin Marketplace | `backend/tests/test_wo011_to_wo020.py:28,202` |
| WO-020 | Autonomous Organization | `backend/tests/test_wo011_to_wo020.py:31,251` |

**Nota:** el salto WO-013→WO-015 ausente ocurre *dentro* de la propia numeración de Build C — no es un artefacto de esta consolidación, ya existía antes de esta auditoría.

## 4. Línea de Gobierno / Consolidación (nueva, esta sesión)

| WO | Tema | Estado |
|---|---|---|
| WO-090 | Consolidación Oficial de ADÁN Enterprise (esta WO) | En curso — Sprint 2 de 4 |
| WO-091 | Migración Enterprise — PostgreSQL + pgvector | No iniciada |
| WO-092 | TypeScript | No iniciada |
| WO-093 | Producción Enterprise — CI/CD, observabilidad, seguridad (alcance de "multiempresa" con solapamiento sin resolver contra WO-101-106, ver `AD-ROOT-0001 §4`) | No iniciada |

## 5. Rangos reservados — no tocados por este catálogo

| Rango | Reserva | Fuente |
|---|---|---|
| WO-100 | Business Architecture (precio, billing, legal, IP en disputa) | `docs/WO-000_INDICE_MAESTRO_v2/v3/v3.21.md` — preexistente a los tres Builds |
| WO-101 → WO-106 | Cadena SaaS (multi-tenant, billing, administración) | `CHAIN_CLOSURE.md` (Build B) — requiere aprobación humana separada y Plan Maestro II |

---

## 6. Brechas de este catálogo (honestas, no rellenadas por inferencia)

1. Tema de Build C WO-003 a WO-010: sin evidencia directa. Cerrar esta brecha requeriría leer el código de `cognitive/`, `oos/`, `dka/`, `tef/`, `ems/`, `nivel1/` línea por línea para inferir a qué WO correspondería cada uno — no se hizo en este Sprint porque sería inferencia, no catalogación.
2. No se verificó si WO-013 a WO-015 fueron deliberadamente saltadas (reservadas para algo) o simplemente no se llegaron a nombrar — ningún documento de Build C lo explica.
