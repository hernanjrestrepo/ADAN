# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.2)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1).
**Estado de la WO-000:** En construcción de contenido. `AD-000` aprobado y congelado. `AD-001` en redacción.
**Supersede a:** `WO-000_INDICE_MAESTRO_v3.1.md` (retirado, no eliminado — cadena de evidencia: v1 → v2 → v3 → v3.1 → v3.2).
**Naturaleza de este cambio:** editorial, no estructural — igual que v3.1. Ningún documento se agregó, quitó o movió de categoría.

---

## 0. Qué cambió respecto a v3.1 (changelog)

Un solo cambio: se agregan los **6 Estándares Permanentes de Redacción**, fijados por el Board al aprobar AD-000, que rigen la voz y profundidad de los 57 documentos restantes de la WO-000. No afectan el árbol, las dependencias ni los códigos — solo cómo se escribe cada documento a partir de ahora.

---

## 1. Estándares Permanentes de Redacción (nuevo — aplican a todo documento desde AD-001 en adelante)

Estos 6 estándares se suman a los Estándares Editoriales de v3.1 (no duplicación, estructura de cierre obligatoria, Confidence Level, registro de decisiones, Prueba de Reconstrucción) — no los reemplazan, los profundizan. Mientras v3.1 fijaba *estructura*, estos fijan *nivel de ambición*.

**Regla 1 — No describimos software, describimos sistemas empresariales.** Un documento de la WO-000 no explica cómo funciona una aplicación; explica cómo funciona una capacidad de negocio, y la aplicación es la forma en que esa capacidad se ejecuta hoy.

**Regla 2 — No describimos implementación, describimos comportamiento.** Salvo en la categoría Arquitectura (Fase 2, deliberadamente técnica), ningún documento nombra un framework, un modelo de IA específico, un proveedor de infraestructura o un precio — esos son detalles de una época, y el documento debe seguir siendo cierto cuando esos detalles cambien.

**Regla 3 — Todo concepto importante se define una única vez.** Ya establecida como "regla de no duplicación" en v3.1 — se reafirma aquí como principio de redacción, no solo de estructura: si un concepto ya tiene dueño (un documento donde se define), todo lo demás lo referencia por código, nunca lo redefine con otras palabras.

**Regla 4 — Toda decisión importante se justifica.** Ya establecida como "registro de decisiones" en v3.1 — se reafirma aquí: ninguna afirmación de peso se presenta sin la razón detrás de ella, incluso cuando esa razón es incómoda.

**Regla 5 — Todo documento pasa la Prueba de Reconstrucción.** Ya establecida en v3.1 — se reafirma como el estándar mínimo de aceptación, no como aspiración.

**Regla 6 — No se optimiza para escribir más rápido; se optimiza para no tener que rediseñar el producto dentro de tres años.** La calidad de la especificación es prioritaria sobre la velocidad de producción. Un documento que ahorra una hora de redacción hoy pero obliga a una versión estructural en seis meses no cumplió su propósito.

**Consecuencia práctica de estas 6 reglas:** cada documento de la WO-000 aspira a ser documentación fundacional —el tipo de documento que sigue vigente 10-20 años después de escrito—, no un documento técnico, comercial ni un informe. AD-000 es la primera aplicación completa de este estándar; es la vara con la que se mide todo lo que sigue.

---

## 2. Estado de aprobación de documentos redactados

Tabla de seguimiento, nueva en v3.2 — antes no existía porque no había documentos de contenido redactados. Se actualiza según avanza la Fase 1, no reemplaza el Historial de cambios de cada documento individual.

| Código | Documento | Estado | Versión vigente |
|---|---|---|---|
| AD-000 | Paradixe Ecosystem Vision | **Aprobado y congelado** | v1.0 |
| AD-001 | Product DNA | En redacción | — |

---

## 3. Referencia al árbol completo

El detalle de los 58 documentos (Objetivo, Alcance, Dependencias, Prioridad, Estado de insumos, Responsable, Páginas, Complejidad) permanece sin cambios en `WO-000_INDICE_MAESTRO_v3.1.md`, retirado pero vigente como fuente de las tablas — no se reproduce aquí, en cumplimiento de la Regla 3 de este mismo archivo.

---

## 4. Nota de cierre

AD-000 quedó aprobado y congelado el 2026-07-14. A partir de aquí, el trabajo de la WO-000 es puramente de construcción de contenido siguiendo el backbone ya fijado en v3.1: `AD-001 Product DNA` es el siguiente documento, redactado bajo los 6 Estándares Permanentes de esta versión.
