"""Agentes por tiempo (WO-109): contratar, asignar trabajo, ejecutarlo con TEF y medirlo."""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.router import for_tier
from app.ai.usage import usage_scope
from app.hire.models import PERIOD_HOURS, AgentContract, AgentOffering, AgentWorkLog
from app.models.models import Company, User
from app.oos.models import Assignment, Organization, WorkOrder
from app.tef.interfaces import ToolContext

MAX_UNITS = {"hour": 200, "day": 60, "week": 26, "month": 12}

CATALOG = [
    {"code": "investigador", "name": "Investigador de Mercado", "role": "Investigación",
     "description": "Busca y resume información de mercado, competidores y tendencias para una pregunta concreta.",
     "skills": ["investigación de mercado", "análisis de competidores", "síntesis"], "tools": ["http_request"],
     "tier": "standard",
     "system_prompt": "Eres un investigador de mercado. Respondes con hallazgos concretos, citas la fuente de cada "
                      "dato y separas lo verificado de lo que es inferencia tuya."},
    {"code": "analista_financiero", "name": "Analista Financiero", "role": "Finanzas",
     "description": "Arma proyecciones, calcula márgenes, punto de equilibrio y escenarios.",
     "skills": ["proyecciones", "márgenes", "punto de equilibrio", "escenarios"], "tools": ["calculator"],
     "tier": "complex",
     "system_prompt": "Eres un analista financiero. Muestras cada supuesto, cada cálculo y el rango de "
                      "incertidumbre. Nunca presentas una cifra sin decir de dónde sale."},
    {"code": "redactor", "name": "Redactor Comercial", "role": "Marketing",
     "description": "Escribe textos comerciales: propuestas de valor, correos, publicaciones y guiones.",
     "skills": ["copywriting", "propuestas de valor", "correos comerciales"], "tools": [],
     "tier": "standard",
     "system_prompt": "Eres un redactor comercial. Escribes claro, concreto y en el tono de la marca. Entregas "
                      "el texto listo para usar y, si aplica, dos variantes."},
    {"code": "asistente_operaciones", "name": "Asistente de Operaciones", "role": "Operaciones",
     "description": "Ordena procesos, checklists, cronogramas y tareas operativas del día a día.",
     "skills": ["procesos", "checklists", "cronogramas"], "tools": ["calculator"],
     "tier": "fast",
     "system_prompt": "Eres un asistente de operaciones. Entregas listas accionables, con responsables y "
                      "fechas sugeridas, sin relleno."},
]


class HireError(ValueError):
    """La contratación o la tarea no es válida en el estado actual."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def ensure_catalog(db: Session) -> None:
    known = {code for (code,) in db.query(AgentOffering.code).all()}
    for item in CATALOG:
        if item["code"] not in known:
            db.add(AgentOffering(**item))
    db.flush()


def offerings(db: Session) -> list[AgentOffering]:
    ensure_catalog(db)
    return db.query(AgentOffering).filter(AgentOffering.active.is_(True)).order_by(AgentOffering.name).all()


def hire(db: Session, company: Company, user: User, offering_code: str, period: str, units: int) -> AgentContract:
    if period not in PERIOD_HOURS:
        raise HireError("El período es hora, día, semana o mes")
    if not 1 <= units <= MAX_UNITS[period]:
        raise HireError(f"Para '{period}' se contratan entre 1 y {MAX_UNITS[period]} unidades")
    ensure_catalog(db)
    offering = db.query(AgentOffering).filter(AgentOffering.code == offering_code,
                                              AgentOffering.active.is_(True)).first()
    if offering is None:
        raise HireError("Ese agente no está en el catálogo")
    start = _now()
    span = {"hour": timedelta(days=30), "day": timedelta(days=units), "week": timedelta(weeks=units),
            "month": timedelta(days=30 * units)}[period]
    contract = AgentContract(company_id=company.id, offering_id=offering.id, period=period, units=units,
                             hours_capacity=float(PERIOD_HOURS[period] * units), starts_at=start,
                             ends_at=start + span, hired_by=user.id)
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def hours_used(db: Session, contract: AgentContract) -> float:
    seconds = sum(s for (s,) in db.query(AgentWorkLog.seconds).filter(AgentWorkLog.contract_id == contract.id).all())
    return round(seconds / 3600, 4)


def contract_state(db: Session, contract: AgentContract) -> str:
    if contract.status == "cancelled":
        return "cancelled"
    if _utc(contract.ends_at) < _now():
        return "expired"
    if hours_used(db, contract) >= contract.hours_capacity:
        return "exhausted"
    return "active"


def cancel(db: Session, contract: AgentContract) -> AgentContract:
    if contract.status == "cancelled":
        return contract
    contract.status = "cancelled"
    contract.cancelled_at = _now()
    db.commit()
    db.refresh(contract)
    return contract


def organization_for(db: Session, company: Company) -> Organization:
    """La organización del OOS de la Empresa: ahí viven las Work Orders de sus agentes."""
    org = db.query(Organization).filter(Organization.company_id == company.id).first()
    if org is None:
        org = Organization(company_id=company.id, name=company.name, industry=company.industry,
                           country=company.country)
        db.add(org)
        db.flush()
    return org


def assign_task(db: Session, company: Company, contract: AgentContract, title: str, description: str) -> WorkOrder:
    state = contract_state(db, contract)
    if state != "active":
        raise HireError(f"El contrato no está activo ({state})")
    offering = db.get(AgentOffering, contract.offering_id)
    org = organization_for(db, company)
    wo = WorkOrder(organization_id=org.id, title=title, description=description, status="assigned",
                   assigned_to=contract.id, assigned_to_name=offering.name, priority="medium",
                   metadata_json={"source": "hire", "contract_id": contract.id, "offering": offering.code})
    db.add(wo)
    db.flush()
    db.add(Assignment(work_order_id=wo.id, assigned_to=contract.id, assigned_to_name=offering.name,
                      assigned_to_type="agent", accepted_at=_now()))
    db.commit()
    db.refresh(wo)
    return wo


def contract_tasks(db: Session, contract: AgentContract) -> list[WorkOrder]:
    return db.query(WorkOrder).filter(WorkOrder.assigned_to == contract.id).order_by(WorkOrder.created_at.desc()).all()


def _tool_schema(tools: list[str]) -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["tool", "params", "reason"],
            "properties": {"tool": {"type": "string", "enum": [*tools, "none"]},
                           "params": {"type": "object"}, "reason": {"type": "string"}}}


async def run_task(db: Session, company: Company, user: User, contract: AgentContract, wo: WorkOrder,
                   llm: LLMAdapter, executor) -> AgentWorkLog:
    """El agente trabaja la tarea: decide si usa una herramienta de TEF, la usa y entrega.

    El tiempo real de trabajo se mide de punta a punta y descuenta de la capacidad contratada.
    """
    state = contract_state(db, contract)
    if state != "active":
        raise HireError(f"El contrato no está activo ({state})")
    if wo.status not in ("assigned", "in_progress"):
        raise HireError("La tarea ya fue entregada; revísala o asigna una nueva")
    offering = db.get(AgentOffering, contract.offering_id)
    agent = for_tier(llm, offering.tier)
    wo.status = "in_progress"
    wo.started_at = wo.started_at or datetime.utcnow()
    db.commit()

    feedback = (wo.metadata_json or {}).get("feedback") or []
    task = f"Empresa: {company.name} ({company.industry or 'sin industria'}, {company.country or 'sin país'}).\n" \
           f"Tarea: {wo.title}\n{wo.description or ''}"
    if feedback:
        task += "\n\nCorrecciones pedidas por el cliente en entregas anteriores:\n" + "\n".join(f"- {f}" for f in feedback)
    system = offering.system_prompt + " Respondes en español."
    started_at, start = _now(), time.monotonic()
    tools_used, outcome, result_text = [], "delivered", ""
    with usage_scope(db, company.id) as scope:
        try:
            context_extra = ""
            if offering.tools:
                plan = await agent.chat_json(
                    [LLMMessage(role="system", content=system + " Antes de responder decides si una herramienta "
                                "te ayuda; si no, eliges 'none'."),
                     LLMMessage(role="user", content=task)], _tool_schema(offering.tools), max_tokens=512)
                try:
                    choice = json.loads(plan.content)
                except ValueError:
                    choice = {"tool": "none"}
                if choice.get("tool") in offering.tools:
                    ctx = ToolContext(company_id=company.id, user_id=user.id, trace_id=str(uuid.uuid4()),
                                      metadata={"contract_id": contract.id, "work_order_id": wo.id})
                    res = await executor.execute(choice["tool"], choice.get("params") or {}, ctx, db=db)
                    tools_used.append({"tool": choice["tool"], "status": res.status})
                    context_extra = (f"\n\nResultado de la herramienta {choice['tool']} ({res.status}): "
                                     f"{json.dumps(res.output, ensure_ascii=False, default=str)[:4000] if res.output else res.error}")
            answer = await agent.chat([LLMMessage(role="system", content=system),
                                       LLMMessage(role="user", content=task + context_extra)], max_tokens=2048)
            result_text = answer.content.strip()
            if not result_text:
                raise HireError("El modelo no devolvió contenido")
        except Exception as exc:  # la falla también se registra: el cliente ve el intento
            outcome, result_text = "failed", f"No se pudo completar: {type(exc).__name__}"
        records = list(scope["records"])
    seconds = round(time.monotonic() - start, 3)
    log = AgentWorkLog(contract_id=contract.id, work_order_id=wo.id, started_at=started_at, seconds=seconds,
                       prompt_tokens=sum(r.input_tokens for r in records),
                       completion_tokens=sum(r.output_tokens for r in records),
                       cost_usd=round(sum(r.cost_usd for r in records), 6),
                       model=records[-1].model if records else None,
                       degraded=any(r.degraded for r in records), tools_used=tools_used, outcome=outcome)
    db.add(log)
    if outcome == "delivered":
        wo.result, wo.status, wo.progress = result_text, "review", 1.0
    else:
        wo.status, wo.blocking_reason = "assigned", result_text
    db.commit()
    db.refresh(log)
    return log


def review(db: Session, wo: WorkOrder, approve: bool, feedback: str | None) -> WorkOrder:
    """El cliente aprueba la entrega o la devuelve con correcciones (Patrón A: decide el cliente)."""
    if wo.status != "review":
        raise HireError("Solo se revisa una tarea entregada")
    if approve:
        wo.status, wo.completed_at = "completed", datetime.utcnow()
    else:
        if not feedback or len(feedback.strip()) < 5:
            raise HireError("Di qué hay que corregir")
        meta = dict(wo.metadata_json or {})
        meta["feedback"] = [*meta.get("feedback", []), feedback.strip()]
        wo.metadata_json, wo.status, wo.progress = meta, "assigned", 0.5
    db.commit()
    db.refresh(wo)
    return wo


def report(db: Session, contract: AgentContract) -> dict:
    """Reporte al cliente: horas contratadas y usadas, trabajo entregado y su costo de modelo."""
    logs = db.query(AgentWorkLog).filter(AgentWorkLog.contract_id == contract.id).order_by(AgentWorkLog.created_at).all()
    tasks = contract_tasks(db, contract)
    used = hours_used(db, contract)
    return {
        "contract_id": contract.id, "hours_capacity": contract.hours_capacity, "hours_used": used,
        "hours_left": round(max(0.0, contract.hours_capacity - used), 4), "state": contract_state(db, contract),
        "runs": len(logs), "delivered": sum(1 for lg in logs if lg.outcome == "delivered"),
        "failed": sum(1 for lg in logs if lg.outcome == "failed"),
        "tasks": {s: sum(1 for t in tasks if t.status == s) for s in ("assigned", "in_progress", "review", "completed")},
        "model_cost_usd": round(sum(lg.cost_usd for lg in logs), 6),
        "tokens": sum(lg.prompt_tokens + lg.completion_tokens for lg in logs),
        "degraded_runs": sum(1 for lg in logs if lg.degraded),
        "tools": sorted({t["tool"] for lg in logs for t in (lg.tools_used or [])}),
        "price_note": contract.price_note,
    }
