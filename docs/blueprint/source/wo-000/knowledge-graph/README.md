# Knowledge Graph de la WO-000

Propuesta por el Board el 2026-07-14, al aprobar AD-002. No es infraestructura del producto ADÁN — es infraestructura de la propia especificación, para que la coherencia entre 58 documentos y potencialmente más de 2.000 páginas sea verificable mecánicamente, no solo de memoria.

## Qué es `kg.json`

Un grafo simple en JSON con cuatro tipos de nodo y un solo arreglo de relaciones (`edges`):

- **`documents`** — cada `AD-XXX`, con su código, versión vigente, estado (`approved` / `draft`), a qué otros documentos depende, y su historial de versiones cuando aplica. Se registra **un nodo por código de documento**, no uno por versión — el historial de versiones vive en el campo `version_history`, no como nodos separados, para que el grafo no crezca sin control cada vez que un documento se revisa (aplicación directa de Economía Conceptual, AD-002 §1.10, al propio grafo).
- **`concepts`** — cada término del lenguaje controlado (AD-003 y los que se agreguen después), con dónde se define, quién es su dueño autoritativo (a veces un documento que todavía no existe, marcado `authoritative_owner_status: "pendiente"`), y su nivel de estabilidad.
- **`principles`** — los Principios Permanentes de AD-001 y las Reglas de Sistema de AD-002, con relaciones `operationalizes` entre ellas (qué regla de AD-002 traduce a la práctica qué principio de AD-001).
- **`edges`** — todas las relaciones que no encajan como campo simple de un nodo: `depends_on`, `defined_by`, `referenced_in`, `awaits_full_spec`, `operationalizes`, y casos especiales como `name_collision_risk` (usado para registrar el hallazgo real de AD-003 sobre "Decisión" vs. "Decisión de Diseño" — el grafo también sirve para llevar registro de riesgos arquitectónicos encontrados durante las autoauditorías, no solo de dependencias limpias).

## Cómo se mantiene

Este archivo se actualiza como parte obligatoria de la autoauditoría previa a la entrega de cualquier documento nuevo (ver la pregunta de autoauditoría "¿qué impacto tendrá este documento sobre documentos futuros?", respondida en el chat de aprobación de cada documento desde AD-003 en adelante). El procedimiento, en cuatro pasos:

1. Agregar un nodo en `documents` para el nuevo `AD-XXX`, con sus `depends_on` reales (los mismos que aparecen en la sección "Dependencias" del documento).
2. Agregar un nodo en `concepts` por cada término genuinamente nuevo que el documento introduce — si el documento no introduce ningún concepto nuevo (como AD-003, que solo formalizó vocabulario ya disperso), no se agrega nada aquí, y eso es una señal sana, no una omisión.
3. Agregar un nodo en `principles` si el documento declara una regla permanente nueva.
4. Agregar los `edges` correspondientes — como mínimo, uno `depends_on` por cada dependencia declarada; adicionalmente, cualquier `awaits_full_spec` que el nuevo documento resuelva (cambiando el nodo de `concepts` correspondiente para que ya no diga `authoritative_owner_status: "pendiente"`).

No existe todavía un motor de consultas sobre este grafo — hoy es un archivo de datos estructurado, pensado para inspección manual o para cargarse con cualquier herramienta que lea JSON. Su propósito inmediato es responder preguntas como *"¿qué documentos dependen del Gemelo Digital?"* leyendo el archivo directamente. Su propósito de largo plazo, señalado por el Board, es alimentar el RAG interno de ADÁN una vez que AD-ARQ-06 (RAG) se construya — este archivo es, en ese sentido, el primer dato de entrenamiento real de esa futura capacidad, no solo una ayuda de mantenimiento de la documentación.

## Estado actual

4 documentos (`AD-000` a `AD-003`), 21 conceptos, 16 principios, con sus relaciones. Dos riesgos ya registrados en el grafo desde su primera versión: la colisión de nombre "Decisión" / "Decisión de Diseño", y la lista de conceptos que todavía esperan su especificación completa en un documento que aún no existe (`awaits_full_spec`).
