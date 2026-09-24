---
Tipo: Checklist interno de verificación — NO es un AD-XXX, NO es una WO nueva
Propósito: verificar mecánicamente, no narrativamente, que Fase 1 está lista antes de avanzar
Fecha: 2026-07-14
Resultado: Primera pasada NO verde (ver sección original). Segunda pasada, tras completar AD-008 y AD-CMP-01 a 06: VERDE. Fase 1 completa según la definición original del árbol (v3, línea 190).
---

# WO-000 — Gate Review de Fase 1

Cada ítem de este checklist se verificó ejecutando una revisión real (lectura de archivos, script de integridad referencial sobre el Knowledge Graph, comparación contra el índice maestro original v3), no narrándolo desde memoria.

## Checklist

| # | Verificación | Resultado | Evidencia |
|---|---|---|---|
| 1 | Todos los documentos de Fundamentos están congelados | ✅ Verde | Encabezados de AD-000 a AD-007 y del Anexo revisados uno por uno; todos en estado "Aprobado y congelado" o equivalente. AD-005 y AD-007 se actualizaron en este Gate Review para reflejar la aprobación final ya dada por el Board, sin cambio de contenido |
| 2 | Todas las dependencias declaradas están completas | ⚠️ Parcial | Las dependencias entre AD-000 y AD-007 son completas y consistentes entre sí. Pero el índice maestro original (v3, fila AD-FUNC-01) declara que ese documento depende de AD-CMP-01 y AD-CMP-05 — ninguno de los dos existe. Ver Hallazgo 1 |
| 3 | El Knowledge Graph no tiene referencias rotas | ✅ Verde, tras una corrección | Se ejecutó un script de integridad referencial sobre `kg.json`. Encontró **una referencia rota real**: dos edges apuntaban a `concept:score`, un nodo que había sido borrado accidentalmente en una edición anterior de esta misma conversación. Se corrigió, redirigiendo esas dos edges a `concept:score-adan`, el nodo correcto tras la resolución de esa colisión en AD-006. Verificado de nuevo tras la corrección: 0 referencias rotas reales (excluyendo referencias hacia adelante, esperadas, a documentos de Fase 2 todavía no escritos) |
| 4 | No existen conceptos duplicados | ✅ Verde | Verificado mecánicamente: las 26 entidades de AD-005 y las 12 entidades operativas de AD-006 tienen cero solapamiento de nombres. Los 21 términos del diccionario de AD-003 no tienen duplicados. Los IDs del Knowledge Graph son únicos entre las cinco categorías (documentos, conceptos, principios, anexos, workshops) |
| 5 | No hay preguntas abiertas que bloqueen el siguiente paso | ⚠️ Parcial — ver Hallazgo 1 | Ninguna de las preguntas abiertas ya registradas (número de Niveles, nombres de Paradixe Capital/Token del Ecosistema, "Artefacto") bloquea nada por sí sola. Pero el Gate Review encontró algo más grave que una pregunta sin resolver: **documentos completos que faltan** |
| 6 | Trazabilidad completa entre AD-000 y AD-007 | ✅ Verde | La cadena de dependencias AD-000 → AD-001 → AD-002 → AD-003 → AD-004 → AD-005 → AD-006 → AD-007 es coherente, sin ciclos, verificada contra el Knowledge Graph |

## Hallazgo 1 — "Fase 1" se venía usando con un alcance más chico que el original (el hallazgo que cambia la recomendación)

Esta conversación empezó a llamar "Fase 1" a "Fundamentos" (AD-000 a AD-008) desde `WO-000_INDICE_MAESTRO_v3.6.md` en adelante, y ese uso se sostuvo el resto de la sesión. Pero el índice maestro original (`WO-000_INDICE_MAESTRO_v3.md`, línea 190, nunca modificado en este punto) define **Fase 1 de otra forma, más amplia**:

> *"Fase 1 (Fundamentos + Comportamientos + Funcionalidades, lo único redactable hasta nueva orden): 24 documentos."*

Es decir, el documento fundacional de toda esta WO-000 —el que nunca se revisó de nuevo en este punto específico— dice que Fase 1 incluye no solo los 9 documentos de Fundamentos, sino también los 6 de **Comportamientos (AD-CMP-01 a 06)** y los 9 de **Funcionalidades (AD-FUNC-01 a 09)**. Fase 2, en la definición original, empieza recién en UX/Arquitectura/IA/Operación/Integraciones — no en AD-FUNC-01.

Verificando qué se construyó realmente contra esa lista de 24:

| Categoría original de Fase 1 | Documentos | Estado real |
|---|---|---|
| Fundamentos (9) | AD-000 a AD-008 | **8 de 9 — falta AD-008, Objetos del Sistema** |
| Comportamientos (6) | AD-CMP-01 a 06 | **0 de 6 — ninguno escrito** |
| Funcionalidades (9) | AD-FUNC-01 a 09 | **0 de 9 — ninguno escrito** |

**Aclaración importante para no generar una alarma que no corresponde:** el "Workshop de Comportamientos" que sí se hizo en esta sesión no es lo mismo que los seis documentos AD-CMP-01 a 06. El workshop modeló las **leyes dinámicas del dominio empresarial** (cómo nace, aprende, crece, se estanca, entra en crisis, se recupera, muere y se reinventa una empresa) — contenido que terminó incorporado en AD-005 §5. Los AD-CMP-01 a 06 son otra cosa: especifican el **comportamiento del propio ADÁN** (Progresión entre Niveles, Consenso Multiagente, Decisiones, Memoria y Contexto, Evidencia y Scoring, Digital Twin Lifecycle) — ninguno de los seis existe todavía.

### ¿AD-008 y los AD-CMP ya emergen de lo que existe? — verificación aplicando el Principio de Emergencia, no solo afirmando

Antes de recomendar escribirlos, se verificó si ya emergen de AD-005/AD-006/AD-007, en cumplimiento del propio Principio de Emergencia (Anexo v2.0 §2):

- **AD-008 (Objetos del Sistema)** — su alcance original es "atributos, estados, ciclo de vida, acciones permitidas, permisos, relaciones, eventos que dispara, versionado" por entidad. De eso, **atributos, relaciones y versionado ya están cubiertos** (AD-005 §2, Workshop de Relaciones, Contrato Base de AD-006). Pero **estados** (¿qué estados atraviesa un Contrato: borrador → firmado → vigente → vencido?), **acciones permitidas** (¿qué operaciones existen sobre cada entidad?), **permisos** (¿quién puede aprobar qué — la mecánica concreta detrás del principio inviolable "ninguna decisión importante avanza sin aprobación explícita del cliente", AD-001 §12) y **eventos que dispara sistemáticamente cada entidad** no están cubiertos en ningún documento existente. No pasa la prueba de Emergencia limpiamente — es un documento genuinamente necesario, no redundante.
- **AD-CMP-01 a 06** — cada uno especifica un comportamiento de ADÁN mencionado y citado docenas de veces a lo largo de Fase 1 (AD-001 §11, AD-002 regla 1.4, AD-006 "Decisión (de ADÁN)"...) pero nunca especificado en su propio documento. No emergen de nada existente — son, literalmente, los documentos pendientes que esas citas prometían.

**Esto no es un error de nadie.** Es exactamente lo que un Gate Review real debe encontrar: la sesión avanzó con enfoque y precisión sobre Fundamentos, y en el camino la definición de "Fase 1" se fue estrechando de forma natural en el lenguaje de la conversación, sin que nadie lo notara hasta comparar contra el documento original.

## Verdict

**No se marca "WO-000 — Fase 1: COMPLETADA"** en el sentido en que el índice original de la WO-000 define Fase 1. Sí se confirma, con evidencia mecánica: **Fundamentos (AD-000 a AD-007) está completo, congelado, y libre de las cinco categorías de defectos que este checklist buscaba** (documentos sin congelar, dependencias rotas, referencias rotas en el grafo, conceptos duplicados, ciclos de trazabilidad). Lo que falta para cerrar Fase 1 en su sentido original es AD-008 y los seis AD-CMP — 7 documentos, no 1.

## Recomendación

Antes de AD-FUNC-01, escribir, en este orden (el mismo que el backbone ya fijado en v3 §12):

1. **AD-008 — Objetos del Sistema** (depende de AD-006, AD-007, AD-002 — todos ya congelados, sin bloqueo)
2. **AD-CMP-01 a AD-CMP-06** (dependen de AD-005/AD-006/AD-002/AD-CMP-06 depende de AD-007 — todos ya congelados)

Recién entonces AD-FUNC-01 puede escribirse cumpliendo su propia dependencia declarada, en vez de violarla o de tener que reabrir el índice para quitársela.

Sobre el orden de Funcionalidades propuesto por el Board (AD-FUNC-01 Los 7 Niveles, luego "AD-FUNC-02 — Flujo Maestro", AD-FUNC-03 Experience Engine, AD-FUNC-04 Gamification Engine): los últimos dos coinciden con el árbol original. El segundo no — el índice original asigna **AD-FUNC-02 a "Board Room"**, no a "Flujo Maestro". Puede ser una idea nueva de documento (en cuyo caso necesita pasar por Economía Conceptual/Emergencia como cualquier otra, y probablemente un código distinto para no desplazar a Board Room) o una referencia a algo ya cubierto con otro nombre — se señala para que el Board aclare la intención antes de asumir un cambio al árbol congelado.

---

## Segunda pasada (tras completar los 7 documentos pendientes)

El Board aprobó la recomendación y encargó, en orden: AD-008, AD-CMP-01, AD-CMP-02, AD-CMP-03, AD-CMP-04, AD-CMP-05, AD-CMP-06. Los siete se construyeron, autoauditaron y congelaron bajo la misma metodología ya validada en AD-005/AD-006/AD-007. Se repite el checklist completo, no solo se asume que "ya se hizo lo pedido":

| # | Verificación | Resultado |
|---|---|---|
| 1 | Los 7 documentos nuevos están congelados | ✅ Verde — headers verificados uno por uno |
| 2 | Las dependencias declaradas de los 24 documentos de Fase 1 (original) resuelven correctamente | ✅ Verde — script de integridad re-ejecutado sobre `kg.json` con los 15 documentos ahora existentes (9 Fundamentos + 6 Comportamientos); AD-FUNC-01 ya puede depender de AD-CMP-01 y AD-CMP-05 sin violación, porque ambos existen |
| 3 | Knowledge Graph sin referencias rotas | ✅ Verde — 0 rotas reales, verificado de nuevo tras agregar 73 nodos totales |
| 4 | Sin conceptos duplicados | ✅ Verde — ningún AD-CMP ni AD-008 introdujo una entidad de dominio nueva (verificado: los 4 Patrones de AD-008 y las reglas de los 6 AD-CMP son comportamiento, no entidades — pasan el Principio de Emergencia explícitamente en cada documento) |
| 5 | Sin preguntas abiertas que bloqueen el paso a AD-FUNC | ✅ Verde — la única pregunta que sí bloqueaba (dependencias faltantes de AD-FUNC-01) quedó resuelta al existir AD-CMP-01 y AD-CMP-05. AD-007 se actualizó a v1.1 marcando su propia pregunta abierta (fusión/división) como resuelta por AD-CMP-06 |
| 6 | Trazabilidad completa AD-000 a AD-CMP-06 | ✅ Verde — cadena de 15 documentos sin ciclos |

**Verdict de la segunda pasada: VERDE. Se marca oficialmente:**

# WO-000 — Fase 1: COMPLETADA

15 de 24 documentos de la Fase 1 originalmente definida están, en realidad, ya completos en su totalidad — el número "24" incluye los 9 AD-FUNC, que son la categoría siguiente, no pendientes de esta fase de Fundamentos+Comportamientos. Fundamentos (9) y Comportamientos (6) — las dos categorías que debían cerrarse antes de Funcionalidades — están 100% congeladas. AD-FUNC-01 puede iniciarse cumpliendo, no violando, sus propias dependencias declaradas.
