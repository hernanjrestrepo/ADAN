"""API del Gemelo Digital (WO-098): `/api/v1/twin/...`.

- `GET  /twin/kinds`: catálogo de entidades de negocio (nombres de AD-003).
- `GET  /twin/{company_id}`: identidad del Gemelo (Edad, Madurez, Etapa, Velocidad de
  Maduración), conteo por entidad y linaje.
- `GET|POST /twin/{company_id}/entities/{kind}` y `GET|PATCH .../{id}`: las 23 entidades de
  negocio y el Riesgo, con versión e historial automáticos (app/twin/hooks.py).
- `POST .../{id}/archive` y `.../restore`: nunca se borra (AD-002 §1.5).
- `GET  /twin/{company_id}/history/{entity_type}/{entity_id}`: versiones de una entidad.
- `GET  /twin/{company_id}/timeline`: eventos de dominio (AD-UX-08).
- `GET  /twin/agents`: catálogo de Agentes.

Todo lo que pasa por aquí queda a nombre del usuario autenticado (AD-008 §3).
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field as PydField, ValidationError, create_model
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.models.models import Company, Event, User
from app.twin import models as tm
from app.twin.actor import Actor, acting_as, set_request_actor
from app.twin.agents import ensure_agent_catalog
from app.twin.hooks import TwinRuleError
from app.twin.registry import (
    CONTRACT_FIELDS, KINDS, RISK_SUBJECTS, EntityKind, Field, describe, kind_or_none,
)

router = APIRouter(prefix="/twin", tags=["twin"])


async def acting_user(user: User = Depends(get_current_user)) -> User:
    """Todo cambio de esta API queda a nombre del cliente autenticado.

    Es async a propósito: corre en la tarea de la request, así el actor llega a los
    endpoints (que corren en el threadpool con una copia del contexto).
    """
    set_request_actor(Actor.user(user.id, user.name))
    return user


# ============================================================
# Validación dinámica por tipo de entidad
# ============================================================

def _annotation(f: Field) -> Any:
    if f.choices:
        return Literal[f.choices]  # type: ignore[valid-type]
    return f.type


def _pyd_field(f: Field, required: bool) -> tuple[Any, Any]:
    ann = _annotation(f)
    kwargs: dict[str, Any] = {}
    if f.max_length and f.type is str:
        kwargs["max_length"] = f.max_length
    if required:
        return ann, PydField(..., **kwargs)
    return Optional[ann], PydField(None, **kwargs)


def _build_models(kind: EntityKind) -> tuple[type[BaseModel], type[BaseModel]]:
    config = ConfigDict(extra="forbid")
    create_fields = {name: _pyd_field(f, f.required) for name, f in kind.fields.items()}
    update_fields = {name: _pyd_field(f, False) for name, f in kind.fields.items()}
    for name, f in CONTRACT_FIELDS.items():
        create_fields[name] = _pyd_field(f, False)
        update_fields[name] = _pyd_field(f, False)
    create_fields["confidence_level"] = (Optional[float], PydField(None, ge=0, le=100))
    update_fields["confidence_level"] = (Optional[float], PydField(None, ge=0, le=100))
    update_fields["reason"] = (Optional[str], PydField(None, max_length=2000))
    create_model_ = create_model(f"{kind.model.__name__}Create", __config__=config, **create_fields)
    update_model_ = create_model(f"{kind.model.__name__}Update", __config__=config, **update_fields)
    return create_model_, update_model_


_MODELS = {key: _build_models(kind) for key, kind in KINDS.items()}


def _validate(model_cls: type[BaseModel], body: dict[str, Any]) -> BaseModel:
    try:
        return model_cls.model_validate(body)
    except ValidationError as exc:
        errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
        raise HTTPException(status_code=422, detail=errors) from exc


def _kind(key: str) -> EntityKind:
    kind = kind_or_none(key)
    if kind is None:
        raise HTTPException(status_code=404, detail=f"Tipo de entidad desconocido: {key}")
    return kind


def _serialize(obj) -> dict[str, Any]:
    from sqlalchemy import inspect as sa_inspect
    out: dict[str, Any] = {}
    for attr in sa_inspect(obj).mapper.column_attrs:
        value = getattr(obj, attr.key)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        elif hasattr(value, "value"):
            value = value.value
        out[attr.key] = value
    return out


def _get_entity(db: Session, kind: EntityKind, company_id: str, entity_id: str):
    obj = db.query(kind.model).filter(kind.model.id == entity_id, kind.model.company_id == company_id).first()
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{kind.label} no encontrado")
    return obj


def _validate_refs(db: Session, kind: EntityKind, company_id: str, data: dict[str, Any]) -> None:
    """Toda referencia apunta a una entidad activa de la misma empresa (frontera del Gemelo)."""
    for name, f in kind.fields.items():
        if f.ref and data.get(name):
            target = KINDS[f.ref]
            exists = db.query(target.model.id).filter(
                target.model.id == data[name], target.model.company_id == company_id,
                target.model.status == "active").first()
            if not exists:
                raise HTTPException(status_code=422, detail=f"{name}: {target.label} no encontrado en esta empresa")
    if kind.key == "risks" and "subject_type" in data:
        subject_type, subject_id = data["subject_type"], data.get("subject_id")
        if subject_type == "company":
            if subject_id != company_id:
                raise HTTPException(status_code=422, detail="subject_id debe ser el id de la empresa")
        else:
            target = KINDS[RISK_SUBJECTS[subject_type]]
            if not db.query(target.model.id).filter(
                    target.model.id == subject_id, target.model.company_id == company_id).first():
                raise HTTPException(status_code=422, detail=f"subject_id: {target.label} no encontrado")


def _commit(db: Session) -> None:
    try:
        db.commit()
    except TwinRuleError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc


# ============================================================
# Catálogos
# ============================================================

@router.get("/kinds")
def list_kinds(user: User = Depends(acting_user)):
    return [describe(kind) for kind in KINDS.values()]


@router.get("/agents")
def list_agents(db: Session = Depends(get_db), user: User = Depends(acting_user)):
    ensure_agent_catalog(db)
    db.commit()
    return [{"id": a.id, "code": a.code, "name": a.name, "description": a.description}
            for a in db.query(tm.Agent).order_by(tm.Agent.name).all()]


# ============================================================
# Identidad del Gemelo (AD-005 §4, AD-007)
# ============================================================

def lifecycle_stage(age_years: float, maturity: float) -> str:
    """Etapa del Ciclo de Vida: etiqueta derivada de Edad × Madurez (AD-005 §4).

    No se almacena. La Ley 5 (Estancamiento) se reconoce por la divergencia: mucha Edad con
    poca Madurez.
    """
    if age_years < 1:
        return "nacimiento"
    if age_years >= 5 and maturity < 0.3:
        return "estancamiento"
    if maturity < 0.3:
        return "temprana"
    if maturity < 0.7:
        return "crecimiento"
    return "madurez"


def maturation_velocity(db: Session, company: Company) -> float | None:
    """Δ Madurez / Δ Tiempo, por año, desde el historial de versiones (AD-005 §4).

    Se calcula, no se guarda: del valor de Madurez al nacer el Gemelo al último registrado.
    """
    rows = db.query(tm.EntityVersion.changes, tm.EntityVersion.created_at).filter(
        tm.EntityVersion.entity_type == "companies", tm.EntityVersion.entity_id == company.id,
    ).order_by(tm.EntityVersion.version).all()
    changes = [(created_at, c["maturity"]) for c, created_at in rows if c and "maturity" in c]
    if not changes:
        return None
    first_value = changes[0][1][0] or 0.0
    last_time, (_, last_value) = changes[-1]
    years = (last_time - company.created_at).total_seconds() / (365.25 * 86400)
    if years <= 0 or last_value is None:
        return None
    return round((last_value - first_value) / years, 4)


@router.get("/{company_id}")
def twin_overview(company_id: str, db: Session = Depends(get_db), user: User = Depends(acting_user)):
    company = get_owned_company(db, company_id, user)
    today = datetime.now(timezone.utc).date()
    born = company.founded_on or company.created_at.date()
    age_years = round(max(0, (today - born).days) / 365.25, 2)
    maturity = company.maturity or 0.0

    counts = {}
    for key, kind in KINDS.items():
        counts[key] = db.query(func.count(kind.model.id)).filter(
            kind.model.company_id == company_id, kind.model.status == "active").scalar()

    lineage = db.query(tm.TwinLineage).filter(
        (tm.TwinLineage.company_id == company_id) | (tm.TwinLineage.source_company_id == company_id)
    ).order_by(tm.TwinLineage.created_at).all()

    status = company.status.value if hasattr(company.status, "value") else company.status
    return {
        "company": {"id": company.id, "name": company.name, "status": status,
                    "version": company.version, "founded_on": company.founded_on.isoformat()
                    if company.founded_on else None, "jurisdiction": company.jurisdiction,
                    "legal_structure": company.legal_structure, "intangibles": company.intangibles or {}},
        "identity": {
            "age_years": age_years,
            "maturity": maturity,
            "lifecycle_stage": lifecycle_stage(age_years, maturity),
            "maturation_velocity_per_year": maturation_velocity(db, company),
        },
        "counts": counts,
        "lineage": [{"company_id": row.company_id, "source_company_id": row.source_company_id,
                     "relation": row.relation, "initiative_id": row.initiative_id, "note": row.note,
                     "created_at": row.created_at.isoformat()} for row in lineage],
    }


# ============================================================
# Entidades de negocio (CRUD sin borrado)
# ============================================================

@router.get("/{company_id}/entities/{kind_key}")
def list_entities(
    company_id: str, kind_key: str,
    include_archived: bool = False,
    db: Session = Depends(get_db), user: User = Depends(acting_user),
):
    get_owned_company(db, company_id, user)
    kind = _kind(kind_key)
    query = db.query(kind.model).filter(kind.model.company_id == company_id)
    if not include_archived:
        query = query.filter(kind.model.status == "active")
    return [_serialize(obj) for obj in query.order_by(kind.model.created_at).all()]


@router.post("/{company_id}/entities/{kind_key}", status_code=201)
def create_entity(
    company_id: str, kind_key: str, body: dict[str, Any],
    db: Session = Depends(get_db), user: User = Depends(acting_user),
):
    get_owned_company(db, company_id, user)
    kind = _kind(kind_key)
    create_cls, _ = _MODELS[kind.key]
    data = _validate(create_cls, body).model_dump(exclude_none=True)
    _validate_refs(db, kind, company_id, data)
    obj = kind.model(company_id=company_id, **data)
    db.add(obj)
    _commit(db)
    db.refresh(obj)
    return _serialize(obj)


@router.get("/{company_id}/entities/{kind_key}/{entity_id}")
def get_entity(company_id: str, kind_key: str, entity_id: str,
               db: Session = Depends(get_db), user: User = Depends(acting_user)):
    get_owned_company(db, company_id, user)
    kind = _kind(kind_key)
    return _serialize(_get_entity(db, kind, company_id, entity_id))


@router.patch("/{company_id}/entities/{kind_key}/{entity_id}")
def update_entity(
    company_id: str, kind_key: str, entity_id: str, body: dict[str, Any],
    db: Session = Depends(get_db), user: User = Depends(acting_user),
):
    get_owned_company(db, company_id, user)
    kind = _kind(kind_key)
    _, update_cls = _MODELS[kind.key]
    data = _validate(update_cls, body).model_dump(exclude_unset=True)
    reason = data.pop("reason", None)
    for name, f in kind.fields.items():
        if f.required and name in data and data[name] is None:
            raise HTTPException(status_code=422, detail=f"{name} es obligatorio")
    obj = _get_entity(db, kind, company_id, entity_id)
    if obj.status == "archived":
        raise HTTPException(status_code=409, detail=f"{kind.label} archivado: restáuralo antes de editarlo")
    _validate_refs(db, kind, company_id, data)
    with acting_as(Actor.user(user.id, user.name), reason=reason):
        for key, value in data.items():
            setattr(obj, key, value)
        _commit(db)
    db.refresh(obj)
    return _serialize(obj)


class ArchiveBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str | None = PydField(None, max_length=2000)


def _set_status(db, user, company_id, kind_key, entity_id, status, reason):
    get_owned_company(db, company_id, user)
    kind = _kind(kind_key)
    obj = _get_entity(db, kind, company_id, entity_id)
    if obj.status == status:
        return _serialize(obj)
    with acting_as(Actor.user(user.id, user.name), reason=reason):
        obj.status = status
        _commit(db)
    db.refresh(obj)
    return _serialize(obj)


@router.post("/{company_id}/entities/{kind_key}/{entity_id}/archive")
def archive_entity(company_id: str, kind_key: str, entity_id: str, body: ArchiveBody | None = None,
                   db: Session = Depends(get_db), user: User = Depends(acting_user)):
    return _set_status(db, user, company_id, kind_key, entity_id, "archived", body.reason if body else None)


@router.post("/{company_id}/entities/{kind_key}/{entity_id}/restore")
def restore_entity(company_id: str, kind_key: str, entity_id: str, body: ArchiveBody | None = None,
                   db: Session = Depends(get_db), user: User = Depends(acting_user)):
    return _set_status(db, user, company_id, kind_key, entity_id, "active", body.reason if body else None)


class RolesBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    functional_role_ids: list[str]


@router.put("/{company_id}/entities/positions/{position_id}/roles")
def set_position_roles(company_id: str, position_id: str, body: RolesBody,
                       db: Session = Depends(get_db), user: User = Depends(acting_user)):
    """Rol Funcional es N:M con Cargo (AD-006 §3)."""
    get_owned_company(db, company_id, user)
    position = _get_entity(db, KINDS["positions"], company_id, position_id)
    role_ids = sorted(set(body.functional_role_ids))
    found = {r for (r,) in db.query(tm.FunctionalRole.id).filter(
        tm.FunctionalRole.id.in_(role_ids), tm.FunctionalRole.company_id == company_id).all()}
    if found != set(role_ids):
        raise HTTPException(status_code=422, detail="Algún rol funcional no pertenece a esta empresa")
    table = tm.position_roles
    before = sorted(r for (r,) in db.execute(
        select(table.c.functional_role_id).where(table.c.position_id == position.id)).all())
    if before != role_ids:
        db.execute(table.delete().where(table.c.position_id == position.id))
        if role_ids:
            db.execute(table.insert(), [{"position_id": position.id, "functional_role_id": r} for r in role_ids])
        # La asociación no es una columna: se versiona explícitamente en el Cargo
        position.version = (position.version or 1) + 1
        position.updated_by = str(Actor.user(user.id))
        db.add(tm.EntityVersion(
            company_id=company_id, entity_type="positions", entity_id=position.id,
            version=position.version, change="updated",
            changes={"functional_role_ids": [before, role_ids]},
            snapshot={**_serialize(position), "functional_role_ids": role_ids},
            actor_type="user", actor_id=user.id,
        ))
        _commit(db)
    return {"position_id": position.id, "functional_role_ids": role_ids}


@router.get("/{company_id}/entities/positions/{position_id}/roles")
def get_position_roles(company_id: str, position_id: str,
                       db: Session = Depends(get_db), user: User = Depends(acting_user)):
    get_owned_company(db, company_id, user)
    position = _get_entity(db, KINDS["positions"], company_id, position_id)
    table = tm.position_roles
    role_ids = sorted(r for (r,) in db.execute(
        select(table.c.functional_role_id).where(table.c.position_id == position.id)).all())
    return {"position_id": position.id, "functional_role_ids": role_ids}


# ============================================================
# Historia y Timeline
# ============================================================

@router.get("/{company_id}/history/{entity_type}/{entity_id}")
def entity_history(company_id: str, entity_type: str, entity_id: str,
                   db: Session = Depends(get_db), user: User = Depends(acting_user)):
    get_owned_company(db, company_id, user)
    rows = db.query(tm.EntityVersion).filter(
        tm.EntityVersion.company_id == company_id,
        tm.EntityVersion.entity_type == entity_type,
        tm.EntityVersion.entity_id == entity_id,
    ).order_by(tm.EntityVersion.version).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Sin historial para esa entidad")
    return [{"version": r.version, "change": r.change, "changes": r.changes, "snapshot": r.snapshot,
             "actor_type": r.actor_type, "actor_id": r.actor_id, "reason": r.reason,
             "created_at": r.created_at.isoformat()} for r in rows]


@router.get("/{company_id}/timeline")
def timeline(
    company_id: str,
    limit: int = Query(50, ge=1, le=200),
    before: Optional[str] = None,
    include_cognitive: bool = False,
    db: Session = Depends(get_db), user: User = Depends(acting_user),
):
    """Eventos del Gemelo, del más reciente al más antiguo (AD-UX-08, AD-008 §4)."""
    get_owned_company(db, company_id, user)
    from app.models.models import Project
    project_ids = [p for (p,) in db.query(Project.id).filter(Project.company_id == company_id).all()]
    scope = [Event.company_id == company_id]
    if project_ids:
        scope.append(Event.project_id.in_(project_ids))
    query = db.query(Event).filter(or_(*scope))
    if not include_cognitive:
        query = query.filter(Event.category == "domain")
    if before:
        try:
            cutoff = datetime.fromisoformat(before)
            if cutoff.tzinfo is not None:
                cutoff = cutoff.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(Event.created_at < cutoff)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="before debe ser una fecha ISO") from exc
    events = query.order_by(Event.created_at.desc(), Event.id.desc()).limit(limit).all()
    return [{"id": e.id, "event_type": e.event_type, "entity_type": e.entity_type, "entity_id": e.entity_id,
             "category": e.category, "data": e.data or {}, "actor_type": e.actor_type, "actor_id": e.actor_id,
             "created_at": e.created_at.isoformat()} for e in events]
