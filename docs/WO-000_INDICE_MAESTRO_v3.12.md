# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.12)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1).
**Estado de la WO-000:** **WO-000 — FASE 1: COMPLETADA**, verificada por Gate Review en dos pasadas. 15 de 24 documentos originales de Fase 1 (Fundamentos + Comportamientos). AD-FUNC (Funcionalidades, 9 documentos) es la siguiente categoría.
**Supersede a:** `WO-000_INDICE_MAESTRO_v3.11.md`.
**Naturaleza de este cambio:** cierre real de Fase 1, tras corregir una definición de alcance que se había estrechado informalmente durante la conversación.

---

## 0. Qué cambió respecto a v3.11

Un Gate Review (`WO-000_GATE_REVIEW_FASE1.md`) encontró que "Fase 1" se venía usando, desde v3.6, para referirse solo a Fundamentos (9 documentos) — pero la definición original del árbol (v3, línea 190) es **Fundamentos + Comportamientos + Funcionalidades = 24 documentos**, y Fase 1 termina al cerrar las primeras dos categorías (15 documentos), no la primera sola. Se completaron los 7 documentos faltantes: **AD-008 — Objetos del Sistema** y **AD-CMP-01 a AD-CMP-06**. Una segunda pasada del Gate Review confirmó: cero referencias rotas en el Knowledge Graph, cero entidades duplicadas, cero dependencias sin resolver. AD-007 subió a v1.1 (cierre de su pregunta abierta, sin cambio estructural).

---

## 1. Estado de aprobación — Fase 1 completa (15 documentos)

| Categoría | Documentos | Estado |
|---|---|---|
| Fundamentos (9) | AD-000, AD-001, AD-002, AD-003, AD-004, AD-005, AD-006, AD-007, AD-008 | **Todos aprobados y congelados** |
| Anexo transversal | Meta-Principios de Ingeniería | Aprobado y congelado, v2.0 |
| Ciclo Dominio | 3 workshops (Taxonomía, Relaciones, Comportamientos de negocio) | Aprobados como base |
| Comportamientos (6) | AD-CMP-01 a AD-CMP-06 | **Todos aprobados y congelados** |

**Total de entidades y reglas fijadas:** 26 entidades de negocio + 12 operativas de ADÁN (38), 2 propiedades transversales, 4 dimensiones derivadas, 10 leyes dinámicas de dominio, 4 patrones de estado de objeto (AD-008), 6 comportamientos formales de ADÁN (AD-CMP).

---

## 2. Referencia al árbol completo

El detalle de los 58 documentos permanece sin cambios en `WO-000_INDICE_MAESTRO_v3.1.md`.

---

## 3. Nota de cierre

**WO-000 — FASE 1: COMPLETADA.** El Gate Review demostró su valor dos veces en la misma sesión: primero encontrando que "Fase 1" se había estrechado informalmente sin que nadie lo notara, y después confirmando mecánicamente —no narrativamente— que los siete documentos faltantes cierran esa brecha sin dejar referencias rotas ni dependencias sin resolver. Empieza ahora **AD-FUNC — Funcionalidades**, comenzando por AD-FUNC-01 — Los 7 Niveles, que puede escribirse cumpliendo (no violando) las dependencias que el propio árbol le exige desde su origen.
