# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.11)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1).
**Estado de la WO-000:** **Fase 1 (Fundamentos) completa.** AD-000 a AD-007, Anexo de Meta-Principios, y los tres workshops del Ciclo Dominio. Fase 2 (Comportamientos, Funcionalidades, UX, Arquitectura, IA, Operación, Platform Services, Integraciones) es el siguiente bloque de trabajo.
**Supersede a:** `WO-000_INDICE_MAESTRO_v3.10.md`.
**Naturaleza de este cambio:** cierre de Fase 1 completa.

---

## 0. Qué cambió respecto a v3.10

1. **AD-006 pasó a v1.1** — cambio menor: se reescribió la sección 0 con la forma precisa de la instrucción del Board ("AD-006 no crea entidades nuevas *del dominio empresarial*", no de la totalidad del documento) y se agregó el diagrama de los Dos Dominios. Ninguna entidad, atributo o relación cambió.
2. **AD-007 — Gemelo Digital, construido y congelado.** Se definió como **límite de agregación** (1:1:1 con Empresa y Proyecto) — no como entidad de datos nueva —, tras pasar explícitamente la prueba del Principio de Emergencia en su propia sección 0. Recupera el lenguaje de "genoma" reservado desde el Enterprise Taxonomy Workshop, sin convertirlo en concepto formal.
3. **Fase 1 (Fundamentos) de la WO-000 queda cerrada por completo.**

---

## 1. Estado de aprobación — Fase 1 completa

| Código | Documento | Estado | Versión vigente |
|---|---|---|---|
| AD-000 | Paradixe Ecosystem Vision | Aprobado y congelado | v1.0 |
| AD-001 | Product DNA | Aprobado y congelado | v1.0 |
| AD-002 | Principios del Sistema | Aprobado y congelado | v2.0 |
| AD-003 | Product Language | Aprobado y congelado | v1.0 |
| AD-004 | Product Evolution | Aprobado y congelado | v1.0 |
| ANEXO-MPI | Meta-Principios de Ingeniería | Aprobado y congelado | v2.0 |
| — | Ciclo Dominio (3 workshops) | Aprobado como base | — |
| AD-005 | Enterprise Domain Model | Construido y autoauditado — congelado | v1.0 |
| AD-006 | Domain Model (Software) | Aprobado y congelado | v1.1 |
| AD-007 | Gemelo Digital | Construido y autoauditado — congelado | v1.0 |

**Total de entidades formalizadas: 26 de negocio (AD-005) + 12 operativas de ADÁN (AD-006), unidas bajo un límite de agregación único (AD-007).**

---

## 2. Nota de cierre — fin de Fase 1

Ocho documentos, un anexo transversal y tres workshops de descubrimiento después, la WO-000 tiene una identidad de producto (AD-001), reglas de sistema (AD-002), vocabulario controlado (AD-003), reglas de evolución (AD-004), disciplina de ingeniería (Anexo), y un modelo completo del mundo que ADÁN entiende y de cómo lo representa (AD-005, AD-006, AD-007). Ningún documento de Fase 2 puede introducir una entidad de dominio nueva sin abrir una nueva versión de AD-005, AD-006 o AD-007 — la Regla de Entidades (v3.1 §1) sigue vigente sin cambios. El siguiente bloque de trabajo es Fase 2, empezando por la categoría Funcionalidades (AD-FUNC), que ya tiene su primer punto de partida resuelto: AD-FUNC-01 puede ahora fijar el número definitivo de Niveles contra una entidad `Nivel` formalizada.
