# WO-000 — Índice Maestro de Especificación de Producto ADÁN (v3.1)

**Tipo de documento:** Árbol documental — **APROBADO**. Congelado salvo inconsistencia arquitectónica de alto impacto durante la redacción.
**Estado de la WO-000:** Cerrada la fase de diseño del árbol. Entra en fase de construcción de contenido, empezando por AD-000.
**Supersede a:** `WO-000_INDICE_MAESTRO_v3.md` (retirado, no eliminado — cadena de evidencia: v1 → v2 → v3 → v3.1).
**Naturaleza de este cambio:** editorial, no estructural. Ningún documento se agregó, quitó o movió de categoría respecto a v3. Ver sección 0.

---

## 0. Qué cambió respecto a v3 (changelog)

Cambio menor (v3 → v3.1), por eso el número de versión sube en el segundo dígito y no en el primero — la propia disciplina de versionado que se fija en la sección 3 aplica desde ya a este archivo.

1. **Renombrado `AD-005`:** de "Business Domain" a **"Enterprise Domain Model"**. Motivo: "Business Domain" sonaba a dominio técnico (como si fuera un bounded context de software); el documento en realidad modela conocimiento empresarial (qué es una Empresa, un Activo, un Mercado), no una capa de la aplicación. Solo cambia el nombre — objetivo, alcance, código y dependencias quedan idénticos a v3.
2. **Se agregaron 4 estándares editoriales obligatorios para los 58 documentos**, sección 1: regla de no duplicación, estructura de cierre obligatoria (7 secciones), indicador de Confidence Level, y registro obligatorio de justificación/alternativas para toda decisión de arquitectura o producto.
3. **Se agregó la disciplina de versionado** (sección 3, nueva): documentos aprobados se congelan; toda mejora crea una versión nueva con Change Log propio. Este archivo es la primera aplicación de esa regla.

Todo lo demás —58 documentos, categorías, dependencias, secuenciación, totales— es idéntico a v3 y no se reproduce dos veces en el cuerpo de este documento salvo donde el nombre cambió, en cumplimiento de la regla de no duplicación que este mismo archivo introduce.

---

## 1. Estándares Editoriales Obligatorios (aplican a los 58 documentos, sin excepción)

**Prueba de Reconstrucción (heredada de v3, sin cambios).** Todo documento debe redactarse pensando en una sola pregunta: *si el código de ADÁN desaparece esta noche, ¿un equipo de ingeniería distinto podría reconstruir el sistema completo leyendo solo estos documentos, sin reinterpretar ni inventar nada?* Si la respuesta es no, el documento está incompleto. Queda promovida de criterio de esta WO a norma editorial de Paradixe — ver sección 4.

**Regla de no duplicación (nueva).** Ningún documento repite información ya definida en otro. Cuando un concepto, entidad, regla o cifra ya existe en otro documento, se referencia por código (ej. *"ver AD-006, entidad Decisión"*), nunca se copia ni se reformula. Motivo: una sola fuente de verdad por concepto — si se duplica, en la primera actualización futura los duplicados divergen y nadie sabe cuál es el correcto. Excepción explícita: este índice maestro, cuyo propósito es ser el único punto de consulta consolidado del árbol completo, no está sujeto a esta regla frente a los documentos que resume.

**Estructura de cierre obligatoria (nueva).** Todo documento de la WO-000 termina, en este orden, con estas siete secciones:
1. Dependencias
2. Documentos relacionados
3. Impacto sobre otros módulos
4. Riesgos
5. Preguntas abiertas
6. Decisiones pendientes
7. Historial de cambios

**Confidence Level (nueva).** Todo documento declara en su encabezado un nivel de confianza de 0-100%, según cuánto de su contenido está respaldado por evidencia (Chat 1.docx, Blueprint v1, validación real) frente a cuánto es hipótesis o propuesta pendiente de aprobación del Board. No es una nota de calidad de redacción — es una nota de certeza de la información.

**Registro de decisiones (nueva).** Toda decisión de arquitectura o de producto que se tome *dentro* de un documento —no solo el objeto `Decisión` operativo definido en AD-006— debe registrar: Justificación · Alternativas evaluadas · Motivo por el cual cada alternativa fue descartada.

**Regla de entidades (heredada de v3, sin cambios):** ningún documento fuera de AD-005/AD-006/AD-007 puede introducir una entidad nueva.

---

## 2. Índice de categorías (sin cambios de contenido respecto a v3 — solo referencia)

El detalle completo de los 58 documentos (Objetivo, Alcance, Dependencias, Prioridad, Estado, Responsable, Páginas, Complejidad) queda en `WO-000_INDICE_MAESTRO_v3.md`, retirado pero vigente como fuente de las tablas — no se reproducen aquí para no violar la regla de no duplicación que este archivo introduce en la sección 1. Único cambio de contenido real: la fila `AD-005` de la categoría **Fundamentos del Ecosistema y del Producto** cambia su columna Nombre de *"Business Domain"* a **"Enterprise Domain Model"**; su Objetivo, Alcance y Dependencias no cambian.

| Categoría | Rango de códigos | Docs |
|---|---|---|
| Fundamentos del Ecosistema y del Producto | AD-000 a AD-008 | 9 |
| Comportamientos | AD-CMP-01 a AD-CMP-06 | 6 |
| Funcionalidades | AD-FUNC-01 a AD-FUNC-09 | 9 |
| UX/UI | AD-UX-01 a AD-UX-12 | 12 |
| Arquitectura | AD-ARQ-01 a AD-ARQ-10 | 10 |
| Inteligencia Artificial | AD-IA-01 a AD-IA-04 | 4 |
| Operación | AD-OPS-01 a AD-OPS-03 | 3 |
| Platform Services | AD-PLAT-01 | 1 |
| Integraciones | AD-INT-01 a AD-INT-04 | 4 |
| **Total** | | **58** |

Backbone y secuenciación de Fase 1 / Fase 2: sin cambios respecto a v3, sección 12 de ese archivo.

---

## 3. Disciplina de Versionado (nueva, rige desde ahora para todos los documentos de la WO-000)

Un documento aprobado se congela. No se edita en el sitio. Toda mejora futura crea una versión nueva:

- **Cambio menor** (aclaración, corrección, ajuste de alcance sin romper dependencias): `v1.0 → v1.1`.
- **Cambio estructural** (nueva entidad, nueva dependencia, cambio de alcance que afecta a otros documentos): `v1.0 → v2.0`.

Cada versión trae su propio **Historial de cambios** (una de las 7 secciones de cierre obligatorias) explicando qué cambió y por qué. El archivo de la versión anterior no se borra — queda como evidencia, igual que `v1`, `v2` y `v3` de este mismo índice no se borraron al ser superados.

---

## 4. Nota de cierre

**Estado:** árbol documental aprobado. A partir de aquí, cualquier ajuste al árbol mismo requiere que aparezca una inconsistencia arquitectónica de alto impacto durante la redacción — no una preferencia de forma.

**La Constitución de Paradixe** (gobernando EVA, ARQAI, Genexis, CSI, ADÁN y futuros productos, no solo ADÁN) queda fuera de esta WO-000, tal como se decidió: es un documento paralelo, de mayor jerarquía que cualquier Ecosystem Vision de un producto individual. AD-000 (sección siguiente) se escribe sabiendo que en el futuro heredará de esa Constitución cuando exista; mientras tanto, AD-000 declara sus propios principios de ecosistema al nivel de ADÁN, sin inventar autoridad que no le corresponde sobre EVA, ARQAI, Genexis o CSI.

**Siguiente paso:** redacción de `AD-000 — Paradixe Ecosystem Vision v1.0`.
