"""API de Agentes por tiempo (WO-109): /api/v1/hire/..."""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.api.v1.nivel1 import get_llm
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.hire import service
from app.hire.models import AgentContract, AgentOffering
from app.models.models import User
from app.oos.models import WorkOrder
from app.twin import lifecycle

router = APIRouter(prefix="/hire", tags=["Agentes por tiempo (WO-109)"])


def get_tool_executor():
    from app.tef.api import _executor
    return _executor


class HireBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    offering_code: str = Field(..., max_length=50)
    period: Literal["hour", "day", "week", "month"]
    units: int = Field(..., ge=1, le=200)


class TaskBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)


class ReviewBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approve: bool
    feedback: Optional[str] = Field(None, max_length=5000)


def _offering_out(o: AgentOffering) -> dict:
    return {"code": o.code, "name": o.name, "role": o.role, "description": o.description, "skills": o.skills,
            "tools": o.tools, "tier": o.tier, "price_note": "Precio por definir (WO-100)"}


def _contract_out(db: Session, c: AgentContract) -> dict:
    offering = db.get(AgentOffering, c.offering_id)
    return {"id": c.id, "offering": _offering_out(offering), "period": c.period, "units": c.units,
            "hours_capacity": c.hours_capacity, "hours_used": service.hours_used(db, c),
            "starts_at": c.starts_at.isoformat(), "ends_at": c.ends_at.isoformat(),
            "state": service.contract_state(db, c), "price_note": c.price_note}


def _task_out(wo: WorkOrder) -> dict:
    meta = wo.metadata_json or {}
    return {"id": wo.id, "title": wo.title, "description": wo.description, "status": wo.status, "result": wo.result,
            "blocking_reason": wo.blocking_reason, "feedback": meta.get("feedback", []),
            "created_at": wo.created_at.isoformat() if wo.created_at else None,
            "completed_at": wo.completed_at.isoformat() if wo.completed_at else None}


def _company(db: Session, company_id: str, user: User, writable: bool = False):
    company = get_owned_company(db, company_id, user)
    if writable:
        try:
            lifecycle.ensure_writable(company)
        except lifecycle.LifecycleError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
    return company


def _contract(db: Session, company_id: str, contract_id: str) -> AgentContract:
    c = db.query(AgentContract).filter(AgentContract.id == contract_id, AgentContract.company_id == company_id).first()
    if c is None:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return c


def _task(db: Session, contract: AgentContract, task_id: str) -> WorkOrder:
    wo = db.query(WorkOrder).filter(WorkOrder.id == task_id, WorkOrder.assigned_to == contract.id).first()
    if wo is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return wo


@router.get("/catalog")
def catalog(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = [_offering_out(o) for o in service.offerings(db)]
    db.commit()
    return items


@router.get("/{company_id}/contracts")
def list_contracts(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _company(db, company_id, user)
    rows = db.query(AgentContract).filter(AgentContract.company_id == company_id) \
        .order_by(AgentContract.created_at.desc()).all()
    return [_contract_out(db, c) for c in rows]


@router.post("/{company_id}/contracts", status_code=201)
def hire(company_id: str, body: HireBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company = _company(db, company_id, user, writable=True)
    try:
        contract = service.hire(db, company, user, body.offering_code, body.period, body.units)
    except service.HireError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _contract_out(db, contract)


@router.post("/{company_id}/contracts/{contract_id}/cancel")
def cancel(company_id: str, contract_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _company(db, company_id, user, writable=True)
    return _contract_out(db, service.cancel(db, _contract(db, company_id, contract_id)))


@router.get("/{company_id}/contracts/{contract_id}/tasks")
def list_tasks(company_id: str, contract_id: str, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    _company(db, company_id, user)
    return [_task_out(t) for t in service.contract_tasks(db, _contract(db, company_id, contract_id))]


@router.post("/{company_id}/contracts/{contract_id}/tasks", status_code=201)
def assign(company_id: str, contract_id: str, body: TaskBody, db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    company = _company(db, company_id, user, writable=True)
    try:
        wo = service.assign_task(db, company, _contract(db, company_id, contract_id), body.title, body.description)
    except service.HireError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _task_out(wo)


@router.post("/{company_id}/contracts/{contract_id}/tasks/{task_id}/run")
async def run(company_id: str, contract_id: str, task_id: str, db: Session = Depends(get_db),
              user: User = Depends(get_current_user), llm: LLMAdapter = Depends(get_llm),
              executor=Depends(get_tool_executor)):
    company = _company(db, company_id, user, writable=True)
    contract = _contract(db, company_id, contract_id)
    wo = _task(db, contract, task_id)
    try:
        log = await service.run_task(db, company, user, contract, wo, llm, executor)
    except service.HireError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.refresh(wo)
    return {"task": _task_out(wo), "work": {"seconds": log.seconds, "outcome": log.outcome, "model": log.model,
                                            "degraded": log.degraded, "tools_used": log.tools_used,
                                            "cost_usd": log.cost_usd}}


@router.post("/{company_id}/contracts/{contract_id}/tasks/{task_id}/review")
def review(company_id: str, contract_id: str, task_id: str, body: ReviewBody, db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    _company(db, company_id, user, writable=True)
    contract = _contract(db, company_id, contract_id)
    try:
        wo = service.review(db, _task(db, contract, task_id), body.approve, body.feedback)
    except service.HireError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _task_out(wo)


@router.get("/{company_id}/contracts/{contract_id}/report")
def report(company_id: str, contract_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _company(db, company_id, user)
    return service.report(db, _contract(db, company_id, contract_id))
