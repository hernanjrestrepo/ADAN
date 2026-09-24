# WO-091 — Migración Enterprise: PostgreSQL + pgvector

**Fecha:** 2026-09-24 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("haz todo lo que tengas que hacer", 2026-09-24)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** ✅ Cerrada al fusionar su PR en `main`. Una parte del alcance pasó a WO-098 (§2).

---

## 1. Fase -1 (AD-GOV-0001, Regla 7)

| Verificación | Resultado |
|---|---|
| Canon | `AD-ROOT-0001` §3 fija PostgreSQL + pgvector. WO-091 está definida en el Canon desde el 2026-07-31. `main` en `84df426`. |
| Reutilización (EPWO-022) | Según `docs/wo/WO-096_MAPA_REUTILIZACION.md`: la búsqueda por coseno en pgvector, los embeddings por `/api/embed` y el servicio `pgvector/pgvector:pg16` vienen de Build A. El esquema de 37 tablas de Build A **no** se trae aquí (§2). Se reutilizaron las interfaces `EmbeddingProvider` y `VectorStoreProvider` que ya existían en Build C. |
| Inventario | 3 bases declarativas (`Base`, `EMSBase`, `OOSBase`), 32 tablas, **sin nombres de clase ni de tabla repetidos**, sin SQL crudo. Riesgos encontrados: 1) `String(n)` que SQLite no hace cumplir, con texto del LLM (títulos de Work Orders del OOS); 2) enums nativos, que en PostgreSQL obligan a `ALTER TYPE` para agregar valores. |
| Numeración | WO-091 ya estaba asignada en el Canon. |
| Camino crítico | Base única → Alembic → pgvector → migración de datos. |
| Aprobación | Hernán aprobó el plan (2026-09-24). |

## 2. Cambio de alcance

**"Las 38 entidades de AD-006 v1.2, partiendo de la migración de Build A" pasa a WO-098.** Razones:
1. Build A y Build C nombran el dominio distinto: `empresas` frente a `companies`. Unificarlo es una decisión de modelo de dominio, no de motor de base.
2. Crear 20 tablas que ningún código usa va contra la Regla de Entidades de AD-004. En WO-098 cada entidad llega con el Gemelo y las Decisiones que la usan.
3. Build B, que tiene su propio modelo, todavía no está importado (WO-096). Conviene compararlo antes de elegir.

Todo lo demás del alcance se hizo.

## 3. Qué se hizo

| Pieza | Detalle |
|---|---|
| **Una sola base declarativa** | `EMSBase` y `OOSBase` desaparecen: todo hereda de `app.core.database.Base`, con 33 tablas. `import_all_models()` registra los modelos para Alembic y las pruebas. |
| **Alembic** | `backend/alembic.ini`, `backend/migrations/` y la migración `0001` (esquema inicial). Funciona en SQLite (modo batch) y en PostgreSQL. En PostgreSQL crea la extensión `vector` y un índice **HNSW** (`vector_cosine_ops`). La app migra al arrancar (`AUTO_MIGRATE`). Una base anterior a WO-091 se adopta sin perder datos: se completan las tablas que falten y se marca como `0001`. |
| **Tipos portables** | Los enums se guardan como texto (`native_enum=False`), así que agregar un estado no exige `ALTER TYPE`. JSON pasa a **JSONB** en PostgreSQL. Las fechas se guardan en UTC en los dos motores. La URL `postgres://` o `postgresql://` se normaliza a psycopg 3. |
| **Texto que excede su columna** | Un `before_flush` recorta el texto que no cabe en `String(n)` y deja un aviso en el log, en lugar de fallar con 500. Sin esto, en PostgreSQL una acción larga del Board convertida en Work Order tumbaba la petición. `Text` no se toca. |
| **pgvector** | Tabla `ems_chunk_embeddings`: `vector(768)` en PostgreSQL, JSON en SQLite. `PgVectorStoreProvider`: vectores en la misma transacción que los chunks, búsqueda por distancia coseno filtrada por empresa, sin documentos archivados y sin mezclar vectores de modelos distintos. |
| **Embeddings reales** | `OllamaEmbeddingProvider` (`nomic-embed-text`, 768 dimensiones) valida la dimensión. `EMBEDDING_PROVIDER=ollama` o `local` (hash sin red, para pruebas). `/ems/health` informa qué proveedor e índice están activos. |
| **Aislamiento** | `/ems/stats` contaba los vectores de **todas** las empresas en `vector_store_size`. Ahora cuenta solo los de la empresa consultada. |
| **Migración de datos** | `python -m app.core.sqlite_to_postgres --from … --to …`. Crea el esquema, exige un destino vacío, copia tabla por tabla en orden de claves foráneas y recalcula los embeddings. No modifica el origen. |
| **Docker Compose** | Servicio `postgres` (`pgvector/pgvector:pg16`) con healthcheck y volumen. El backend usa PostgreSQL y embeddings de Ollama. `model-pull` descarga también `nomic-embed-text`. |
| **Pruebas en los dos motores** | `conftest.py` acepta `TEST_DATABASE_URL`. Se quitaron 9 fixtures que creaban cada una su propia base SQLite en memoria, sin claves foráneas activas, así que **toda** la suite corre en los dos motores. Con las claves foráneas activas aparecieron 2 pruebas de OOS con datos inválidos (Work Orders ligadas a decisiones inexistentes): se corrigieron los datos de la prueba, no la app. |

## 4. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Suite con SQLite | **268 passed**, 5 omitidas (requieren PostgreSQL) | `pytest`, 33 s |
| Suite con PostgreSQL 16.13 + pgvector 0.6 | **272 passed**, 1 omitida (B11, que prueba el índice en memoria de SQLite) | `TEST_DATABASE_URL=… pytest`, 37 s |
| Esquema de Alembic = modelos | Sin diferencias en los dos motores | `alembic check` y `compare_metadata`, también dentro de la suite |
| Stress con PostgreSQL | 2 passed y 0 errores en el log. El servidor arrancó sobre una base vacía y la migró solo a `0001` (34 tablas). | `tests/test_stress.py` contra `uvicorn` en `:8050` |
| Stress con SQLite | 2 passed y 0 errores; la base quedó en `0001` | Igual |
| Migración de datos reales | La base del E2E de WO-095 (1 usuario, 2 empresas, 14 niveles, 6 decisiones, 13 eventos, 9 mensajes…): **58 filas copiadas y comparadas campo por campo, 0 diferencias** | `app.core.sqlite_to_postgres` + comparación |
| E2E sobre la base migrada | Login, empresas, decisiones del Nivel 1, documentos y scores responden 200. La ingesta en dos empresas generó embeddings reales de `nomic-embed-text` (768 dimensiones). La búsqueda de una empresa solo devuelve sus propios chunks (similitud 0,76). El índice HNSW existe. | Backend en `:8061` sobre PostgreSQL + Ollama 0.34.4 |
| Docker Compose | Válido | `docker compose config` (no hay daemon de Docker en este entorno: el stack no se levantó) |
| Lint de los archivos nuevos | Sin avisos | pyflakes |

## 5. Deuda y riesgos

- **Stack Docker completo sin levantar:** este entorno no tiene daemon de Docker. Se validó la configuración y cada pieza por separado (PostgreSQL 16 + pgvector, Ollama y el backend). Levantarlo completo queda para WO-093 (CI con servicios).
- **`POSTGRES_PASSWORD` tiene un valor por defecto de desarrollo** (`adan-dev`), igual que `JWT_SECRET`. Exigir ambos fuera de desarrollo es WO-097.
- **Puerto 5432 publicado** en `docker-compose.yml`, para desarrollo. En producción no debe publicarse (WO-093).
- **Recorte de texto:** evita el error 500, pero el texto que sobra se pierde; el log registra cada recorte. Validar las longitudes en la entrada de la API (422) es WO-097.
- **Con SQLite y `EMBEDDING_PROVIDER=ollama`,** el índice en memoria recalcula todos los embeddings en el primer uso. Es aceptable en desarrollo; en producción se usa pgvector.
- **Dimensión fija de 768** (`EMBEDDING_DIM`). Cambiar de modelo de embeddings exige una migración y recalcular los vectores (`reindex_embeddings`).

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§4).
- [x] Pruebas que pasan en los dos motores.
- [x] Documentación (README, Canon §3, plan) y deuda registradas.
- [x] Cambio de alcance registrado y trasladado a WO-098 (§2).
- [x] `git status` limpio al hacer el commit.
- [x] Reporte en `docs/wo/`.
- [x] PR fusionado a `main`.
