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
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.models.models import Company, Event, User
from app.twin import models as tm
from app.twin.actor import Actor, acting_as, set_request_actor
from app.twin import decisions as twin_decisions, lifecycle
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


def _writable_company(db: Session, company_id: str, user: User) -> Company:
    company = get_owned_company(db, company_id, user)
    try:
        lifecycle.ensure_writable(company)
    except lifecycle.LifecycleError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return company


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
    _writable_company(db, company_id, user)
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
    _writable_company(db, company_id, user)
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
    _writable_company(db, company_id, user)
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
    _writable_company(db, company_id, user)
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
    before_id: Optional[str] = None,
    include_cognitive: bool = False,
    db: Session = Depends(get_db), user: User = Depends(acting_user),
):
    """Eventos del Gemelo, del más reciente al más antiguo (AD-UX-08, AD-008 §4).

    Paginación por cursor: `before` (y `before_id`, el último evento recibido) devuelven los
    anteriores sin perder los que comparten la misma marca de tiempo.
    """
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
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="before debe ser una fecha ISO") from exc
        older = Event.created_at < cutoff
        if before_id:
            older = or_(older, and_(Event.created_at == cutoff, Event.id < before_id))
        query = query.filter(older)
    events = query.order_by(Event.created_at.desc(), Event.id.desc()).limit(limit).all()
    return [{"id": e.id, "event_type": e.event_type, "entity_type": e.entity_type, "entity_id": e.entity_id,
             "category": e.category, "data": e.data or {}, "actor_type": e.actor_type, "actor_id": e.actor_id,
             "created_at": e.created_at.isoformat()} for e in events]


# ============================================================
# Decisiones (AD-CMP-03, AD-FUNC-02 §2.5) — vista DEC (AD-UX-10)
# ============================================================

def _decision_out(d) -> dict[str, Any]:
    from app.schemas.schemas import DecisionResponse
    return DecisionResponse.model_validate(d).model_dump(mode="json")


def _owned_decision(db: Session, company_id: str, decision_id: str, user: User):
    from app.core.authz import get_owned_project
    from app.models.models import Decision
    project = get_owned_project(db, company_id, user)
    decision = db.query(Decision).filter(Decision.id == decision_id, Decision.project_id == project.id).first()
    if decision is None:
        raise HTTPException(status_code=404, detail="Decisión no encontrada")
    return project, decision


@router.get("/{company_id}/decisions")
def list_decisions(company_id: str, db: Session = Depends(get_db), user: User = Depends(acting_user)):
    """Todas las decisiones del Gemelo con su ciclo, opciones, disenso y registro de §2.5."""
    from app.core.authz import get_owned_project
    from app.models.models import Decision
    from app.twin.models import BusinessDecision
    project = get_owned_project(db, company_id, user)
    decisions = db.query(Decision).filter(Decision.project_id == project.id).order_by(Decision.created_at.desc()).all()
    business = {b.adan_decision_id: b for b in db.query(BusinessDecision).filter(
        BusinessDecision.company_id == company_id, BusinessDecision.adan_decision_id.isnot(None)).all()}
    out = []
    for d in decisions:
        item = _decision_out(d)
        b = business.get(d.id)
        item["business_decision"] = {"id": b.id, "title": b.title, "state": b.state} if b else None
        out.append(item)
    return out


class ProposeBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = PydField(..., min_length=3, max_length=255)
    description: str | None = PydField(None, max_length=20000)
    options: list[dict[str, Any]] = PydField(..., min_length=2, max_length=10)
    recommended_option: str = PydField(..., max_length=50)


@router.post("/{company_id}/decisions", status_code=201)
def propose_decision(company_id: str, body: ProposeBody, db: Session = Depends(get_db),
                     user: User = Depends(acting_user)):
    """El cliente (o un Usuario con delegación) registra una propuesta con sus opciones.

    Los Agentes proponen por sus propios flujos (Board Room, Gate Review).
    """
    from app.core.authz import get_owned_project
    from app.models.models import Decision, DecisionStatus
    _writable_company(db, company_id, user)
    project = get_owned_project(db, company_id, user)
    keys = [str(o.get("key", "")).strip() for o in body.options]
    if any(not k for k in keys) or len(set(keys)) != len(keys):
        raise HTTPException(status_code=422, detail="Cada opción necesita una clave única")
    if body.recommended_option not in keys:
        raise HTTPException(status_code=422, detail="La opción recomendada debe ser una de las opciones")
    options = [{"key": str(o["key"]).strip(), "label": str(o.get("label") or o["key"])[:255],
                "rationale": str(o.get("rationale") or "")[:2000],
                "evidence_level": o.get("evidence_level") if o.get("evidence_level") in ("alta", "media", "baja") else "baja",
                "confidence": float(o.get("confidence") or 0)} for o in body.options]
    decision = Decision(project_id=project.id, title=body.title, description=body.description,
                        proposed_by="Usuario Principal", status=DecisionStatus.PROPOSED, options=options,
                        recommended_option=body.recommended_option,
                        prior_decisions=twin_decisions.prior_decisions(db, project))
    db.add(decision)
    _commit(db)
    db.refresh(decision)
    return _decision_out(decision)


@router.post("/{company_id}/decisions/{decision_id}/present")
def present_decision(company_id: str, decision_id: str, db: Session = Depends(get_db),
                     user: User = Depends(acting_user)):
    _writable_company(db, company_id, user)
    _, decision = _owned_decision(db, company_id, decision_id, user)
    try:
        decision = twin_decisions.present(db, decision, Actor.user(user.id, user.name))
    except (twin_decisions.DecisionError, TwinRuleError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _decision_out(decision)


class DecideBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["approve", "reject"]
    chosen_option: str | None = PydField(None, max_length=50)
    risks_assumed: list[str] | None = PydField(None, max_length=20)
    responsibility_statement: str | None = PydField(None, max_length=2000)


@router.post("/{company_id}/decisions/{decision_id}/decide")
def decide_decision(company_id: str, decision_id: str, body: DecideBody, db: Session = Depends(get_db),
                    user: User = Depends(acting_user)):
    """Aprobar o rechazar (solo el cliente). Decidir distinto exige los 6 campos de §2.5."""
    from app.services.gemelo_digital import GemeloDigitalService
    _writable_company(db, company_id, user)
    project, decision = _owned_decision(db, company_id, decision_id, user)
    try:
        decision = GemeloDigitalService(db).decide(
            project, decision, body.action == "approve", user.id, chosen_option=body.chosen_option,
            risks_assumed=body.risks_assumed, responsibility_statement=body.responsibility_statement)
    except (twin_decisions.DecisionError, TwinRuleError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _decision_out(decision)


class ExecuteBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    business_decision_title: str | None = PydField(None, max_length=255)


@router.post("/{company_id}/decisions/{decision_id}/execute")
def execute_decision(company_id: str, decision_id: str, body: ExecuteBody | None = None,
                     db: Session = Depends(get_db), user: User = Depends(acting_user)):
    """Aprobada → Ejecutada. Opcionalmente registra la Decisión de Negocio que originó (§4)."""
    _writable_company(db, company_id, user)
    project, decision = _owned_decision(db, company_id, decision_id, user)
    try:
        decision = twin_decisions.execute(db, project, decision, user.id,
                                          business_title=body.business_decision_title if body else None)
    except (twin_decisions.DecisionError, TwinRuleError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _decision_out(decision)


# ============================================================
# Ciclo de vida (AD-CMP-06)
# ============================================================

class ReasonBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str | None = PydField(None, max_length=2000)


class ReinventBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    origin_story: str = PydField(..., min_length=10, max_length=20000)
    founding_motivation: str | None = PydField(None, max_length=20000)
    irreversible_commitment: str | None = PydField(None, max_length=20000)
    reason: str = PydField(..., min_length=10, max_length=2000)


class SplitBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    initiative_id: str
    name: str = PydField(..., min_length=1, max_length=255)
    description: str | None = PydField(None, max_length=5000)
    reason: str = PydField(..., min_length=10, max_length=2000)


class MergeBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    company_ids: list[str] = PydField(..., min_length=2, max_length=10)
    name: str = PydField(..., min_length=1, max_length=255)
    description: str | None = PydField(None, max_length=5000)
    reason: str = PydField(..., min_length=10, max_length=2000)


def _lifecycle_call(db: Session, fn, *args, **kwargs):
    try:
        return fn(db, *args, **kwargs)
    except (lifecycle.LifecycleError, TwinRuleError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _company_out(company: Company) -> dict[str, Any]:
    status = company.status.value if hasattr(company.status, "value") else company.status
    return {"id": company.id, "name": company.name, "status": status, "version": company.version}


@router.post("/lifecycle/merge", status_code=201)
def merge_twins(body: MergeBody, db: Session = Depends(get_db), user: User = Depends(acting_user)):
    companies = [get_owned_company(db, cid, user) for cid in body.company_ids]
    merged = _lifecycle_call(db, lifecycle.merge, companies, user, body.name, body.reason, body.description)
    return _company_out(merged)


@router.post("/{company_id}/lifecycle/reinvent")
def reinvent_twin(company_id: str, body: ReinventBody, db: Session = Depends(get_db),
                  user: User = Depends(acting_user)):
    company = get_owned_company(db, company_id, user)
    company = _lifecycle_call(db, lifecycle.reinvent, company, user, body.origin_story, body.reason,
                              body.founding_motivation, body.irreversible_commitment)
    return _company_out(company)


@router.post("/{company_id}/lifecycle/split", status_code=201)
def split_twin(company_id: str, body: SplitBody, db: Session = Depends(get_db),
               user: User = Depends(acting_user)):
    company = get_owned_company(db, company_id, user)
    child = _lifecycle_call(db, lifecycle.split, company, user, body.initiative_id, body.name, body.reason,
                            body.description)
    return _company_out(child)


@router.post("/{company_id}/lifecycle/pause")
def pause_twin(company_id: str, body: ReasonBody | None = None, db: Session = Depends(get_db),
               user: User = Depends(acting_user)):
    company = get_owned_company(db, company_id, user)
    return _company_out(_lifecycle_call(db, lifecycle.pause, company, user, body.reason if body else None))


@router.post("/{company_id}/lifecycle/resume")
def resume_twin(company_id: str, body: ReasonBody | None = None, db: Session = Depends(get_db),
                user: User = Depends(acting_user)):
    company = get_owned_company(db, company_id, user)
    return _company_out(_lifecycle_call(db, lifecycle.resume, company, user, body.reason if body else None))


@router.post("/{company_id}/lifecycle/archive")
def archive_twin(company_id: str, body: ReasonBody, db: Session = Depends(get_db),
                 user: User = Depends(acting_user)):
    if not body.reason or len(body.reason.strip()) < 10:
        raise HTTPException(status_code=422, detail="Archivar un Gemelo exige explicar por qué")
    company = get_owned_company(db, company_id, user)
    return _company_out(_lifecycle_call(db, lifecycle.archive, company, user, body.reason))
