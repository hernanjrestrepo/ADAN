# AD-ROOT-0001 — Canon del Proyecto ADÁN

**Fecha de redacción:** 2026-07-31
**Estado:** ✅ VIGENTE — 2026-07-31, por Hernán (CTO ADÁN), en cumplimiento de `AD-DEC-0001 §5`.
**Deriva de:** `AD-DEC-0001` (Historia Oficial de ADÁN) — la línea oficial decidida es Build C.
**Propósito:** este es el documento que un agente o desarrollador nuevo debe leer antes de escribir una sola línea de código para ADÁN — sin tener que reconstruir la genealogía por auditoría forense, como fue necesario esta vez (Regla 1 de `AD-GOV-0001`).

---

## 1. Repositorio oficial

✅ **`C:\Users\herna\Documents\Paradixe\repos`** (monorepo compartido).

## 2. Rama oficial

✅ Una rama **nueva**, dedicada a la continuación de Build C — explícitamente **no** se reutiliza `adan/platform-integration` (esa rama pasa a rol de referencia técnica, ver §6).
**Nombre propuesto, pendiente de confirmación:** `adan/enterprise`. No colisiona con ninguna rama existente (verificado contra la lista completa de ramas locales/remotas de esta auditoría). Este documento no crea la rama por sí mismo — queda como acción derivada a ejecutar cuando se confirme el nombre.

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
WO-100            RESERVADO — Business Architecture (precio por Nivel, Billing técnico,
                  Marketplace revenue share, Marco Legal/Regulatorio incl. "Ondas Expansivas"
                  e IP en disputa con el socio) — reserva preexistente en el blueprint
                  original (docs/WO-000_INDICE_MAESTRO_v2/v3/v3.21.md), NO tocada por WO-090+.
WO-101 → WO-106   RESERVADO — cadena SaaS (multi-tenant, billing, administración de cuentas)
                  — reserva preexistente de CHAIN_CLOSURE.md (Build B), requiere aprobación
                  humana explícita y Plan Maestro II propio para abrirse. NO tocada por WO-090+.
```

**Nota de alcance sin resolver:** el "WO-103 Producción Enterprise" original de Hernán (ahora WO-093) incluía "multiempresa" en su alcance — eso se superpone temáticamente con la cadena SaaS ya reservada en WO-101→WO-106, que `CHAIN_CLOSURE.md` condiciona explícitamente a una aprobación separada. Este documento no resuelve ese solapamiento — lo deja marcado para que se decida cuando se llegue a WO-093, no ahora.
**Pendiente de resolución operativa (no de decisión — de mapeo):** Build C ya tiene su propia WO-001 interna (cerrada, `WO-001_CIERRE_DEFINITIVO.md`) y módulos etiquetados WO-011 a WO-020 (`test_wo011_to_wo020.py`). Falta mapear esa numeración interna existente hacia el nuevo esquema WO-100+ para que no queden dos numeraciones superpuestas dentro de la misma línea oficial — este mapeo no se resuelve solo con esta decisión, requiere trabajo de catalogación adicional.

**WO-090 — Consolidación Oficial de ADÁN Enterprise: ABIERTA el 2026-07-31** (renumerada de "WO-100" tras detectar colisión con la reserva preexistente de Business Architecture — ver nota arriba), autorizada por Hernán (CTO). Alcance: congelar Build C como baseline oficial, catalogar WOs existentes y mapearlas a este esquema, generar inventario técnico y `BASELINE_ENTERPRISE_v1.md`. Explícitamente prohibido en su alcance: agregar features, refactorizar masivamente, migrar de base de datos, cambiar de lenguaje, modificar la arquitectura funcional. Ningún commit de congelación (rama/tag) se ejecuta hasta que los 4 entregables de WO-090 estén revisados y aprobados. Ver `REPORTE_CONSOLIDACION_WO090.md` para el resultado.

## 5. Documentación canónica

✅
- `docs/wo-000/*` (fuente compartida, idéntica en las tres líneas — canónica independientemente de la decisión de línea oficial).
- `AD-DEC-0001`, `AD-ROOT-0001` (este documento), `AD-GOV-0001` — canónicos de gobierno.
- `ADAN_MASTER_ARCHITECTURE_v1.0.md` (Build C) — **reclasificado**: deja de ser "Single Source of Truth" autodeclarada y pasa a ser documentación de arquitectura subordinada a este Canon. Esta misma sección cumple la función de la nueva Regla 6 de `AD-GOV-0001`: revoca explícitamente esa autodeclaración.
- `CHAIN_CLOSURE.md` (Build B) — permanece como documento de cierre histórico de la línea experimental, con valor de referencia técnica.

## 6. Estado de las líneas no elegidas

✅
- **Build A** (`adan-platform/`) → **Archivo histórico.** Sin más desarrollo.
- **Build B** (rama `adan/platform-integration`) → **Referencia técnica.** Se preserva como repositorio de reutilización (PostgreSQL, pgvector, arquitectura enterprise, implementaciones ya probadas). No compite con Build C ni recibe desarrollo bajo el rol de línea oficial.

---

## Nota sobre `adan-integration/` (worktree)

Independientemente de la decisión anterior: el worktree registrado en `C:\Users\herna\Documents\Paradixe\adan-integration` (rama `adan/platform-integration`) y el archivo `.claude/launch.json` de esta sesión ya apuntan a Build B como el entorno de ejecución activo. Si la decisión de la sección 1-2 cambia el repositorio o rama oficial, este archivo de configuración debe actualizarse en consecuencia — no queda automáticamente sincronizado con lo que este documento declare.
