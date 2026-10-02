# WO-091 — Migración Enterprise: PostgreSQL + pgvector · Reporte de cierre

**Formato:** EPWO-050 · **Checklist:** EPWO-051 · **Fecha:** 2026-10-01
**Estado:** ✅ **CERRADA**
**Commits:** `b6e38d1` (migración), `11e78f8` (tests herméticos), `25eb5e7` (los tests crean el esquema con las migraciones)
**Decisiones de arquitectura:** `AD-DEC-0002 §D6`

---

## 1. Resultado

ADÁN corre sobre **PostgreSQL 16 + pgvector**, y SQLite se mantiene para desarrollo y tests. El esquema lo gestiona Alembic, con una sola base declarativa. La memoria vectorial del EMS es persistente y la comparten todos los módulos.

| Antes (WO-090) | Después |
|---|---|
| SQLite como único motor | PostgreSQL + pgvector (producción) o SQLite (desarrollo), según `DATABASE_URL` |
| 3 bases declarativas (`Base`, `EMSBase`, `OOSBase`) | 1 (`Base`); las otras dos quedan como alias |
| `create_all` al arrancar, sin migraciones | Alembic: `0001` baseline + `0002` `ems_embeddings`; adopción automática de bases antiguas |
| Vector store **en memoria, uno por router** (EMS, agentes, Board, DKA no compartían conocimiento y todo se perdía al reiniciar) | Tabla `ems_embeddings` compartida; distancia coseno de pgvector (`<=>`) en PostgreSQL |
| Sin camino para los datos existentes | `scripts/migrate_sqlite_to_postgres.py` |

## 2. Evidencias (ejecución real, no inspección)

| Evidencia | Resultado |
|---|---|
| Suite completa contra PostgreSQL 16.x + pgvector 0.6 | **260/260** |
| Suite completa contra SQLite | **259 + 1 skip** (el skip es el test del script SQLite→PostgreSQL, que necesita PostgreSQL) |
| `alembic check` (modelos = migraciones) en ambos motores | "No new upgrade operations detected" |
| Upgrade → downgrade → upgrade en PostgreSQL | Limpio, incluida la eliminación de los tipos ENUM |
| Adopción de una BD SQLite antigua con datos | Test `test_legacy_sqlite_database_is_adopted`: los datos se conservan y queda en `0002` |
| Conocimiento compartido entre módulos | Test `test_knowledge_is_shared_across_ems_instances` |
| App real sobre PostgreSQL | Registro → empresa → ingesta EMS → recuperación semántica → estrés concurrente: OK |
| Stack Docker de producción | `ems_embeddings` en pgvector y `alembic_version = 0002` dentro del contenedor de PostgreSQL |

## 3. Hallazgos (EPWO-009)

**Bloqueantes resueltos dentro de la WO:**
1. `oos_work_orders.decision_id` es una FK y los tests insertaban IDs inventados. En SQLite pasaba porque ese fixture no activaba las FKs; en PostgreSQL fallaba. La app sí usaba IDs reales. Corregido en los tests.
2. Un error de ingesta dejaba la transacción abortada en PostgreSQL. Ahora se hace `rollback`.
3. `SqlQueryTool` nunca había funcionado con SQLAlchemy 2 (faltaba `text()`). Corregido en WO-090.

## 4. Deuda técnica registrada

- **D-1 Sin índice ANN.** La columna `vector` no tiene dimensión fija, para poder cambiar de proveedor de embeddings, y por eso no admite HNSW/IVFFlat. La búsqueda es exacta. Basta mientras cada empresa tenga hasta unas decenas de miles de chunks. Cuando se fije el modelo de embeddings de producción, agregar una migración con un índice HNSW por expresión (`(embedding::vector(N))`).
- **D-2 Embeddings locales no semánticos.** `EMBEDDING_PROVIDER=local` (el default) es hashing. Para búsqueda semántica real hay que configurar `EMBEDDING_PROVIDER=ollama` con `nomic-embed-text`. Al cambiar de proveedor, los documentos ya ingeridos no aparecen en la búsqueda vectorial (se filtra por dimensión) hasta reingerirlos; la búsqueda por palabras clave sigue funcionando.
- **D-3** Las fechas se guardan *naive* en UTC (la sesión de PostgreSQL fija `timezone=utc`). Es consistente, pero conviene migrar a `timestamptz` en una WO futura.

## 5. Riesgos abiertos

- La migración de **los datos reales de la laptop** no se pudo ejecutar desde aquí, porque esa base no está en el repositorio. El script está probado con datos sintéticos. Pasos: `README.md` → "Migrar datos de SQLite a PostgreSQL".

## 6. Checklist EPWO-051

- [x] Evidencia objetiva
- [x] Funcionalidad implementada
- [x] Pruebas aprobadas (ambos motores, CI incluido)
- [x] Documentación actualizada (`README.md`, `.env.example`, `AD-DEC-0002`)
- [x] Commits realizados y repositorio limpio
- [x] Baseline reproducible desde el repositorio (CI con servicio PostgreSQL)
- [x] Deuda y riesgos registrados
