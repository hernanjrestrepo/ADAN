"""
OOS API — Endpoints del Organizational Operating System.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, Company
from app.oos.models import WorkOrder, DecisionRecord, KPI, Risk, Organization
from app.oos.services import (
    OrganizationService, WorkOrderService, ProgressService,
    KPIService, RiskService, MeetingService,
)
from app.oos.workflow import WorkOrderEngine
from app.oos.scheduler import SchedulerEngine
from app.oos.kpi import KPIEngine

router = APIRouter(prefix="/oos", tags=["oos"])


# ============================================================
# Schemas
# ============================================================

class WorkOrderCreate(BaseModel):
    organization_id: str
    title: str
    description: str = ""
    priority: str = "medium"
    assigned_to_name: str | None = None
    due_date: str | None = None


class WorkOrderUpdate(BaseModel):
    status: str | None = None
    progress: float | None = None
    result: str | None = None
    blocking_reason: str | None = None


class WorkOrderResponse(BaseModel):
    id: str
    title: str
    description: str | None
    priority: str
    status: str
    assigned_to_name: str | None
    progress: float
    due_date: str | None
    created_at: str


class ProgressReportRequest(BaseModel):
    work_order_id: str
    progress: float
    status_update: str
    problems: list[str] = []
    evidence: list[str] = []
    next_steps: list[str] = []


class MeetingCreate(BaseModel):
    organization_id: str
    title: str
    participants: list[str] = []
    agenda: list[str] = []


class ReviewRequest(BaseModel):
    organization_id: str
    question: str


class KPICreate(BaseModel):
    organization_id: str
    name: str
    category: str
    current_value: float = 0.0
    target_value: float | None = None
    unit: str | None = None


class RiskCreate(BaseModel):
    organization_id: str
    title: str
    probability: str = "medium"
    impact: str = "medium"
    mitigation: str | None = None
    owner_name: str | None = None


class DashboardResponse(BaseModel):
    organization: dict | None
    work_orders: dict
    kpis: list[dict]
    risks: list[dict]
    overdue: list[dict]
    blocked: list[dict]
    escalation_candidates: list[dict]


# ============================================================
# Singletons
# ============================================================

def get_org_service(db: Session) -> OrganizationService:
    return OrganizationService(db)

def get_wo_service(db: Session) -> WorkOrderService:
    return WorkOrderService(db)

def get_wo_engine(db: Session) -> WorkOrderEngine:
    return WorkOrderEngine(db)

def get_scheduler(db: Session) -> SchedulerEngine:
    return SchedulerEngine(db)

def get_kpi_engine(db: Session) -> KPIEngine:
    return KPIEngine(db)

def get_progress_service(db: Session) -> ProgressService:
    return ProgressService(db)

def get_kpi_service(db: Session) -> KPIService:
    return KPIService(db)

def get_risk_service(db: Session) -> RiskService:
    return RiskService(db)

def get_meeting_service(db: Session) -> MeetingService:
    return MeetingService(db)


# ============================================================
# Autorización
# ============================================================

def require_organization(db: Session, organization_id: str, user: User) -> Organization:
    """Verifica que la organización pertenece a una empresa del usuario."""
    org = (
        db.query(Organization)
        .join(Company, Company.id == Organization.company_id)
        .filter(Organization.id == organization_id, Company.primary_user_id == user.id)
        .first()
    )
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    return org


def require_work_order(db: Session, work_order_id: str, user: User) -> WorkOrder:
    """Verifica que la Work Order pertenece a una organización del usuario."""
    wo = (
        db.query(WorkOrder)
        .join(Organization, Organization.id == WorkOrder.organization_id)
        .join(Company, Company.id == Organization.company_id)
        .filter(WorkOrder.id == work_order_id, Company.primary_user_id == user.id)
        .first()
    )
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    return wo


# ============================================================
# Work Orders
# ============================================================

@router.post("/workorders", response_model=WorkOrderResponse)
async def create_work_order(
    request: WorkOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea una Work Order."""
    require_organization(db, request.organization_id, current_user)
    service = get_wo_service(db)
    wo = service.create_from_decision(
        organization_id=request.organization_id,
        decision_id=None,
        title=request.title,
        description=request.description,
        priority=request.priority,
        assigned_to_name=request.assigned_to_name,
    )
    db.commit()
    return WorkOrderResponse(
        id=wo.id,
        title=wo.title,
        description=wo.description,
        priority=wo.priority,
        status=wo.status,
        assigned_to_name=wo.assigned_to_name,
        progress=wo.progress,
        due_date=wo.due_date.isoformat() if wo.due_date else None,
        created_at=wo.created_at.isoformat(),
    )


@router.get("/workorders/{organization_id}", response_model=list[WorkOrderResponse])
async def list_work_orders(
    organization_id: str,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista Work Orders de una organización."""
    require_organization(db, organization_id, current_user)
    service = get_wo_service(db)
    if status:
        wos = service.list_by_org(organization_id, status)
    else:
        wos = service.list_by_org(organization_id)
    return [
        WorkOrderResponse(
            id=wo.id,
            title=wo.title,
            description=wo.description,
            priority=wo.priority,
            status=wo.status,
            assigned_to_name=wo.assigned_to_name,
            progress=wo.progress,
            due_date=wo.due_date.isoformat() if wo.due_date else None,
            created_at=wo.created_at.isoformat(),
        )
        for wo in wos
    ]


@router.patch("/workorders/{work_order_id}")
async def update_work_order(
    work_order_id: str,
    request: WorkOrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza una Work Order."""
    wo = require_work_order(db, work_order_id, current_user)

    if request.status:
        wo.status = request.status
    if request.progress is not None:
        wo.progress = request.progress
    if request.result:
        wo.result = request.result
    if request.blocking_reason:
        wo.blocking_reason = request.blocking_reason

    db.commit()
    return {"status": "updated", "id": work_order_id}


@router.post("/workorders/{work_order_id}/start")
async def start_work_order(
    work_order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marca una Work Order como en progreso."""
    require_work_order(db, work_order_id, current_user)
    service = get_wo_service(db)
    service.start(work_order_id)
    db.commit()
    return {"status": "in_progress", "id": work_order_id}


@router.post("/workorders/{work_order_id}/complete")
async def complete_work_order(
    work_order_id: str,
    result: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marca una Work Order como completada."""
    require_work_order(db, work_order_id, current_user)
    service = get_wo_service(db)
    service.complete(work_order_id, result)
    db.commit()
    return {"status": "completed", "id": work_order_id}


@router.post("/workorders/{work_order_id}/progress")
async def report_progress(
    work_order_id: str,
    request: ProgressReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reporta progreso de una Work Order."""
    require_work_order(db, work_order_id, current_user)
    service = get_progress_service(db)
    report = service.report(
        work_order_id=work_order_id,
        reporter_id=str(current_user.id),
        reporter_name=current_user.name,
        progress=request.progress,
        status_update=request.status_update,
        problems=request.problems,
        evidence=request.evidence,
        next_steps=request.next_steps,
    )
    db.commit()
    return {"status": "reported", "report_id": report.id}


# ============================================================
# Dashboard
# ============================================================

@router.get("/dashboard/{organization_id}")
async def get_dashboard(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dashboard ejecutivo completo."""
    org = require_organization(db, organization_id, current_user)
    wo_service = get_wo_service(db)
    kpi_engine = get_kpi_engine(db)
    scheduler = get_scheduler(db)
    kpi_svc = get_kpi_service(db)
    risk_svc = get_risk_service(db)

    wos = wo_service.list_by_org(organization_id)
    open_wos = wo_service.list_open(organization_id)
    blocked_wos = wo_service.list_blocked(organization_id)

    # Actualizar KPIs
    kpi_engine.update_kpis_from_metrics(organization_id)
    kpis = kpi_svc.get_all(organization_id)
    risks = risk_svc.get_all(organization_id)

    # Scheduler checks
    overdue = scheduler.check_overdue(organization_id)
    escalation = scheduler.get_escalation_candidates(organization_id)

    return {
        "organization": {
            "id": org.id if org else None,
            "name": org.name if org else None,
        } if org else None,
        "work_orders": {
            "total": len(wos),
            "open": len(open_wos),
            "blocked": len(blocked_wos),
            "completed": sum(1 for wo in wos if wo.status == "completed"),
        },
        "kpis": [
            {
                "id": kpi.id,
                "name": kpi.name,
                "category": kpi.category,
                "current_value": kpi.current_value,
                "target_value": kpi.target_value,
                "unit": kpi.unit,
                "status": kpi.status,
            }
            for kpi in kpis
        ],
        "risks": [
            {
                "id": risk.id,
                "title": risk.title,
                "probability": risk.probability,
                "impact": risk.impact,
                "severity": risk.severity,
                "status": risk.status,
            }
            for risk in risks
        ],
        "overdue": overdue,
        "blocked": [
            {"id": wo.id, "title": wo.title, "reason": wo.blocking_reason}
            for wo in blocked_wos
        ],
        "escalation_candidates": escalation,
    }


# ============================================================
# KPIs
# ============================================================

@router.get("/kpis/{organization_id}")
async def get_kpis(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene todos los KPIs de una organización."""
    require_organization(db, organization_id, current_user)
    service = get_kpi_service(db)
    kpis = service.get_all(organization_id)
    return [
        {
            "id": kpi.id,
            "name": kpi.name,
            "category": kpi.category,
            "current_value": kpi.current_value,
            "target_value": kpi.target_value,
            "unit": kpi.unit,
            "status": kpi.status,
            "history": kpi.history[-5:] if kpi.history else [],
        }
        for kpi in kpis
    ]


@router.post("/kpis")
async def create_kpi(
    request: KPICreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un KPI."""
    require_organization(db, request.organization_id, current_user)
    service = get_kpi_service(db)
    kpi = service.create(
        organization_id=request.organization_id,
        name=request.name,
        category=request.category,
        current_value=request.current_value,
        target_value=request.target_value,
        unit=request.unit,
    )
    db.commit()
    return {"id": kpi.id, "name": kpi.name}


# ============================================================
# Risks
# ============================================================

@router.get("/risks/{organization_id}")
async def get_risks(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene todos los riesgos de una organización."""
    require_organization(db, organization_id, current_user)
    service = get_risk_service(db)
    risks = service.get_all(organization_id)
    return [
        {
            "id": risk.id,
            "title": risk.title,
            "probability": risk.probability,
            "impact": risk.impact,
            "severity": risk.severity,
            "status": risk.status,
            "mitigation": risk.mitigation,
            "owner_name": risk.owner_name,
        }
        for risk in risks
    ]


@router.post("/risks")
async def create_risk(
    request: RiskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un riesgo."""
    require_organization(db, request.organization_id, current_user)
    service = get_risk_service(db)
    risk = service.create(
        organization_id=request.organization_id,
        title=request.title,
        probability=request.probability,
        impact=request.impact,
        mitigation=request.mitigation,
        owner_name=request.owner_name,
    )
    db.commit()
    return {"id": risk.id, "title": risk.title, "severity": risk.severity}


# ============================================================
# Review
# ============================================================

@router.post("/review")
async def board_review(
    request: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Revisión ejecutiva — responde preguntas del Board
    usando información persistida.
    """
    require_organization(db, request.organization_id, current_user)
    wo_service = get_wo_service(db)
    scheduler = get_scheduler(db)
    kpi_engine = get_kpi_engine(db)
    kpi_svc = get_kpi_service(db)
    risk_svc = get_risk_service(db)

    question = request.question.lower()

    # Actualizar KPIs
    kpi_engine.update_kpis_from_metrics(request.organization_id)

    # Responder根据 la pregunta
    if "work orders" in question and "abiertas" in question:
        open_wos = wo_service.list_open(request.organization_id)
        return {
            "answer": f"Hay {len(open_wos)} Work Orders abiertas",
            "data": [{"id": wo.id, "title": wo.title, "status": wo.status} for wo in open_wos],
        }

    elif "bloqueadas" in question:
        blocked = wo_service.list_blocked(request.organization_id)
        return {
            "answer": f"Hay {len(blocked)} Work Orders bloqueadas",
            "data": [{"id": wo.id, "title": wo.title, "reason": wo.blocking_reason} for wo in blocked],
        }

    elif "kpi" in question and ("empeoró" in question or "peor" in question):
        kpis = kpi_svc.get_all(request.organization_id)
        declining = [k for k in kpis if k.history and len(k.history) > 1 and k.current_value < k.history[-1]["value"]]
        return {
            "answer": f"{len(declining)} KPIs han empeorado",
            "data": [{"name": k.name, "current": k.current_value, "previous": k.history[-1]["value"]} for k in declining],
        }

    elif "riesgos" in question and ("aparecieron" in question or "nuevos" in question):
        risks = risk_svc.get_active(request.organization_id)
        return {
            "answer": f"Hay {len(risks)} riesgos activos",
            "data": [{"title": r.title, "severity": r.severity, "status": r.status} for r in risks],
        }

    elif "dependencias" in question or "detenidas" in question:
        blocked = wo_service.list_blocked(request.organization_id)
        return {
            "answer": f"{len(blocked)} Work Orders están detenidas por dependencias o bloqueos",
            "data": [{"id": wo.id, "title": wo.title, "reason": wo.blocking_reason} for wo in blocked],
        }

    else:
        # Respuesta genérica con resumen
        metrics = kpi_engine.calculate_from_work_orders(request.organization_id)
        return {
            "answer": f"Resumen: {metrics['total']} Work Orders, {metrics['completed']} completadas, {metrics['blocked']} bloqueadas, {metrics['overdue']} vencidas",
            "data": metrics,
        }


# ============================================================
# Meetings
# ============================================================

@router.post("/meetings")
async def create_meeting(
    request: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea una reunión."""
    require_organization(db, request.organization_id, current_user)
    service = get_meeting_service(db)
    meeting = service.create(
        organization_id=request.organization_id,
        title=request.title,
        participants=request.participants,
        agenda=request.agenda,
    )
    db.commit()
    return {"id": meeting.id, "title": meeting.title}


# ============================================================
# Health
# ============================================================

@router.get("/health")
async def oos_health():
    """Health check del OOS."""
    return {
        "status": "healthy",
        "version": "0.1.0-wo008",
    }
