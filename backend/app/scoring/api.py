"""API de Evidencia y Scoring (WO-107): /api/v1/scoring/{company_id}/..."""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.authz import get_owned_company, get_owned_project
from app.core.database import get_db
from app.models.models import User
from app.scoring import engine, external, service
from app.twin import lifecycle
from app.twin.actor import Actor, acting_as
from app.twin.api import acting_user
from app.twin.models import Evidence

router = APIRouter(prefix="/scoring", tags=["Evidencia y Scoring (WO-107)"])


class EvidenceBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dimension: str = Field("problem", max_length=30)
    claim: str = Field(..., min_length=10, max_length=5000)
    kind: Literal["external", "testimony"]
    polarity: Literal["supports", "contradicts"] = "supports"
    source: Optional[str] = Field(None, max_length=2000)


class ArchiveBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(..., min_length=5, max_length=1000)


def _evidence_out(e: Evidence) -> dict:
    return {"id": e.id, "dimension": e.dimension, "claim": e.claim, "kind": e.kind,
            "kind_label": engine.TIERS[e.kind]["label"], "polarity": e.polarity, "source": e.source,
            "level_number": e.level_number, "status": e.status, "created_by": e.created_by,
            "confidence_level": e.confidence_level, "confirmed": e.confirmed, "verification": e.verification,
            "created_at": e.created_at.isoformat()}


def _gate_out(evaluation: engine.GateEvaluation) -> dict:
    s = evaluation.score
    return {"level_number": evaluation.level_number, "sufficient": evaluation.sufficient,
            "missing": evaluation.missing, "score_type": s.score_type, "value": s.value,
            "confidence": s.confidence, "reasoning": s.reasoning, "breakdown": s.breakdown}


def _writable(db: Session, company_id: str, user: User):
    company = get_owned_company(db, company_id, user)
    try:
        lifecycle.ensure_writable(company)
    except lifecycle.LifecycleError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return company, get_owned_project(db, company_id, user)


@router.get("/{company_id}/evidence")
def list_evidence(company_id: str, dimension: Optional[str] = None, include_archived: bool = False,
                  db: Session = Depends(get_db), user: User = Depends(acting_user)):
    project = get_owned_project(db, company_id, user)
    q = db.query(Evidence).filter(Evidence.project_id == project.id)  # incluye las propuestas de CSI
    if dimension:
        q = q.filter(Evidence.dimension == dimension)
    if not include_archived:
        q = q.filter(Evidence.status == "active")
    return [_evidence_out(e) for e in q.order_by(Evidence.created_at.desc()).all()]


@router.post("/{company_id}/evidence", status_code=201)
async def add_evidence(company_id: str, body: EvidenceBody, db: Session = Depends(get_db),
                       user: User = Depends(acting_user)):
    _, project = _writable(db, company_id, user)
    # Si la fuente es un enlace, ADÁN la abre y deja constancia (WO-108): verificable → verificado
    verification = await external.verify_source(body.source.strip()) if external.looks_like_url(body.source) else None
    try:
        item = service.record_evidence(db, project, user, dimension=body.dimension, claim=body.claim,
                                       kind=body.kind, polarity=body.polarity, source=body.source,
                                       verification=verification)
    except service.EvidenceError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _evidence_out(item)


class CsiBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: Optional[str] = Field(None, max_length=2000)


@router.post("/{company_id}/csi/search")
async def csi_search(company_id: str, body: CsiBody, db: Session = Depends(get_db),
                     user: User = Depends(acting_user)):
    """Pide a CSI evidencia externa sobre el dolor; llega como propuesta que el cliente confirma o descarta."""
    company, project = _writable(db, company_id, user)
    query = (body.query or company.description or company.name).strip()
    try:
        signals = await external.csi_signals(query, country=company.country, industry=company.industry)
    except external.CsiUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    known = {e.source for e in service.active_evidence(db, project, include_unconfirmed=True)}
    created = []
    for signal in signals:
        if signal["source"] in known:
            continue  # no repetir lo que ya está (AD-CMP-04 §4)
        verification = await external.verify_source(signal["source"]) if external.looks_like_url(signal["source"]) else None
        created.append(service.record_csi_signal(db, project, signal, verification))
    db.commit()
    return [_evidence_out(e) for e in created]


@router.post("/{company_id}/evidence/{evidence_id}/confirm")
def confirm_evidence(company_id: str, evidence_id: str, db: Session = Depends(get_db),
                     user: User = Depends(acting_user)):
    _, project = _writable(db, company_id, user)
    item = db.query(Evidence).filter(Evidence.id == evidence_id, Evidence.project_id == project.id,
                                     Evidence.status == "active").first()
    if item is None:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    return _evidence_out(service.confirm_evidence(db, item, user))


@router.get("/{company_id}/csi")
def csi_status(company_id: str, db: Session = Depends(get_db), user: User = Depends(acting_user)):
    get_owned_company(db, company_id, user)
    from app.core.config import settings
    return {"connected": bool(settings.CSI_BASE_URL)}


@router.post("/{company_id}/evidence/{evidence_id}/archive")
def archive_evidence(company_id: str, evidence_id: str, body: ArchiveBody, db: Session = Depends(get_db),
                     user: User = Depends(acting_user)):
    """Retirar evidencia es archivarla: nunca se borra y los Scores anteriores la siguen citando."""
    _, project = _writable(db, company_id, user)
    item = db.query(Evidence).filter(Evidence.id == evidence_id, Evidence.project_id == project.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    with acting_as(Actor.user(user.id, user.name), reason=body.reason):
        item.status = "archived"
        db.commit()
    db.refresh(item)
    return _evidence_out(item)


@router.get("/{company_id}/scores")
def scores_overview(company_id: str, db: Session = Depends(get_db), user: User = Depends(acting_user)):
    """Los 8 Scores de AD-FUNC-07 con su último cálculo, su confianza y su desglose de evidencia."""
    return service.overview(db, get_owned_project(db, company_id, user))


@router.post("/{company_id}/scores/{score_type}/calculate")
def calculate(company_id: str, score_type: str, db: Session = Depends(get_db), user: User = Depends(acting_user)):
    company, project = _writable(db, company_id, user)
    entry = next((s for s in service.overview(db, project) if s["key"] == score_type), None)
    if entry is None:
        raise HTTPException(status_code=404, detail="Score desconocido")
    if not entry["available"]:
        raise HTTPException(status_code=409, detail=f"{entry['label']}: {entry['unavailable_reason']}")
    if score_type == "responsible":
        service.calculate_responsible(db, project, company)
    elif score_type == "venture":
        service.calculate_venture(db, project)
    else:
        service.calculate_dimension(db, project, score_type)
    return next(s for s in service.overview(db, project) if s["key"] == score_type)


@router.get("/{company_id}/gate/{level_number}")
def gate_preview(company_id: str, level_number: int, db: Session = Depends(get_db),
                 user: User = Depends(acting_user)):
    """Qué tan cerca está el Nivel de tener evidencia suficiente (no guarda nada)."""
    project = get_owned_project(db, company_id, user)
    if level_number not in engine.GATE_RULES:
        raise HTTPException(status_code=404, detail="Ese Nivel todavía no tiene regla de Gate")
    rule = engine.GATE_RULES[level_number]
    rows = service.active_evidence(db, project, rule.score_type)
    return _gate_out(engine.evaluate_gate(level_number, service._items(rows)))
