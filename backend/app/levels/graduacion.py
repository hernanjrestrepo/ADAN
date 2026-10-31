"""El cierre de todo el proceso: la graduación al cerrar el Nivel 7 y el modo continuo.

Al graduarse, ADAN: 1) consolida la memoria, 2) convoca la sesión final del Board (¿la empresa está lista para operar
y crecer?), 3) escribe el Libro de la Empresa (la ficha, lo que se construyó en cada Nivel, las decisiones, los
riesgos asumidos y el plan de 90 días con sus indicadores) y 4) emite el certificado. Después sigue el modo
continuo: el fundador reporta cada mes sus indicadores, Camila los compara con el plan y cada trimestre sesiona
el Board.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.router import for_tier
from app.ai.usage import usage_scope
from app.levels.scripts import script_for
from app.models.models import Company, Document, Level, NivelStatus, Project
from app.nivel1 import memoria, timeline

logger = logging.getLogger(__name__)
GRAD_DOC = "graduacion"
BOOK_DOC = "libro_empresa"
CHECKIN_DOC = "seguimiento"

PLAN_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["resumen_ejecutivo", "plan_90_dias", "kpis", "frase"],
    "properties": {
        "resumen_ejecutivo": {"type": "string"},
        "plan_90_dias": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["periodo", "objetivo", "acciones"],
            "properties": {"periodo": {"type": "string"}, "objetivo": {"type": "string"},
                           "acciones": {"type": "array", "items": {"type": "string"}}}}},
        "kpis": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["nombre", "meta", "unidad", "frecuencia"],
            "properties": {"nombre": {"type": "string"}, "meta": {"type": "number"}, "unidad": {"type": "string"},
                           "frecuencia": {"type": "string"}}}},
        "frase": {"type": "string"},
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _doc(db: Session, project: Project, kind: str) -> Document | None:
    return db.query(Document).filter(Document.project_id == project.id, Document.doc_type == kind) \
        .order_by(Document.created_at.desc()).first()


def status(db: Session, project: Project) -> dict:
    level7 = db.query(Level).filter(Level.project_id == project.id, Level.number == 7).first()
    grad = _doc(db, project, GRAD_DOC)
    data = json.loads(grad.content) if grad and grad.content else {}
    book = _doc(db, project, BOOK_DOC)
    checkins = _doc(db, project, CHECKIN_DOC)
    return {"nivel7_cerrado": bool(level7 and level7.status == NivelStatus.COMPLETED),
            "graduada": data.get("estado") == "lista", "estado": data.get("estado") or "pendiente", **data,
            "libro": {"id": book.id, "markdown": book.content} if book else None,
            "seguimientos": json.loads(checkins.content).get("meses", []) if checkins and checkins.content else []}


def _save(db: Session, project: Project, kind: str, title: str, content: str) -> Document:
    doc = _doc(db, project, kind)
    if doc is None:
        doc = Document(project_id=project.id, title=title, doc_type=kind, origin="generated_by_adan", content=content)
        db.add(doc)
    else:
        doc.title, doc.content = title, content
    db.commit()
    db.refresh(doc)
    return doc


def _book(company: Company, ficha: dict, plan: dict, board, delivered: list[Document], agreements: list[dict]) -> str:
    lines = [f"# Libro de la Empresa — {company.name}", "", f"_Construido con ADAN · graduación del {datetime.now():%d/%m/%Y}_",
             "", "## Resumen ejecutivo", plan.get("resumen_ejecutivo", "")]
    if ficha:
        lines += ["", "## Ficha de la empresa", ""] + [f"- **{k}:** {v}" for k, v in ficha.items()]
    lines += ["", "## Lo que se construyó en cada Nivel"]
    for n in range(1, 8):
        s = script_for(n)
        docs = [d for d in delivered if d.title.startswith(f"Nivel {n} ·")]
        lines += ["", f"### Nivel {n} · {s.name}", f"_{s.goal}_"]
        lines += [f"- {d.title.split(' · ', 1)[1]}" for d in docs] or ["- (sin entregables guardados)"]
    decided = [a for a in agreements if a.get("tipo") == "decidido"]
    if decided:
        lines += ["", "## Decisiones clave"] + [f"- {a['texto']} (Nivel {a.get('nivel', '?')})" for a in decided[-30:]]
    if board is not None:
        lines += ["", "## Sesión final del Board",
                  f"**Resultado:** {board.decision} · preparación {board.score:.0f}/100", "", board.synthesis or ""]
        if board.assumed_risks:
            lines += ["", "**Riesgos que el fundador decidió asumir:**"] + [f"- {r}" for r in board.assumed_risks]
        if board.blockers:
            lines += ["", "**Por resolver:**"] + [f"- {b}" for b in board.blockers]
        if board.post_launch:
            lines += ["", "**Para medir:**"] + [f"- {p}" for p in board.post_launch]
    lines += ["", "## Plan de 90 días"]
    for step in plan.get("plan_90_dias", []):
        lines += ["", f"### {step.get('periodo')}: {step.get('objetivo')}"] + [f"- {a}" for a in step.get("acciones", [])]
    if plan.get("kpis"):
        lines += ["", "## Indicadores del modo continuo", "", "| Indicador | Meta | Unidad | Frecuencia |", "|---|---|---|---|"]
        lines += [f"| {k['nombre']} | {k['meta']} | {k['unidad']} | {k['frecuencia']} |" for k in plan["kpis"]]
    lines += ["", "---", "ADAN te acompaña en modo continuo: reporta tus indicadores cada mes y el Board sesiona cada trimestre."]
    return "\n".join(lines)


async def graduate(llm: LLMAdapter, db: Session, project: Project, company: Company) -> dict:
    from app.nivel1.service import Nivel1Service

    _save(db, project, GRAD_DOC, "Graduación", json.dumps({"estado": "preparando", "inicio": _now()}))
    service = Nivel1Service(llm, db)
    await service.refresh_memory(project, max_age_hours=0)
    board = None
    try:
        board = await service.run_board_room(project, company, client_question=(
            "Graduación: la empresa completó los 7 Niveles. ¿Está lista para operar y crecer? ¿Qué debe vigilar en "
            "los próximos 90 días?"), level_number=7)
        timeline.board_session(db, project, board, nivel=7)
        db.commit()
    except Exception:  # noqa: BLE001 - sin Board final igual se gradúa; queda escrito en el libro
        logger.exception("La sesión final del Board falló")
    mem = memoria.load(db, project)
    delivered = db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "entregable") \
        .order_by(Document.title).all()
    context = memoria.context(db, project, "plan crecimiento indicadores metas", 7)[:9000]
    resp = await for_tier(llm, "standard").chat_json([
        LLMMessage("system", (
            "Eres ADAN cerrando el proceso de creación de la empresa con el fundador. Con la memoria (la ficha y los "
            "acuerdos mandan) y el resultado del Board escribe: `resumen_ejecutivo` (máximo 180 palabras: qué empresa "
            "quedó construida, para quién, cómo gana dinero y su estado), `plan_90_dias` (3 periodos: días 1-30, "
            "31-60 y 61-90, cada uno con objetivo y 3 a 5 acciones concretas), `kpis` (4 a 6 indicadores medibles "
            "con meta numérica coherente con la ficha, unidad y frecuencia mensual) y `frase` (una frase corta de "
            "celebración para el certificado). No inventes cifras fuera de la ficha.")),
        LLMMessage("user", context + (f"\n\nBoard final: {board.decision}. {board.synthesis}" if board else "")),
    ], PLAN_SCHEMA, temperature=0.4, max_tokens=3500)
    plan = resp.parsed if isinstance(resp.parsed, dict) and not resp.metadata.get("degraded") else {}
    book = _save(db, project, BOOK_DOC, f"Libro de la Empresa — {company.name}",
                 _book(company, mem.get("ficha", {}), plan, board, delivered, mem.get("acuerdos", [])))
    data = {"estado": "lista", "fecha": _now(), "certificado": f"ADAN-{uuid.uuid4().hex[:8].upper()}",
            "frase": plan.get("frase") or f"{company.name} completó los 7 Niveles de ADAN.",
            "kpis": plan.get("kpis", []), "board": {"decision": board.decision, "preparacion": round(board.score)} if board else None,
            "libro_id": book.id}
    _save(db, project, GRAD_DOC, "Graduación", json.dumps(data, ensure_ascii=False))
    timeline.post(db, project, (f"🎓 **¡{company.name} se graduó de ADAN!** Completaste los 7 Niveles. Te dejé el "
                                "**Libro de la Empresa** con todo lo construido y el plan de 90 días, y tu certificado. "
                                "Desde hoy seguimos en **modo continuo**: cada mes me cuentas tus indicadores y cada "
                                "trimestre sesiona el Board."), agent="ceo", nivel=7, graduacion=True,
                  reaccion={"agente": "ceo", "emocion": "celebrando", "frase": "¡Nos graduamos!"})
    db.commit()
    return data


async def graduate_later(bind, llm: LLMAdapter, company_id: str) -> None:
    db = Session(bind=bind)
    try:
        project = db.query(Project).filter(Project.company_id == company_id).first()
        company = db.get(Company, company_id)
        if project is None or company is None:
            return
        with usage_scope(db, company_id, level=7):
            await graduate(llm, db, project, company)
    except Exception:  # noqa: BLE001
        logger.exception("La graduación falló")
        try:
            _save(db, project, GRAD_DOC, "Graduación", json.dumps({"estado": "error", "fecha": _now()}))
        except Exception:  # noqa: BLE001
            pass
    finally:
        db.close()


async def check_in(llm: LLMAdapter, db: Session, project: Project, values: dict[str, float], note: str) -> dict:
    """Modo continuo: el fundador reporta el mes; Camila compara con la meta y propone el ajuste."""
    grad = json.loads((_doc(db, project, GRAD_DOC).content or "{}")) if _doc(db, project, GRAD_DOC) else {}
    kpis = {k["nombre"]: k for k in grad.get("kpis", [])}
    lines = [f"- {name}: real {value} vs meta {kpis.get(name, {}).get('meta', '?')} {kpis.get(name, {}).get('unidad', '')}"
             for name, value in values.items()]
    resp = await for_tier(llm, "standard").chat([
        LLMMessage("system", (
            "Eres Camila, CFO de ADAN, en el seguimiento mensual del modo continuo. Compara lo real con la meta, "
            "celebra lo que va bien, señala lo que se desvía y propone 2 acciones concretas para el próximo mes. "
            "Cálida y directa, máximo 120 palabras.")),
        LLMMessage("user", "Indicadores del mes:\n" + "\n".join(lines) + (f"\nNota del fundador: {note}" if note else "")
                   + "\n\n" + memoria.context(db, project, "metas indicadores", 7)[:3000]),
    ], max_tokens=900)
    reading = (resp.content or "").strip()
    doc = _doc(db, project, CHECKIN_DOC)
    data = json.loads(doc.content) if doc and doc.content else {"meses": []}
    entry = {"fecha": _now(), "valores": values, "nota": note[:500], "lectura": reading}
    data["meses"].append(entry)
    _save(db, project, CHECKIN_DOC, "Seguimiento del modo continuo", json.dumps(data, ensure_ascii=False))
    if reading:
        timeline.post(db, project, f"📈 **Seguimiento del mes.**\n\n{reading}", agent="cfo", nivel=7, seguimiento=True)
        db.commit()
    return entry
