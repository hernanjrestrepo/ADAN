# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.9)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1).
**Estado de la WO-000:** Fase 1 (Fundamentos) completa: AD-000 a AD-005, Anexo y Ciclo Dominio. AD-006 es el siguiente documento.
**Supersede a:** `WO-000_INDICE_MAESTRO_v3.8.md`.
**Naturaleza de este cambio:** cierre de fase + primer documento bajo la nueva metodología de construcción.

---

## 0. Qué cambió respecto a v3.8

1. **AD-005 — Enterprise Domain Model, construido y congelado.** Primer documento producido bajo la metodología nueva instruida por el Board: *se construye, se autoaudita, se congela, se continúa* — sin ronda de revisión previa a su entrega, con validación del Board posterior y no bloqueante salvo que encuentre una contradicción objetiva de alto impacto.
2. Selecciona **26 entidades núcleo** de los 172 conceptos candidatos del Ciclo Dominio — la reducción más grande de alcance de toda la WO-000 hasta ahora, aplicando en conjunto el Criterio de Admisión (universalidad + no ser propiedad transversal + Principio de Emergencia + Economía Conceptual).
3. Incorpora por referencia (sin duplicar) las 10 Leyes Dinámicas del Workshop de Comportamientos como reglas formales del dominio.
4. Cierra formalmente las tres colisiones de nombre pendientes desde el Enterprise Taxonomy Workshop (Proyecto/Iniciativa, Decisión/Decisión de Negocio/Elección de Diseño, Evento/Suceso Empresarial, Documento con atributo Origen).

---

## 1. Estado de aprobación

| Código | Documento | Estado | Versión vigente |
|---|---|---|---|
| AD-000 a AD-004 | Núcleo filosófico | **Aprobados y congelados** | v1.0 / v2.0 |
| ANEXO-MPI | Meta-Principios de Ingeniería | **Aprobado y congelado** | v2.0 |
| — | Ciclo Dominio (3 workshops) | Aprobado como base para AD-005 | — |
| **AD-005** | **Enterprise Domain Model** | **Construido y autoauditado — congelado bajo la nueva metodología** | v1.0 |
| AD-006 | Domain Model (software) | No iniciado — siguiente paso | — |

---

## 2. Nota de cierre

Con AD-005 completo, **Fase 1 (Fundamentos) de la WO-000 queda cerrada en su totalidad**: identidad (AD-001), reglas de sistema (AD-002), vocabulario (AD-003), evolución (AD-004), meta-principios de ingeniería (Anexo), y ahora el modelo del mundo empresarial (AD-005) — 26 entidades, 2 propiedades transversales, 4 dimensiones de identidad, 10 leyes dinámicas. El siguiente documento, AD-006 (Domain Model de software), traduce estas 26 entidades a estructuras operables — y, por la Regla de Entidades (v3.1 §1) más el nuevo vínculo de dependencia explícito, no puede introducir ninguna entidad de negocio que no esté ya aquí.
