# AD-GOV-0001 — Reglas de Desarrollo

**Fecha de redacción:** 2026-07-31
**Estado:** Propuesta — no requiere decidir entre Build A/B/C para entrar en vigor, pero sí requiere aprobación de Hernán para ser obligatoria.
**Depende de:** nada — a diferencia de `AD-ROOT-0001`, estas reglas son de proceso, no de arquitectura, y no necesitan esperar a `AD-DEC-0001 §5`.
**Origen:** cada regla de este documento corresponde a un fallo real y verificado, encontrado durante la reconstrucción genealógica de ADÁN (ver `AD-DEC-0001`), no a buenas prácticas genéricas.

---

## Cómo leer este documento

Cada regla incluye el incidente concreto que la motiva. Si una regla no tiene un incidente real citado, no debería estar en este documento — se agregaría fricción sin evidencia de que resuelve algo.

---

## Regla 1 — Ningún agente puede iniciar una Work Order sin leer primero el documento Canon vigente

**Incidente que la motiva:** `ADR-001-Vertical-Nivel-1.md` (Build C, 2026-07-23) afirma *"ADÁN tiene... cero código"* cuando Build B ya tenía 51 commits y una cadena completa cerrada (`v1.0.0`, tres días antes). Quien escribió ese documento no consultó, o no encontró, el estado real del proyecto.

**Regla:** antes de abrir cualquier Work Order nueva, el agente o desarrollador debe leer `AD-ROOT-0001` (cuando exista) y confirmar en su propio reporte de apertura qué repositorio, rama y último commit relevante verificó. Si no puede verificarlo, debe decirlo explícitamente en vez de asumir un estado.

## Regla 2 — Ningún agente puede reutilizar una numeración de Work Order ya existente

**Incidente que la motiva:** "WO-012" significa *Producción/Baseline* en Build B y *Omnichannel* en Build C — dos numeraciones independientes que colisionan en el mismo número sin relación entre sí, generando ambigüedad permanente en cualquier referencia futura a "WO-012".

**Regla:** la numeración de Work Orders es un espacio único y acumulativo por proyecto, no por rama ni por repositorio. Antes de asignar un número de WO, se debe verificar cuál es el último número usado en el Canon vigente (`AD-ROOT-0001`), no solo en la rama o carpeta donde se está trabajando.

## Regla 3 — Ningún agente puede crear una arquitectura o stack tecnológico paralelo sin una decisión explícita registrada

**Incidente que la motiva:** Build C reemplazó PostgreSQL+pgvector por SQLite, y TypeScript por JavaScript, sin ningún documento que compare esa decisión contra la arquitectura ya certificada de Build B ni que la justifique en relación a ella.

**Regla:** un cambio de stack de datos, lenguaje o arquitectura base respecto al Canon vigente requiere un ADR que cite explícitamente qué reemplaza y por qué — no basta con un ADR que describa la nueva arquitectura de forma aislada, como si no existiera nada previo.

## Regla 4 — Toda decisión arquitectónica relevante debe generar un ADR o un AD-DEC, y debe enlazar al estado previo que modifica o reemplaza

**Incidente que la motiva:** ninguno de los documentos de Build C (`ADR-001`, `ADAN_MASTER_ARCHITECTURE_v1.0.md`) menciona a Build A, Build B, la rama `adan/platform-integration` ni `CHAIN_CLOSURE.md` — ni para continuarlos ni para descartarlos explícitamente. La ausencia de esa mención es, en sí misma, lo que hizo imposible reconstruir la relación entre los Builds sin una auditoría forense completa de git.

**Regla:** un ADR o AD-DEC que introduce una decisión arquitectónica nueva debe declarar explícitamente si reemplaza, extiende, ignora deliberadamente o desconoce el estado anterior. "Desconoce" es una respuesta válida — pero debe quedar escrita, no inferida después por auditoría.

## Regla 5 — El conocimiento del proyecto no puede vivir solo en memoria de conversación o en un repositorio aislado

**Incidente que la motiva:** la migración real de Build A a Build B quedó perfectamente documentada porque coincidieron, en la misma sesión, la memoria de conversación, el mensaje de commit y la intención de Hernán. Build C ocurrió sin que ninguno de esos tres elementos coincidiera con el estado de Build B — bastó con que uno de los canales de conocimiento (memoria, commit, o visibilidad de la rama) no estuviera disponible para que apareciera una bifurcación nueva.

**Regla:** ningún repositorio de trabajo activo de ADÁN debe permanecer como repo independiente sin remote, ni como directorio sin versionar por más de una sesión de trabajo. El Canon (`AD-ROOT-0001`) es la única fuente que un agente nuevo debe necesitar consultar — no la memoria de una conversación anterior que podría no estar disponible.

## Regla 6 — Ningún agente puede declarar una nueva "Single Source of Truth" sin revocar explícitamente la anterior mediante un AD-DEC aprobado

**Incidente que la motiva:** `ADAN_MASTER_ARCHITECTURE_v1.0.md` (Build C, 2026-07-24) se autodeclaró *"Single Source of Truth"* sin dejar constancia formal de qué sustituía ni de que existiera un `CHAIN_CLOSURE.md` ya cerrado en Build B. Esa autodeclaración sin revocación explícita fue parte central de la confusión que motivó toda esta auditoría.

**Regla:** ningún documento puede autodeclararse fuente única de verdad. Solo un AD-DEC aprobado puede otorgar ese estatus, y debe hacerlo revocando explícitamente cualquier documento o línea que ocupara ese rol antes. `AD-ROOT-0001 §5` es el primer caso de aplicación de esta regla: revoca formalmente el estatus autodeclarado de `ADAN_MASTER_ARCHITECTURE_v1.0.md`.

*(Regla añadida el 2026-07-31, a solicitud explícita de Hernán.)*

## Regla 7 — Ninguna Work Order puede iniciar su Sprint 1 sin completar una Fase -1 de verificación previa

**Incidente que la motiva:** al ejecutar el Sprint 2 de WO-090 (esta misma sesión), se descubrió que el número "WO-100" ya estaba reservado en el blueprint original para *Business Architecture* — una colisión idéntica en naturaleza a la que motivó la Regla 2, ocurrida dentro de la sesión donde esa regla se escribió. La causa fue no verificar la numeración existente *antes* de empezar a trabajar, solo durante.

**Regla:** toda Work Order de ADÁN debe completar, antes de iniciar su Sprint 1, una **Fase -1 (Pre-WO)** que no produce código ni documentos de producto, solo verifica que la ejecución puede empezar sin violar EPWO v3.1 ni este Canon:

1. Lectura de `AD-ROOT-0001`, `AD-GOV-0001` y `AD-DEC-0001` completos (Regla 1).
2. Auditoría de reutilización de módulos/servicios existentes (EPWO-022).
3. Confirmación explícita del alcance congelado de la WO (EPWO-008).
4. Verificación de que el número de WO propuesto no colisiona con ninguna numeración ya usada o reservada (Regla 2, EPWO-011).
5. Identificación del camino crítico de la WO (EPWO-011).
6. Confirmación registrada de que la WO fue aprobada explícitamente antes de iniciar (EPWO-007).

Solo si la Fase -1 termina sin hallazgos bloqueantes se autoriza el inicio del Sprint 1. Si hay un hallazgo bloqueante (como la colisión de WO-100), se resuelve *antes* de continuar, no en paralelo.

*(Regla añadida el 2026-07-31, a solicitud explícita de Hernán, en el mismo día en que la ausencia de esta regla causó el incidente que la motiva.)*

---

## Relación con EPWO v3.1

Este documento no sustituye a `EPWO_v3.1.md` (estándar oficial de Paradixe para toda Work Order, en cualquier proyecto) — lo **implementa** para el caso específico de ADÁN. Donde una regla de aquí y una de EPWO se refieran al mismo problema, EPWO es la autoridad; las reglas de este documento son más específicas (nacen de incidentes reales de ADÁN) pero nunca lo contradicen. Referencia cruzada directa: Regla 1 ↔ EPWO-007; Regla 2 ↔ EPWO-011; Regla 6 ↔ EPWO-028/029; Regla 7 ↔ EPWO-007/008-010/011/022.

---

## Alcance de este documento

Estas reglas son de proceso. No determinan cuál de las tres líneas (A, B o C) es la oficial — esa decisión vive en `AD-DEC-0001 §5`. Estas reglas aplican **a partir del momento en que se apruebe este documento**, hacia adelante; no se aplican retroactivamente a lo ya ocurrido, que es precisamente lo que documenta `AD-DEC-0001`.
