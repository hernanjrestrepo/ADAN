"""La Sala de cada Nivel (2 a 7): misma conversación con el equipo que en el Nivel 1, con el guion, los entregables
y los indicadores del Nivel. ADÁN abre cada Nivel con la agenda y lo cierra con el fundador."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.ai.usage import usage_scope
from app.api.v1.nivel1 import get_llm, research_later
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.core.ratelimit import llm_user
from app.levels.scripts import script_for
from app.models.models import Level, Message, NivelStatus, Project, User
from app.nivel1 import timeline
from app.nivel1.service import Nivel1Service, auto_register_evidence, discovery_progress
from app.scoring import engine
from app.scoring import service as scoring

router = APIRouter(prefix="/nivel", tags=["niveles"])


class ChatBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)


class CloseBody(BaseModel):
    reason: str = Field("", max_length=2000)


def _level(db: Session, company_id: str, n: int, user: User) -> tuple[Project, Level]:
    if not 2 <= n <= 7:
        raise HTTPException(status_code=404, detail="Ese Nivel no existe en la Sala")
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    level = db.query(Level).filter(Level.project_id == project.id, Level.number == n).first()
    if project is None or level is None:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    return project, level


def _info(n: int) -> dict:
    s = script_for(n)
    return {"number": s.number, "name": s.name, "goal": s.goal, "deliverables": list(s.deliverables),
            "kpis": list(s.kpis), "team": list(s.team), "board": s.board, "arena": s.arena,
            "topics": [{"id": t[0], "label": t[1]} for t in s.topics]}


def _welcome(db: Session, project: Project, n: int) -> None:
    """La agenda del Nivel: qué buscamos, qué vamos a entregar y quién acompaña (sin llamar al modelo)."""
    s = script_for(n)
    names = [timeline.TEAM[a][0] for a in s.team if a in timeline.TEAM and a != "ceo"]
    text = (f"🎯 **Bienvenido al Nivel {n}: {s.name}.** Aquí vamos a {s.goal}.\n\n"
            f"**Lo que vamos a entregar:** {'; '.join(s.deliverables)}.\n\n"
            f"**Cómo sabremos que vamos bien:** {'; '.join(s.kpis)}.\n\n"
            + (f"Te acompañan {', '.join(names[:-1]) + ' y ' + names[-1] if len(names) > 1 else names[0]}. " if names else "")
            + ("Al final sesionará el Board. " if s.board else "")
            + ("En este Nivel también pasas por La Arena con cuatro inversionistas. " if s.arena else "")
            + f"\n\nEmpecemos por lo primero: **{s.topics[0][1].lower()}** — {s.topics[0][2]}. ¿Qué tienes en mente?")
    timeline.post(db, project, text, agent="ceo", nivel=n, agenda=True)
    db.commit()


def _view(db: Session, project: Project, level: Level, n: int) -> dict:
    conv = timeline.conversation(db, project, n)
    messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at).all()
    return {"level": _info(n), "status": getattr(level.status, "value", level.status), "conversation_id": conv.id,
            "messages": [{"id": m.id, "role": m.role, "agent_name": m.agent_name, "content": m.content,
                          "created_at": m.created_at.isoformat(), "metadata_json": m.metadata_json} for m in messages],
            "discovery": discovery_progress(db, conv, project)}


@router.get("/{n}/{company_id}/status")
def status(n: int, company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project, level = _level(db, company_id, n, user)
    if level.status == NivelStatus.BLOCKED:
        return {"level": _info(n), "status": "blocked", "messages": [], "discovery": None, "conversation_id": None}
    conv = timeline.conversation(db, project, n)
    if db.query(Message).filter(Message.conversation_id == conv.id).count() == 0:
        _welcome(db, project, n)
    return _view(db, project, level, n)


@router.post("/{n}/{company_id}/chat")
async def chat(n: int, company_id: str, body: ChatBody, background: BackgroundTasks, db: Session = Depends(get_db),
               user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    project, level = _level(db, company_id, n, user)
    if level.status == NivelStatus.BLOCKED:
        raise HTTPException(status_code=409, detail=f"Primero cierra el Nivel {n - 1}.")
    service = Nivel1Service(llm, db)
    conv = timeline.conversation(db, project, n)
    with usage_scope(db, company_id, level=n):
        msg, conv = await service.chat(project, level, body.message.strip(), conv)
    auto_register_evidence(db, project, user, msg)
    pending = (msg.metadata_json or {}).get("investigando")
    if pending:
        background.add_task(research_later, db.get_bind(), llm, company_id, conv.id, pending["consulta"], user.id)
    return {"message": {"id": msg.id, "role": msg.role, "agent_name": msg.agent_name, "content": msg.content,
                        "created_at": msg.created_at.isoformat(), "metadata_json": msg.metadata_json},
            "conversation_id": conv.id}


@router.post("/{n}/{company_id}/cerrar")
def close(n: int, company_id: str, body: CloseBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """El fundador aprueba el cierre del Nivel. Si faltan temas, puede cerrarlo bajo su responsabilidad con un motivo:
    queda en el acta y baja la calificación del Nivel."""
    project, level = _level(db, company_id, n, user)
    if level.status == NivelStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Este Nivel ya está cerrado.")
    if level.status == NivelStatus.BLOCKED:
        raise HTTPException(status_code=409, detail=f"Primero cierra el Nivel {n - 1}.")
    conv = timeline.conversation(db, project, n)
    progress = discovery_progress(db, conv, project)
    missing = [t["label"] for t in progress["topics"] if t["estado"] not in ("respondido", "sin_dato")]
    reason = body.reason.strip()
    if missing and len(reason) < 10:
        raise HTTPException(status_code=409, detail="Faltan temas por cubrir: " + "; ".join(missing)
                            + ". Puedes cerrarlo bajo tu responsabilidad explicando por qué.")
    script = script_for(n)
    if missing and script.dimension:
        scoring.record_agent_inference(
            db, project, "ADÁN", dimension=script.dimension, polarity=engine.CONTRADICTS, confidence=min(90.0, 30.0 + 10 * len(missing)),
            claim=f"El fundador cerró el Nivel {n} con temas pendientes ({'; '.join(missing)}). Motivo: {reason[:300]}")
    level.status = NivelStatus.COMPLETED
    level.completed_at = datetime.now(timezone.utc)
    nxt = db.query(Level).filter(Level.project_id == project.id, Level.number == n + 1).first()
    if nxt is not None and nxt.status == NivelStatus.BLOCKED:
        nxt.status = NivelStatus.ACTIVE
    if reason:
        timeline.post(db, project, reason, role="user", nivel=n)
    timeline.post(db, project, (f"🏁 **Nivel {n} cerrado.** Entregables: {'; '.join(script.deliverables)}."
                                + (f" Quedó pendiente: {'; '.join(missing)} (afecta la calificación)." if missing else " ¡Buen trabajo!")
                                + (f" Seguimos con el Nivel {n + 1}." if nxt is not None else " Completaste los 7 Niveles. 🎉")),
                  agent="ceo", nivel=n, cierre=True)
    db.commit()
    return {"closed": True, "pending": missing, "next": n + 1 if nxt is not None else None}
