# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.4)

**Tipo de documento:** Árbol documental — **APROBADO Y CONGELADO** (sin cambios de estructura desde v3.1).
**Estado de la WO-000:** En construcción de contenido. `AD-000` y `AD-001` aprobados y congelados. `AD-002` en v2.0 (Draft). `AD-003` en Draft, entregado junto con su primera autoauditoría formal.
**Supersede a:** `WO-000_INDICE_MAESTRO_v3.3.md`.
**Naturaleza de este cambio:** de proceso — cambia cómo se produce y revisa cada documento, no la estructura del árbol.

---

## 0. Qué cambió respecto a v3.3 (changelog)

Tres cambios:

1. **Nuevo flujo de entrega: autoauditoría obligatoria previa.** A partir de AD-003, ningún documento se entrega al Board sin que Claude Code responda primero, explícitamente, diez preguntas de autoauditoría — ver sección 1. El flujo pasa de "escribir → revisar → corregir → aprobar" a "escribir → autoauditar → entregar con la auditoría incluida".
2. **Nuevo principio permanente: Economía Conceptual**, agregado como AD-002 §1.10 (v2.0). Referenciado aquí, no duplicado — ver AD-002 v2.0.
3. **Nueva infraestructura: Knowledge Graph de la WO-000** (`docs/wo-000/knowledge-graph/`), que registra documentos, conceptos, principios y sus relaciones en formato estructurado, mantenido como parte de cada autoauditoría desde ahora.

---

## 1. Flujo de Autoauditoría Obligatoria (nuevo)

Antes de entregar cualquier documento nuevo o cualquier revisión de un documento aprobado, Claude Code responde explícitamente estas diez preguntas, y las presenta junto con el documento — nunca en su lugar, nunca después de forma separada:

1. ¿Existe alguna contradicción con AD-000?
2. ¿Existe alguna contradicción con AD-001?
3. ¿Existe alguna contradicción con AD-002?
4. ¿Qué conceptos nuevos aparecen? ¿Realmente deben existir, o alguno ya está definido en otro documento?
5. ¿Se está duplicando conocimiento? Si la respuesta es sí, eliminar la duplicación antes de entregar.
6. ¿Qué impacto tendrá este documento sobre los documentos futuros?
7. ¿Qué riesgo arquitectónico aparece por primera vez?
8. ¿Qué nivel de confianza real tiene el documento — con justificación, no un número arbitrario?
9. Si este documento desapareciera, ¿qué perdería el producto? Si la respuesta es "muy poco", el documento probablemente sobra.
10. Si este documento permanece igual durante diez años, ¿seguiría siendo válido? Si no, está mal diseñado.

Como los primeros tres documentos de la WO-000 (AD-000, AD-001, AD-002) ya fueron aprobados bajo el flujo anterior de revisión manual del Board, no requieren autoauditoría retroactiva — el flujo nuevo aplica desde AD-003 en adelante.

---

## 2. Referencia a Economía Conceptual

El décimo principio permanente de AD-002 (v2.0, §1.10) — que ningún concepto nuevo se incorpora sin demostrar que resuelve un problema real, que no puede expresarse con conceptos existentes, y que su valor supera la complejidad que agrega — se declara en AD-002, no se repite aquí, en cumplimiento de la Regla de No Duplicación (v3.1 §1).

---

## 3. Knowledge Graph de la WO-000

Nueva infraestructura, en `docs/wo-000/knowledge-graph/` (`kg.json` + `README.md`). Registra documentos, conceptos, principios y relaciones en formato estructurado. Su propósito inmediato es responder mecánicamente preguntas de coherencia ("¿qué depende del Gemelo Digital?"); su propósito de largo plazo, alimentar el RAG interno de ADÁN cuando AD-ARQ-06 exista. Se actualiza como parte obligatoria de la autoauditoría (pregunta 6) de cada documento nuevo.

---

## 4. Estado de aprobación de documentos redactados

| Código | Documento | Estado | Versión vigente |
|---|---|---|---|
| AD-000 | Paradixe Ecosystem Vision | **Aprobado y congelado** | v1.0 |
| AD-001 | Product DNA | **Aprobado y congelado** | v1.0 |
| AD-002 | Principios del Sistema | Draft (v1.0 aprobada y superseded el mismo día) | v2.0 |
| AD-003 | Product Language | Draft — entregado con autoauditoría, pendiente de aprobación | v1.0 |

---

## 5. Referencia al árbol completo

El detalle de los 58 documentos permanece sin cambios en `WO-000_INDICE_MAESTRO_v3.1.md` — no se reproduce aquí.

---

## 6. Nota de cierre

A partir de AD-003, el Board dejó de revisar documento por documento en varias rondas y pasó a un modelo de auditoría integrada: Claude Code se convierte en su propio primer QA. Esto no reduce el estándar de calidad — lo traslada de "el Board encuentra los problemas" a "Claude Code debe encontrarlos primero, o explicar por qué no los hay". La autoauditoría de AD-003 (entregada junto con ese documento) es la primera aplicación real de este flujo.
