# AD-ROOT-0001 — Canon del Proyecto ADÁN

**Fecha de redacción:** 2026-07-31
**Estado:** ✅ VIGENTE — 2026-07-31, por Hernán (CTO ADÁN), en cumplimiento de `AD-DEC-0001 §5`.
**Actualizado:** 2026-09-24 — repositorio y rama oficiales (§1, §2), WO-094 (§4) y ubicación de las líneas (§6), por decisión de Hernán; documentación canónica (§5) y `.claude/launch.json` en WO-096. Ver historial al final.
**Deriva de:** `AD-DEC-0001` (Historia Oficial de ADÁN) — la línea oficial decidida es Build C.
**Propósito:** este es el documento que un agente o desarrollador nuevo debe leer antes de escribir una sola línea de código para ADÁN — sin tener que reconstruir la genealogía por auditoría forense, como fue necesario esta vez (Regla 1 de `AD-GOV-0001`).

---

## 1. Repositorio oficial

✅ **GitHub `hernanjrestrepo/ADAN`** — https://github.com/hernanjrestrepo/ADAN (público). Decidido el 2026-09-24: reúne en un solo repositorio Build C (raíz), Build A (`adan-platform/`, con sus 25 commits) y el prototipo 2024 (`autonomous/`, antes `hernanjrestrepo/adan_autonomous`). `hernanjrestrepo/ADAN-BACK` estaba vacío.

*Antes (2026-07-31 → 2026-09-24):* `C:\Users\herna\Documents\Paradixe\repos` (monorepo compartido, local). Ahí sigue viviendo Build B (§6).

## 2. Rama oficial

✅ **`main`** de `hernanjrestrepo/ADAN`. Todo cambio entra por una rama de trabajo y un Pull Request hacia `main`; `adan/platform-integration` sigue en rol de referencia técnica (§6).

*Antes:* se había propuesto `adan/enterprise` en el monorepo local; queda sin efecto con el cambio de repositorio de §1.

## 3. Arquitectura oficial

✅
```
FastAPI · React · TypeScript · PostgreSQL · pgvector · Ollama · Docker
Event Bus · EMS · TEF · Board · DKA · OOS · Voice
```
**Nota de consistencia (no resuelta silenciosamente):** el frontend actual de Build C está escrito en JavaScript (JSX), no TypeScript. La arquitectura oficial aquí decidida especifica TypeScript. Esto implica que la migración pendiente no es solo SQLite→PostgreSQL (explícita en `AD-DEC-0001 §5.4`) sino también una migración de JSX a TypeScript en el frontend — se deja registrado como parte del alcance en vez de asumir cuál de los dos prevalece.

## 4. Numeración oficial de Work Orders

✅ **Corregida el 2026-07-31** (ver nota de colisión abajo — el número original propuesto, WO-100, ya estaba reservado desde antes de esta sesión).

```
WO-000 → WO-009   histórico (blueprint + intentos de implementación previos)
WO-090            Consolidación Oficial de ADÁN Enterprise (congelación de Build C, ex "WO-100")
WO-091            Migración Enterprise — PostgreSQL + pgvector (ex "WO-101")
WO-092            TypeScript (ex "WO-102")
WO-093            Producción Enterprise — CI/CD, observabilidad, seguridad (ex "WO-103")
WO-094            Hotfix de seguridad — ejecución remota de código en TEF, SSRF y fugas entre
                  empresas (2026-09-24, aprobado por Hernán). Ver docs/auditoria/.
WO-095 → WO-099   Asignadas en docs/auditoria/PLAN_WO_ADAN_100.md (aprobado por Hernán, 2026-09-24).
WO-107 → WO-122   Asignadas en el mismo plan, a continuación de las reservas WO-100 → WO-106.
WO-100            RESERVADO — Business Architecture (precio por Nivel, Billing técnico,
                  Marketplace revenue share, Marco Legal/Regulatorio incl. "Ondas Expansivas"
                  e IP en disputa con el socio) — reserva preexistente en el blueprint
                  original (docs/WO-000_INDICE_MAESTRO_v2/v3/v3.21.md), NO tocada por WO-090+.
                  2026-09-24: insumos decididos en AD-DEC-0002 (no hay disputa de IP; la
                  red de comisiones es multinivel y debe cumplir la Ley 1700/2013).
WO-101 → WO-106   RESERVADO — cadena SaaS (multi-tenant, billing, administración de cuentas)
                  — reserva preexistente de CHAIN_CLOSURE.md (Build B), requiere aprobación
                  humana explícita y Plan Maestro II propio para abrirse. NO tocada por WO-090+.
```

**Nota de alcance sin resolver:** el "WO-103 Producción Enterprise" original de Hernán (ahora WO-093) incluía "multiempresa" en su alcance — eso se superpone temáticamente con la cadena SaaS ya reservada en WO-101→WO-106, que `CHAIN_CLOSURE.md` condiciona explícitamente a una aprobación separada. Este documento no resuelve ese solapamiento — lo deja marcado para que se decida cuando se llegue a WO-093, no ahora.
**Pendiente de resolución operativa (no de decisión — de mapeo):** Build C ya tiene su propia WO-001 interna (cerrada, `WO-001_CIERRE_DEFINITIVO.md`) y módulos etiquetados WO-011 a WO-020 (`test_wo011_to_wo020.py`). Falta mapear esa numeración interna existente hacia el nuevo esquema WO-100+ para que no queden dos numeraciones superpuestas dentro de la misma línea oficial — este mapeo no se resuelve solo con esta decisión, requiere trabajo de catalogación adicional.

**Actualización 2026-09-24 sobre WO-090:** el código de Build C quedó versionado por primera vez (commit `abc6b6c`, hecho por Hernán desde la laptop) y publicado en `main` de `hernanjrestrepo/ADAN`. Siguen pendientes el tag de baseline y la revisión humana previa al cierre (EPWO-053). WO-090 no se declara cerrada aquí: su cierre lo decide Hernán.

**WO-090 — Consolidación Oficial de ADÁN Enterprise: ABIERTA el 2026-07-31** (renumerada de "WO-100" tras detectar colisión con la reserva preexistente de Business Architecture — ver nota arriba), autorizada por Hernán (CTO). Alcance: congelar Build C como baseline oficial, catalogar WOs existentes y mapearlas a este esquema, generar inventario técnico y `BASELINE_ENTERPRISE_v1.md`. Explícitamente prohibido en su alcance: agregar features, refactorizar masivamente, migrar de base de datos, cambiar de lenguaje, modificar la arquitectura funcional. Ningún commit de congelación (rama/tag) se ejecuta hasta que los 4 entregables de WO-090 estén revisados y aprobados. Ver `REPORTE_CONSOLIDACION_WO090.md` para el resultado.

## 5. Documentación canónica

✅
- `docs/wo-000/*`: el blueprint. Era idéntico en las tres líneas. Desde WO-096 (2026-09-24) incluye las versiones más nuevas, que antes solo estaban en Build A (AD-003 v1.2, AD-006 v1.2, AD-FUNC-07/08/09 y `kg.json`), además de AD-000 v2.0 (según AD-DEC-0002) y el mapa de lectura `BLUEPRINT_ADAN_v1.1.md`.
- `AD-DEC-0001`, `AD-DEC-0002` (modelo de negocio y ecosistema, 2026-09-24), `AD-ROOT-0001` (este documento), `AD-GOV-0001` — canónicos de gobierno.
- `ADAN_MASTER_ARCHITECTURE_v1.0.md` (Build C) — **reclasificado**: deja de ser "Single Source of Truth" autodeclarada y pasa a ser documentación de arquitectura subordinada a este Canon. Esta misma sección cumple la función de la nueva Regla 6 de `AD-GOV-0001`: revoca explícitamente esa autodeclaración. *(WO-096: el documento ya lo dice en su propio texto.)*
- `CHAIN_CLOSURE.md` (Build B) — permanece como documento de cierre histórico de la línea experimental, con valor de referencia técnica.

## 6. Estado de las líneas no elegidas

✅
- **Build A** (`adan-platform/`) → **Archivo histórico.** Sin más desarrollo. Desde el 2026-09-24 vive en `adan-platform/` de este repositorio, con su historial completo. Su `docs/blueprint/` tenía la versión más completa del blueprint (AD-003 v1.2, AD-006 v1.2, AD-FUNC-07/08/09); desde WO-096 esas versiones están también en `docs/wo-000/`. Lo que se puede reutilizar de su código está en `docs/wo/WO-096_MAPA_REUTILIZACION.md`.
- **Build B** (rama `adan/platform-integration`) → **Referencia técnica.** Se preserva como repositorio de reutilización (PostgreSQL, pgvector, arquitectura enterprise, implementaciones ya probadas). No compite con Build C ni recibe desarrollo bajo el rol de línea oficial. *Pendiente (aprobado 2026-09-24):* importarlo a este repositorio desde el monorepo local, solo la carpeta de ADÁN y con su historial.
- **Prototipo 2024** (`autonomous/`) → **Histórico.** Lambda de AWS que se clona a sí misma y pipeline CodePipeline/CodeBuild; sin relación de código con A, B o C.

---

## Nota sobre `adan-integration/` (worktree)

Independientemente de la decisión anterior: el worktree registrado en `C:\Users\herna\Documents\Paradixe\adan-integration` (rama `adan/platform-integration`) y el archivo `.claude/launch.json` de esta sesión ya apuntan a Build B como el entorno de ejecución activo. *(2026-09-24, WO-096: `.claude/launch.json` ya apunta a Build C, con rutas relativas a la raíz de este repositorio: backend en `:8020` y frontend en `:5173`.)* Si la decisión de la sección 1-2 cambia el repositorio o rama oficial, este archivo de configuración debe actualizarse en consecuencia — no queda automáticamente sincronizado con lo que este documento declare.

---

## Historial de cambios

| Fecha | Cambio | Decidido por |
|---|---|---|
| 2026-07-31 | Creación: Build C como línea oficial, numeración WO-090+, documentación canónica | Hernán (CTO) |
| 2026-09-24 | §1 repositorio oficial → GitHub `hernanjrestrepo/ADAN`; §2 rama oficial → `main`; §4 WO-094 y rangos WO-095→099 y WO-107→122; insumos de WO-100 (AD-DEC-0002); §6 ubicación de Build A, Build B pendiente y prototipo 2024 | Hernán (CTO) |
| 2026-09-24 | WO-096: §5 `docs/wo-000/` con las versiones más nuevas del blueprint y AD-000 v2.0; `ADAN_MASTER_ARCHITECTURE` marcado en su propio texto; §6 mapa de reutilización; nota de `.claude/launch.json` resuelta | Ejecutado por Claude Code con la autorización general de Hernán (2026-09-24) |
