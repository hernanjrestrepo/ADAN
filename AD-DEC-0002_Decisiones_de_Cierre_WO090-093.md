# AD-DEC-0002 — Decisiones de cierre de WO-090 a WO-093

**Fecha:** 2026-10-01/02
**Estado:** ✅ VIGENTE, tomada por delegación. Hernán (CTO ADÁN) delegó las decisiones el 2026-10-01 con la instrucción *"hazlo todo, lo que tengas que tomar decisiones tómalas tú"*. Cada una puede revertirse con un AD-DEC posterior (Regla 6 de `AD-GOV-0001`).
**Ejecutor:** sesión de Claude Code, rama `claude/amazing-allen-ta66ry` del repositorio `hernanjrestrepo/ADAN`.
**Deriva de:** `AD-ROOT-0001` §2 y §4, `REPORTE_CONSOLIDACION_WO090.md` §6, `AD-GOV-0001` Reglas 3, 4 y 7.

Cada decisión registra **qué estado previo reemplaza** (Regla 4), **por qué** se tomó y **cómo revertirla**.

---

## Fase -1 (Regla 7), registrada antes de ejecutar

| Verificación | Resultado |
|---|---|
| Lectura de `AD-ROOT-0001`, `AD-GOV-0001`, `AD-DEC-0001` | Hecha. Línea oficial: Build C. Stack oficial: FastAPI · React · TypeScript · PostgreSQL · pgvector · Ollama · Docker |
| Repositorio, rama y último commit verificados (Regla 1) | `github.com/hernanjrestrepo/ADAN`, rama por defecto `laptop`, commit `abc6b6c` ("Código de ADAN desde la laptop") |
| Colisión de numeración (Regla 2) | WO-091/092/093 ya estaban reservadas en `AD-ROOT-0001 §4` para exactamente estos temas. Sin colisión. No se creó ningún número nuevo |
| Reutilización (EPWO-022) | Se reutilizaron las interfaces existentes (`VectorStoreProvider`, `EmbeddingProvider`, `ToolProvider`, `ConnectorManager`). No se crearon módulos paralelos |
| Aprobación (EPWO-007) | Delegación explícita del 2026-10-01 (arriba) |

---

## D1 — Repositorio y rama oficiales (cierra `AD-ROOT-0001 §1-2`)

**Decisión:** el repositorio oficial es **`github.com/hernanjrestrepo/ADAN`** (monorepo: `backend/`, `frontend/`, `docs/`, documentos de gobierno en la raíz). La rama oficial es **`laptop`**, la rama por defecto del repositorio.
**Reemplaza:** la ruta local `C:\Users\herna\Documents\Paradixe\repos` como "repositorio oficial" y el nombre propuesto `adan/enterprise`.
**Por qué:** la Regla 5 exige que el conocimiento no viva solo en un disco local. El repositorio en GitHub ya existe, ya es el remoto de la carpeta de la laptop y ya tiene `laptop` como rama por defecto. Crear `adan/enterprise` ahora agregaría una cuarta ubicación posible del "código oficial", que es justo el patrón que originó las tres líneas (`AD-DEC-0001 §6`).
**Recomendación no bloqueante:** renombrar `laptop` a `main` desde GitHub (Settings → Branches). GitHub redirige el nombre viejo, así que no rompe clones existentes. No se hizo desde esta sesión porque cambiar la rama por defecto es una acción de administración del repositorio.
**Revertir:** AD-DEC que nombre otra rama u otro repositorio.

## D2 — Usuario de verificación `wo090-verify@example.com` (cierra `REPORTE_CONSOLIDACION_WO090 §3.9`)

**Decisión:** **archivarlo, no borrarlo.** Comando, a correr en la laptop desde `backend/`:
```
python -m scripts.archive_user wo090-verify@example.com
```
**Por qué:** el Contrato Base del modelo (AD-006 §2, citado en `app/models/models.py`) dice que las entidades se archivan y nunca se eliminan. Desde WO-093 un usuario archivado no puede iniciar sesión ni usar tokens emitidos antes, así que deja de ser una cuenta utilizable sin perder la evidencia de la verificación de WO-090. El usuario vive en la base SQLite de la laptop, que no está versionada (`*.db` en `.gitignore`), por eso queda como comando a ejecutar y no como cambio en el repositorio.
**Revertir:** `python -m scripts.archive_user wo090-verify@example.com --restore`.

## D3 — Estados EPWO-029 de las tres líneas (cierra `REPORTE_CONSOLIDACION_WO090 §3.10`)

| Línea | Terminología de `AD-DEC-0001` | Estado EPWO-029 |
|---|---|---|
| Build A (`adan-platform/`) | Archivo histórico | **Deprecado** |
| Build B (`adan/platform-integration`) | Referencia técnica | **Deprecado** (consultable como referencia, sin desarrollo) |
| Build C (este repositorio) | Línea oficial | **Piloto** |

**Por qué "Piloto" y no "Producción":** desde WO-093 el código cumple los requisitos técnicos de producción (CI, seguridad, despliegue reproducible, observabilidad). Pero no hay evidencia de que esté desplegado con clientes reales, y declarar "Producción" sin esa evidencia repetiría el patrón de autodeclaraciones que `AD-DEC-0001` documentó. Pasa a **Producción** con el primer despliegue real en `docker-compose.prod.yml` con usuarios reales, registrado en un AD-DEC.

## D4 — "Multiempresa" en WO-093 vs. cadena SaaS WO-101→106 (cierra la nota de `AD-ROOT-0001 §4`)

**Decisión:** WO-093 cubrió **aislamiento entre clientes** dentro del modelo existente: cada `Company` pertenece a su `primary_user` y ningún usuario puede leer ni escribir datos de otra empresa. Se corrigieron dos fugas reales (OOS e integraciones, ver `docs/WO-093_REPORTE_CIERRE.md`). **No** cubrió multi-tenant SaaS (varias personas por organización, roles por organización, billing, administración de cuentas). Eso sigue reservado a WO-101→106 y requiere aprobación humana separada y Plan Maestro II, como exige `CHAIN_CLOSURE.md`.
**Por qué:** el aislamiento es un requisito de seguridad sin el cual ningún despliegue con más de un cliente es aceptable, así que pertenece a "Producción Enterprise". El multi-tenant es una decisión de producto y de negocio (precio, billing, WO-100), no técnica.

## D5 — Hueco WO-013→WO-015 de Build C (cierra `CATALOGO_WORK_ORDERS §6.2`)

**Decisión:** se declaran **números no usados, permanentemente**. No se reasignan.
**Por qué:** la Regla 2 prohíbe reutilizar numeración. Reasignarlos hoy crearía exactamente la ambigüedad que la regla busca evitar, porque cualquier referencia futura a "WO-014" sería dudosa.

## D6 — Decisiones de arquitectura de WO-091 (ADR exigido por la Regla 3)

Reemplaza: SQLite como único motor de Build C, tres bases declarativas (`Base`, `EMSBase`, `OOSBase`) y un vector store en memoria por router.

1. **PostgreSQL 16 + pgvector como motor oficial; SQLite se conserva para desarrollo local y tests.** `DATABASE_URL` decide. La suite completa corre en ambos motores (CI incluido), así que SQLite no puede divergir sin que se note.
2. **Una sola base declarativa.** `EMSBase` y `OOSBase` quedan como alias de `Base` para no romper imports.
3. **Alembic como única fuente del esquema.** Baseline `0001` = esquema congelado de WO-090. Una base SQLite antigua (como la de la laptop) se *adopta* automáticamente con `stamp` sin tocar sus datos. Las migraciones se serializan con un advisory lock de PostgreSQL.
4. **Vector store en la base de datos** (tabla `ems_embeddings`), compartido por EMS, agentes, Board y DKA. Antes cada router tenía su propio store en memoria: lo ingerido por un módulo era invisible para los demás y se perdía al reiniciar. Columna `vector` **sin dimensión fija**, con la dimensión guardada por fila, para poder cambiar de proveedor de embeddings sin migrar. Costo aceptado: sin índice ANN, la búsqueda es exacta. Ver deuda D-1 en `docs/WO-091_REPORTE_CIERRE.md`.
5. **Datos existentes:** `backend/scripts/migrate_sqlite_to_postgres.py` copia una base SQLite completa a PostgreSQL.

## D7 — Decisiones de arquitectura de WO-092 (frontend)

Reemplaza: JavaScript/JSX, Vite 5 y React Router 6 con vulnerabilidades conocidas.

- **TypeScript 5.9 estricto** (`strict` + `noUncheckedIndexedAccess`). TS 7 (el compilador nativo nuevo) se descartó por ahora: es más riesgoso y no aporta nada a un frontend de este tamaño.
- **React 18 se mantiene.** Pasar a React 19 no era necesario para eliminar vulnerabilidades y sí arriesgaba regresiones. **React Router 7.18.4** (paquete `react-router`) es la última versión compatible con React 18 y está parcheada. **Vite 8** y **Node 22**.
- **Contrato tipado con el backend** en `src/lib/types.ts`. Al tiparlo apareció un bug real: el Board Room nunca mostraba resultados porque esperaba un campo (`board_results`) que el backend no envía.

## D8 — Decisiones de seguridad y operación de WO-093

- `python-jose` → **PyJWT** y `passlib` → **bcrypt directo** (ambas librerías anteriores tienen CVEs o están sin mantenimiento). Los hashes existentes siguen verificando; está probado con hashes generados por passlib.
- **`TEF_ENABLE_PYTHON_SANDBOX=false` por defecto.** La herramienta ejecutaba código arbitrario con los permisos del backend; no era un sandbox. Activarla exige un entorno aislado.
- **`ALLOW_PRIVATE_HTTP=false` por defecto.** TEF, DKA e integraciones no pueden llamar a la red interna (protección SSRF, incluidas las redirecciones).
- **`ENVIRONMENT=production` falla al arrancar** si `JWT_SECRET` es el de desarrollo o tiene menos de 32 caracteres, si la base es SQLite o si `CORS_ORIGINS` es `*`. Fallar al arrancar es preferible a correr inseguro.
- **Versión 1.0.0** de ADÁN Enterprise (backend), en estado **Piloto** (D3).

---

## Evidencia

Commits sobre `abc6b6c`, en orden:

| Commit | Contenido |
|---|---|
| `c4b7826` | WO-090: hallazgos técnicos (tests asyncio, TEF, dependencias de test) |
| `b6e38d1` | WO-091: PostgreSQL + pgvector |
| `11e78f8` | Tests herméticos, SSRF compartido, cobertura |
| `bfa1595` | WO-092: TypeScript |
| `25eb5e7` | WO-093 (1/2): seguridad y observabilidad |
| `8e483a7` | WO-093 (2/2): despliegue de producción y CI/CD |

Reportes de cierre: `REPORTE_CONSOLIDACION_WO090.md` §9-§10, `docs/WO-091_REPORTE_CIERRE.md`, `docs/WO-092_REPORTE_CIERRE.md`, `docs/WO-093_REPORTE_CIERRE.md`.
