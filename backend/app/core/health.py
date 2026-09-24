"""Chequeos de readiness (WO-093)."""
from __future__ import annotations

import httpx
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


def migrations_status(db: Session) -> tuple[bool, str]:
    """¿La base está en la última migración?"""
    from app.core.migrations import alembic_config

    head = ScriptDirectory.from_config(alembic_config()).get_current_head()
    current = MigrationContext.configure(db.connection()).get_current_revision()
    if current == head:
        return True, f"ok ({current})"
    return False, f"pendientes: base en {current or 'ninguna'}, código en {head}"


def readiness_checks(db: Session) -> tuple[dict, bool]:
    checks: dict[str, str] = {}
    ready = True
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
        ok, detail = migrations_status(db)
        checks["migrations"] = detail
        ready = ready and ok
    except Exception as exc:  # noqa: BLE001 — cualquier falla de la base deja al backend no listo
        checks["database"] = f"error: {type(exc).__name__}"
        ready = False

    try:
        httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2).raise_for_status()
        checks["llm"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["llm"] = f"degradado: {type(exc).__name__}"

    if settings.REDIS_URL:
        from app.core.ratelimit import limiter
        checks["redis"] = "ok" if limiter.ping() else "error"
        ready = ready and checks["redis"] == "ok"
    return checks, ready
