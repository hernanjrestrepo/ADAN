# ADR-002 — Autenticación JWT propia mínima (no reutilización de auth Paradixe)

**Estado:** RATIFICADO
**Fecha:** 2026-07-17 · **Célula:** A · **WO/Sprint:** WO-001 Sprint 3

## Contexto

El Plan Maestro (WO-001 Sprint 3) pide "evaluar reutilización de auth Paradixe vía ADR-R; si no está accesible, JWT propio mínimo". Este repo (`adan-platform`) es, por decisión explícita del humano (ver conversación de arranque de la cadena), **independiente del monorepo de Paradixe** (`repos-active`), precisamente para no entrelazar el trabajo en curso de otros productos (Claro, en `feature/voice-quality`, con 63 archivos modificados y 399 sin trackear al momento de esa decisión).

## Decisión

Se implementa JWT propio mínimo (`python-jose` + `passlib[bcrypt]`) en `backend/app/auth/`. No se copia código de autenticación de EVA/JobXeeker/NOURA/TradeHub/MigPAL/VDC.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Copiar el módulo de auth de otro proyecto Paradixe vía ADR-R | Requeriría acceder al repo `repos-active` (monorepo compartido) desde este repo independiente — reintroduce exactamente el acoplamiento que la decisión de aislamiento buscaba evitar |
| Delegar autenticación a un proveedor externo (Auth0, Clerk, etc.) | Requeriría credenciales/cuenta nueva — parada dura #2, no se resuelve sin el humano |

## Impacto

JWT propio es reemplazable después por un ADR-R real si, en el futuro, el humano decide conectar este repo con el resto del ecosistema Paradixe (ej. SSO vía UC Virtual, ver contexto de otros productos del ecosistema). No bloquea nada del blueprint — AD-006 §4 (Usuario, Usuario Principal) no dicta mecanismo de autenticación, solo la entidad.

## Reversibilidad

Alta — la autenticación vive detrás de `app/auth/dependencies.py`; cambiar el proveedor no toca el resto del backend.

## Ratificación

RATIFICADO — consistente con la decisión de aislamiento de repo ya tomada, y no bloquea ninguna WO posterior.
