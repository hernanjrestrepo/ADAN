"""Un solo punto de control para todo el Gemelo Digital (WO-098).

Antes de cada flush de SQLAlchemy:

1. **Nada se borra** (AD-002 regla 1.5): borrar una entidad del Gemelo falla; se archiva.
2. **Patrón C** (Registro Permanente, AD-008): Score, Evento, Suceso Empresarial, la tabla de
   versiones y el linaje no se modifican nunca; una corrección es un registro nuevo.
3. **Patrones A, B y D**: cada cambio de estado se valida contra su máquina de estados y
   contra el actor que lo hace (AD-008 §3). Un Agente nunca aprueba ni ejecuta.
4. **Versionado** (AD-002 regla 1.7): cada creación o cambio guarda una versión completa con
   el actor y el motivo, incrementa `version` y fija `updated_by`.
5. **Eventos sistemáticos** (AD-008 §4): toda transición de A, B o D, y toda entidad de
   negocio creada o archivada, genera un Evento de dominio para el Timeline.

El actor sale de app/twin/actor.py (por defecto, ADÁN/sistema).
"""
from __future__ import annotations

import logging
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.twin.actor import Actor, current_actor, current_reason

logger = logging.getLogger(__name__)


class TwinRuleError(ValueError):
    """Un cambio viola una regla del Gemelo (patrón, permiso o inmutabilidad)."""


# Columnas que no cuentan como "cambio" de la entidad
_BOOKKEEPING = {"updated_at", "version", "updated_by", "created_by"}

# Máquinas de estado de AD-008 §2 (y AD-CMP-03 §1 para "presented")
_A = {
    "proposed": {"presented", "approved", "rejected"},
    "presented": {"approved", "rejected"},
    "approved": {"executed"},
}
_B = {
    "blocked": {"active"},
    "active": {"completed"},
}
_D = {
    "active": {"paused", "archived"},
    "paused": {"active", "archived"},
}
_TRANSITIONS = {"A": _A, "B": _B, "D": _D}

# Entidades del Patrón C que, además, guardan el historial (siempre append-only)
_APPEND_ONLY_TABLES = {"entity_versions", "twin_lineage"}


def _value(v: Any) -> Any:
    return v.value if isinstance(v, Enum) else v


def _json(v: Any) -> Any:
    v = _value(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v


def _snapshot(obj) -> dict:
    mapper = inspect(obj).mapper
    return {attr.key: _json(getattr(obj, attr.key)) for attr in mapper.column_attrs}


def _stored_values(session: Session, obj) -> dict:
    """Valores guardados en la base para un objeto persistente."""
    mapper = inspect(obj).mapper
    columns = [attr.columns[0] for attr in mapper.column_attrs]
    with session.no_autoflush:
        row = session.execute(
            mapper.local_table.select().with_only_columns(*columns)
            .where(mapper.local_table.c.id == obj.id)
        ).first()
    if row is None:
        return {}
    return {attr.key: _json(value) for attr, value in zip(mapper.column_attrs, row)}


def _pattern(obj) -> str | None:
    return getattr(type(obj), "__pattern__", None)


def _is_versioned(obj) -> bool:
    """Entidades con el Contrato Base completo: tienen `version` y `updated_by`."""
    cls = type(obj)
    return hasattr(cls, "version") and hasattr(cls, "updated_by") and _pattern(obj) != "C"


def _is_twin_business(obj) -> bool:
    """Entidades que el cliente reconoce como suyas (van al Timeline al crearse)."""
    from app.twin.models import Agent, ContratoBase, Workspace
    return isinstance(obj, ContratoBase) and not isinstance(obj, (Agent, Workspace))


def _label(obj) -> str:
    for attr in ("name", "title", "statement", "description", "source", "category"):
        value = getattr(obj, attr, None)
        if isinstance(value, str) and value:
            return value[:120]
    return ""


class _Context:
    """Resuelve empresa y proyecto de cada objeto una sola vez por flush."""

    def __init__(self, session: Session):
        self.session = session
        self._project_company: dict[str, str | None] = {}
        self._company_project: dict[str, str | None] = {}
        self._card_project: dict[str, str | None] = {}

    def _project_of_company(self, company_id: str | None) -> str | None:
        if not company_id:
            return None
        if company_id not in self._company_project:
            from app.models.models import Project
            for obj in self.session.new:
                if isinstance(obj, Project) and obj.company_id == company_id:
                    self._company_project[company_id] = obj.id
                    break
            else:
                with self.session.no_autoflush:
                    row = self.session.query(Project.id).filter(Project.company_id == company_id).first()
                self._company_project[company_id] = row[0] if row else None
        return self._company_project[company_id]

    def _company_of_project(self, project_id: str | None) -> str | None:
        if not project_id:
            return None
        if project_id not in self._project_company:
            from app.models.models import Project
            with self.session.no_autoflush:
                row = self.session.query(Project.company_id).filter(Project.id == project_id).first()
            self._project_company[project_id] = row[0] if row else None
        return self._project_company[project_id]

    def _project_of_card(self, card_id: str | None) -> str | None:
        if not card_id:
            return None
        if card_id not in self._card_project:
            from app.models.models import Card
            with self.session.no_autoflush:
                row = self.session.query(Card.project_id).filter(Card.id == card_id).first()
            self._card_project[card_id] = row[0] if row else None
        return self._card_project[card_id]

    def scope(self, obj) -> tuple[str | None, str | None]:
        """(company_id, project_id) de un objeto del Gemelo."""
        from app.models.models import Company, Conversation
        if isinstance(obj, Company):
            return obj.id, self._project_of_company(obj.id)
        company_id = getattr(obj, "company_id", None)
        project_id = getattr(obj, "project_id", None)
        if isinstance(obj, Conversation):
            project_id = self._project_of_card(obj.card_id)
        if company_id is None and project_id is not None:
            company_id = self._company_of_project(project_id)
        if project_id is None and company_id is not None:
            project_id = self._project_of_company(company_id)
        return company_id, project_id


def _check_transition(obj, pattern: str, old: str, new: str, actor: Actor) -> None:
    entity = type(obj).__name__
    allowed = _TRANSITIONS[pattern].get(old, set())
    if new not in allowed:
        raise TwinRuleError(f"{entity}: transición no permitida {old} → {new} (Patrón {pattern}, AD-008)")

    if pattern == "A" and new in ("approved", "rejected", "executed") and actor.kind != "user":
        # AD-008 §3: ni un Agente ni ADÁN aprueban, rechazan o ejecutan; solo el cliente
        raise TwinRuleError(
            f"{entity}: solo el Usuario Principal puede pasar a '{new}' (actor: {actor}, AD-008 §3)"
        )
    if pattern == "B" and actor.kind == "agent":
        from app.twin.models import LevelTask
        from app.models.models import Card
        if not (isinstance(obj, (Card, LevelTask)) and old == "active" and new == "completed"):
            raise TwinRuleError(f"{entity}: un Agente solo avanza Cards o Tareas ya activas (AD-008 §3)")
    if pattern == "D" and actor.kind == "agent":
        raise TwinRuleError(f"{entity}: un Agente no puede pausar ni archivar (AD-008 §3)")


def _check_insert(obj, pattern: str | None, actor: Actor) -> None:
    if actor.kind != "agent" or pattern is None:
        return
    state = _value(getattr(obj, type(obj).__state_attr__, None)) if pattern in _TRANSITIONS else None
    if pattern == "A" and state not in (None, "proposed", "presented"):
        raise TwinRuleError(f"{type(obj).__name__}: un Agente solo puede proponer (AD-008 §3)")
    if pattern == "B" and state == "completed":
        raise TwinRuleError(f"{type(obj).__name__}: un Agente no crea trabajo ya completado (AD-008 §3)")


def _add_event(session, ctx: _Context, obj, event_type: str, data: dict, actor: Actor) -> None:
    from app.models.models import Event
    company_id, project_id = ctx.scope(obj)
    session.add(Event(
        project_id=project_id,
        company_id=company_id,
        event_type=event_type,
        entity_type=type(obj).__tablename__,
        entity_id=obj.id,
        data={"label": _label(obj), **data},
        category="domain",
        actor_type=actor.kind,
        actor_id=actor.id or actor.label,
    ))


def _add_version(session, ctx: _Context, obj, change: str, changes: dict | None, actor: Actor) -> None:
    from app.twin.models import EntityVersion
    company_id, _ = ctx.scope(obj)
    session.add(EntityVersion(
        company_id=company_id,
        entity_type=type(obj).__tablename__,
        entity_id=obj.id,
        version=obj.version,
        change=change,
        changes=changes,
        snapshot=_snapshot(obj),
        actor_type=actor.kind,
        actor_id=actor.id or actor.label,
        reason=current_reason(),
    ))


def _ensure_id(obj) -> None:
    """Las PK se generan al hacer INSERT; la versión y el evento las necesitan antes."""
    if getattr(obj, "id", None) is None:
        obj.id = str(uuid.uuid4())


@event.listens_for(Session, "before_flush")
def _enforce_twin_rules(session: Session, flush_context, instances) -> None:
    actor = current_actor()
    ctx = _Context(session)

    # 1 y 2: nada se borra; los registros permanentes y el historial no se tocan
    for obj in session.deleted:
        if _pattern(obj) == "C" or _is_versioned(obj) or type(obj).__tablename__ in _APPEND_ONLY_TABLES:
            raise TwinRuleError(f"{type(obj).__name__}: nada se borra en el Gemelo; se archiva (AD-002 §1.5)")

    for obj in list(session.dirty):
        if not session.is_modified(obj, include_collections=False):
            continue
        if _pattern(obj) == "C" or type(obj).__tablename__ in _APPEND_ONLY_TABLES:
            raise TwinRuleError(f"{type(obj).__name__}: es un registro permanente; no se modifica (Patrón C)")

    # 3, 4 y 5: altas
    for obj in list(session.new):
        if not (_is_versioned(obj) or _pattern(obj) == "C"):
            continue
        pattern = _pattern(obj)
        _check_insert(obj, pattern, actor)
        if pattern == "C":
            if _is_twin_business(obj):
                # Un Suceso Empresarial no tiene versiones (no cambia), pero sí va al Timeline
                _ensure_id(obj)
                obj.created_by = obj.updated_by = str(actor)
                _add_event(session, ctx, obj, "entity_created", {}, actor)
            continue
        _ensure_id(obj)
        if hasattr(obj, "created_by") and getattr(obj, "created_by", None) is None and _is_twin_business(obj):
            obj.created_by = str(actor)
        obj.updated_by = str(actor)
        if obj.version is None:
            obj.version = 1
        _add_version(session, ctx, obj, "created", None, actor)
        if _is_twin_business(obj):
            data = {}
            state_attr = getattr(type(obj), "__state_attr__", None)
            if state_attr:
                data["state"] = _value(getattr(obj, state_attr))
            _add_event(session, ctx, obj, "entity_created", data, actor)

    # 3, 4 y 5: cambios
    for obj in list(session.dirty):
        if not _is_versioned(obj) or not session.is_modified(obj, include_collections=False):
            continue
        state = inspect(obj)
        changes: dict[str, list] = {}
        stored: dict | None = None
        for attr in state.mapper.column_attrs:
            if attr.key in _BOOKKEEPING:
                continue
            hist = state.attrs[attr.key].history
            if hist.has_changes():
                if hist.deleted:
                    old = _json(hist.deleted[0])
                else:
                    # Atributo expirado (p. ej. tras un commit): el valor anterior está en la base
                    if stored is None:
                        stored = _stored_values(session, obj)
                    old = stored.get(attr.key)
                new = _json(hist.added[0]) if hist.added else None
                if old != new:
                    changes[attr.key] = [old, new]
        if not changes:
            continue

        pattern = _pattern(obj)
        state_attr = getattr(type(obj), "__state_attr__", None)
        change = "updated"
        if pattern in _TRANSITIONS and state_attr in changes:
            old_state, new_state = changes[state_attr]
            _check_transition(obj, pattern, old_state, new_state, actor)
            _add_event(session, ctx, obj, "state_changed", {"from": old_state, "to": new_state}, actor)
            change = "archived" if new_state == "archived" else "transition"
        elif "status" in changes and pattern != "D":
            # Contrato Base: activo ↔ archivado (nunca eliminado)
            old_status, new_status = changes["status"]
            if actor.kind == "agent":
                raise TwinRuleError(f"{type(obj).__name__}: un Agente no archiva entidades (AD-008 §3)")
            if new_status == "archived":
                change = "archived"
                _add_event(session, ctx, obj, "entity_archived", {"from": old_status}, actor)
            elif old_status == "archived":
                change = "restored"
                _add_event(session, ctx, obj, "entity_restored", {}, actor)

        obj.version = (obj.version or 1) + 1
        obj.updated_by = str(actor)
        _add_version(session, ctx, obj, change, changes, actor)
