"""Los entregables de cada Nivel como documentos de la Biblioteca.

Al cerrar un Nivel, ADAN redacta cada entregable (Lienzo de Propuesta de Valor, Plan de lanzamiento, Precios
finales…) con lo que se habló y se acordó, separando datos de supuestos. Para los Niveles que se cerraron antes
de que existiera esto, la Biblioteca los prepara bajo pedido. Corre en segundo plano con su propia sesión.
"""
from __future__ import annotations

import logging
import re

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.usage import usage_scope
from app.levels.scripts import script_for
from app.models.models import Document, Level, NivelStatus, Project
from app.nivel1 import memoria, timeline

logger = logging.getLogger(__name__)
DOC_TYPE = "entregable"

# Sección de la Biblioteca según de qué trata el entregable
_SECTIONS = (
    ("numeros", re.compile(r"flujo|caja|precio|econom|capital|tam|cac|cotizaci|organigrama|indicador", re.I)),
    ("legal", re.compile(r"legal|contrato|estatut", re.I)),
    ("marca", re.compile(r"marca|logo|pitch", re.I)),
)

WRITER = (
    "Eres el equipo de ADAN redactando un entregable formal de la empresa del fundador. Usa SOLO lo que se habló y "
    "se acordó (memoria y conversación): no inventes cifras; si un dato no está, márcalo como «supuesto» o "
    "«pendiente de validar» y di cómo validarlo. Formato Markdown limpio y profesional: título, resumen de 2 líneas "
    "y las secciones propias de ese entregable (por ejemplo, el Lienzo de Propuesta de Valor con trabajos, dolores, "
    "alegrías, productos, aliviadores y creadores; el Plan Bullseye con canales, prueba, costo y meta). Español, "
    "máximo 600 palabras."
)


def section_of(title: str) -> str:
    for section, pattern in _SECTIONS:
        if pattern.search(title):
            return section
    return "estrategia"


def level_of(title: str) -> int | None:
    m = re.match(r"Nivel (\d)", title or "")
    return int(m.group(1)) if m else None


def missing(db: Session, project: Project) -> dict[int, list[str]]:
    """Entregables que aún no están en la Biblioteca, por cada Nivel cerrado."""
    have = {d.title for d in db.query(Document.title).filter(Document.project_id == project.id,
                                                             Document.doc_type == DOC_TYPE).all()}
    out: dict[int, list[str]] = {}
    for lv in db.query(Level).filter(Level.project_id == project.id, Level.status == NivelStatus.COMPLETED).all():
        todo = [d for d in script_for(lv.number).deliverables if f"Nivel {lv.number} · {d}" not in have]
        if todo:
            out[lv.number] = todo
    return out


def _transcript(db: Session, project: Project, n: int, limit: int = 40) -> str:
    conv = timeline.conversation(db, project, n)
    from app.models.models import Message

    msgs = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.desc()).limit(limit).all()
    return "\n".join(f"{'Fundador' if m.role == 'user' else (m.agent_name or 'ADAN')}: {m.content[:600]}" for m in reversed(msgs))


async def build_level(llm: LLMAdapter, db: Session, project: Project, n: int, only: list[str] | None = None) -> int:
    script = script_for(n)
    todo = only if only is not None else missing(db, project).get(n, [])
    if not todo:
        return 0
    context = memoria.context(db, project, " ".join(script.deliverables), n)[:6000]
    talk = _transcript(db, project, n)[:9000]
    made = 0
    for name in todo:
        try:
            resp = await llm.chat([
                LLMMessage("system", WRITER),
                LLMMessage("user", f"Entregable: «{name}» del Nivel {n} ({script.name}: {script.goal}).\n"
                                   f"Método del Nivel: {script.method}\n\n{context}\n\nConversación del Nivel:\n{talk}"),
            ], max_tokens=2500)
        except Exception:  # noqa: BLE001 - el siguiente entregable se intenta igual
            logger.exception("No se pudo redactar el entregable %s", name)
            continue
        text = (resp.content or "").strip()
        if not text or resp.metadata.get("degraded"):
            continue
        db.add(Document(project_id=project.id, title=f"Nivel {n} · {name}"[:255], content=text, doc_type=DOC_TYPE,
                        origin="generated_by_adan"))
        db.commit()
        made += 1
    return made


async def build_later(bind, llm: LLMAdapter, company_id: str, levels: list[int] | None = None) -> None:
    """Prepara en segundo plano los entregables que faltan (de un Nivel o de todos los cerrados)."""
    from app.ai.router import for_tier

    llm = for_tier(llm, "standard")  # sin nivel, el adaptador va al modelo local de respaldo
    db = Session(bind=bind)
    try:
        project = db.query(Project).filter(Project.company_id == company_id).first()
        if project is None:
            return
        # Primero la memoria al día (acuerdos sin contradicciones y ficha): los entregables salen de ahí
        try:
            await memoria.consolidate(llm, db, project)
        except Exception:  # noqa: BLE001
            logger.exception("No se pudo consolidar la memoria antes de los entregables")
        pending = missing(db, project)
        for n in sorted(pending):
            if levels and n not in levels:
                continue
            with usage_scope(db, company_id, level=n):
                await build_level(llm, db, project, n)
    except Exception:  # noqa: BLE001
        logger.exception("La preparación de entregables falló")
    finally:
        db.close()
