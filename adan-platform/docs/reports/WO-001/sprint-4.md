# WO-001 Sprint 4 — Modelo de entidades núcleo

**Célula:** A · **Fecha:** 2026-07-17

## Resumen ejecutivo

Traducción completa de AD-005 (26 entidades de negocio) y AD-006 §4 (12 entidades operativas, modeladas como 11 tablas — "Usuario Principal" es una relación 1:N en `Proyecto.usuario_principal_id`, no una tabla separada, documentado en `usuario.py`/`proyecto.py`) a modelos SQLAlchemy 2.0, con Contrato Base (AD-006 §2) como mixin compartido. Migración inicial de Alembic generada por autogenerate y aplicada contra PostgreSQL real. Seed de datos demo ejecutado end-to-end.

## Archivos creados

`app/models/mixins.py`, `empresa.py`, `organizacion.py`, `comercial.py`, `operacion.py`, `direccion.py`, `finanzas.py`, `proyecto.py`, `nivel.py`, `conversacion.py`, `decision_score_evento.py` (37 clases ORM en total), `migrations/versions/f8d91060004d_*.py`, `scripts/seed_demo.py`, `tests/test_entities_functional.py`.

## Archivos modificados

`app/models/__init__.py` (importa las 37 clases para que el registro de mapeo de SQLAlchemy resuelva relaciones y Alembic vea el metadata completo), `app/models/usuario.py` (se retiró el flag `is_principal` — el rol de "Usuario Principal"/"Responsable de Empresa" se modela correctamente como relación 1:N vía `Proyecto.usuario_principal_id`), `migrations/env.py` (apunta a `Settings.database_url` real, no a un placeholder), `pyproject.toml` (bcrypt fijado a 4.0.1 — incompatibilidad real con passlib 1.7.4 en bcrypt≥4.1).

## Bugs encontrados

- `passlib[bcrypt]` + `bcrypt>=4.1` rompe en runtime real (`AttributeError: module 'bcrypt' has no attribute '__about__'`) al primer hash de contraseña — no se detecta con solo lectura de código, solo ejecutando.
- Referencias cruzadas de tipo (`Mapped["Proyecto"]` en `nivel.py`, `Mapped["Nivel"]` en `proyecto.py`) generaban `F821` en ruff sin imports `TYPE_CHECKING`.
- Primera versión de los tests funcionales usaba `commit()` en vez de `flush()`, dejando residuo real en Postgres entre corridas — violaba la disciplina de "reutilizar evidencia sin ensuciar el entorno".

## Bugs corregidos

Los tres anteriores. Verificado corriendo la suite dos veces seguidas sin residuo (`SELECT count(*)` de las filas de prueba = 0 tras cada corrida).

## Evidencias objetivas

- `docker compose up -d postgres redis`: ambos contenedores `healthy` en <20s.
- `alembic revision --autogenerate`: detectó las 37 tablas reales sin intervención manual.
- `alembic upgrade head`: aplicado contra Postgres real — `\dt` confirma 37 tablas + `alembic_version`.
- `scripts/seed_demo.py`: ejecutado contra la BD real, Empresa/Proyecto/Usuario/Nivel verificables por `SELECT` directo.
- `pytest`: **5 passed** (3 unitarios + 2 funcionales contra Postgres real), corrido dos veces consecutivas sin duplicados ni residuo.
- `ruff check .`: **All checks passed!**

## Tiempo real (Wall Clock)

~55 minutos (incluye 2 rondas de debugging real: bcrypt y aislamiento de tests).

## Estado del Sprint

COMPLETO
