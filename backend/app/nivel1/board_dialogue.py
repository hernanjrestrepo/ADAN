"""Diálogo con el Board Room (AD-FUNC-02 §3, el cliente participa): después de la votación, el fundador puede hablarle
al Board en general o responderle a un especialista en su tema, para profundizar una explicación, aportar evidencia o
llegar a un consenso. Cada especialista sigue siendo exigente: solo cambia su voto si lo que le dicen trae datos
verificables, no por insistencia.

Cada intercambio se guarda como un documento nuevo (`board_dialogue`): no se reescribe la historia. El hilo es el de
la última sesión del Board; el siguiente Board lo lee como contexto.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.models.models import Document, Project
from app.nivel1.board_room import FAILURE_LENS, SPECIALISTS, VOTE_RULES, BoardConsensus

DOC_TYPE = "board_dialogue"
VOTES = ("PROCEED", "PIVOT", "STOP")
MAX_THREAD = 30

REPLY_SCHEMA = {
    "type": "object",
    "properties": {
        "replies": {"type": "array", "items": {"type": "object", "properties": {
            "agent": {"type": "string"}, "reply": {"type": "string"},
            "vote": {"type": "string", "enum": list(VOTES)}, "changed": {"type": "boolean"},
            "reason": {"type": "string"},
        }, "required": ["agent", "reply", "vote", "changed"]}},
        "ceo": {"type": "string"},
        "consensus": {"type": "string"},
    },
    "required": ["replies", "ceo"],
}


def _session_start(db: Session, project: Project) -> datetime | None:
    doc = db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "board_minutes") \
        .order_by(Document.created_at.desc()).first()
    return doc.created_at if doc else None


def thread(db: Session, project: Project) -> list[dict]:
    """Los intercambios desde la última sesión del Board, en orden."""
    start = _session_start(db, project)
    q = db.query(Document).filter(Document.project_id == project.id, Document.doc_type == DOC_TYPE)
    if start is not None:
        q = q.filter(Document.created_at >= start)
    out = []
    for d in q.order_by(Document.created_at.asc()).limit(MAX_THREAD).all():
        try:
            out.append(json.loads(d.content or "{}"))
        except json.JSONDecodeError:
            continue
    return out


def current_votes(consensus: BoardConsensus, turns: list[dict]) -> dict[str, str]:
    """El voto vigente de cada especialista: el de la sesión, actualizado por lo que cambió en el diálogo."""
    votes = {v.agent: v.vote for v in consensus.votes}
    for t in turns:
        for r in t.get("replies", []):
            if r.get("changed") and r.get("agent") in votes and r.get("vote") in VOTES:
                votes[r["agent"]] = r["vote"]
    return votes


def tally(votes: dict[str, str]) -> dict:
    yes = sum(1 for v in votes.values() if v == "PROCEED")
    return {"votes": votes, "proceed": yes, "total": len(votes),
            # Igual que en la sesión: avanzar exige 5 de 6 a favor
            "recommendation": "PROCEED" if yes >= 5 else ("STOP" if list(votes.values()).count("STOP") >= 3 else "PIVOT")}


def _transcript(turns: list[dict]) -> str:
    lines = []
    for t in turns[-8:]:
        target = f" (a {t['agent']})" if t.get("agent") else ""
        lines.append(f"Fundador{target}: {t.get('message', '')}")
        for r in t.get("replies", []):
            lines.append(f"{r.get('agent')}: {r.get('reply', '')}" + (f" [cambió su voto a {r['vote']}]" if r.get("changed") else ""))
        if t.get("ceo"):
            lines.append(f"CEO: {t['ceo']}")
    return "\n".join(lines)


def _board_state(consensus: BoardConsensus, votes: dict[str, str]) -> str:
    rows = []
    for v in consensus.votes:
        rows.append(
            f"- {v.agent} ({SPECIALISTS.get(v.agent, '')}): voto vigente {votes.get(v.agent, v.vote)}. "
            f"Justificación: {v.justification}. Preocupaciones: {'; '.join(v.key_concerns or [])}. "
            f"Cambiaría su voto si: {'; '.join(v.questions or [])}."
            + (f" Podría cerrar por: {v.failure_mode}." if v.failure_mode else "")
        )
    return (f"Decisión de la sesión: {consensus.decision} (score {consensus.score:.0f}, confianza {consensus.confidence:.0f} %).\n"
            f"Síntesis del CEO: {consensus.synthesis}\nVotos:\n" + "\n".join(rows))


def _system(agent: str | None) -> str:
    lenses = "\n".join(f"- {role}: {FAILURE_LENS.get(role, focus)}" for role, focus in SPECIALISTS.items())
    who = (f"Responde SOLO {agent}, en primera persona, sobre su especialidad." if agent else
           "Responden los 1 a 3 especialistas a los que más les toca lo que dijo el fundador; después el CEO modera.")
    return (
        "Eres el Board Room de ADÁN conversando con el fundador después de votar. Cada especialista habla desde su área "
        "y con los datos de ESTA empresa. Explica con claridad a alguien que no sabe del tema: por qué votó así, qué "
        "evidencia concreta pide (qué medir, con quién, cuántos) y cómo conseguirla rápido y barato. "
        f"{who}\n"
        "Regla de voto: " + VOTE_RULES + " Un especialista solo cambia su voto (`changed`: true) si el fundador aporta "
        "datos o evidencia verificable que resuelve su preocupación; la insistencia o las opiniones no cambian votos. "
        "Si no cambia, `vote` es su voto vigente.\n"
        "Lentes de falla de cada especialista:\n" + lenses + "\n"
        "`reply`: máximo 120 palabras, directo y respetuoso. `ceo`: máximo 80 palabras: qué quedó claro, en qué hay "
        "consenso y qué falta para avanzar. `consensus`: una frase con el acuerdo alcanzado o 'sin consenso todavía'. "
        "Español."
    )


async def reply(llm: LLMAdapter, db: Session, project: Project, consensus: BoardConsensus, brief: str,
                message: str, agent: str | None) -> dict:
    if agent is not None and agent not in SPECIALISTS:
        raise ValueError("Ese miembro no está en el Board")
    turns = thread(db, project)
    votes = current_votes(consensus, turns)
    prompt = (
        f"Lo que se sabe de la empresa:\n{brief[:6000]}\n\n{_board_state(consensus, votes)}\n\n"
        + (f"Conversación hasta ahora:\n{_transcript(turns)}\n\n" if turns else "")
        + (f"El fundador le responde a {agent}: " if agent else "El fundador le dice al Board: ") + message
    )
    response = await llm.chat_json([LLMMessage(role="system", content=_system(agent)),
                                    LLMMessage(role="user", content=prompt)], REPLY_SCHEMA, temperature=0.4,
                                   max_tokens=1600)
    data = response.parsed if isinstance(response.parsed, dict) else {}
    replies = []
    for r in data.get("replies") or []:
        name = r.get("agent")
        if name not in SPECIALISTS or (agent and name != agent):
            continue
        vote = r.get("vote") if r.get("vote") in VOTES else votes.get(name, "PIVOT")
        changed = bool(r.get("changed")) and vote != votes.get(name)
        replies.append({"agent": name, "reply": str(r.get("reply", ""))[:1500], "vote": vote if changed else votes.get(name),
                        "changed": changed, "reason": str(r.get("reason", ""))[:300] if changed else ""})
    if not replies and not data.get("ceo"):
        raise RuntimeError("El Board no pudo responder ahora; intenta de nuevo en un momento.")
    turn = {"message": message, "agent": agent, "replies": replies, "ceo": str(data.get("ceo", ""))[:1200],
            "consensus": str(data.get("consensus", ""))[:300], "at": datetime.now(timezone.utc).isoformat()}
    db.add(Document(project_id=project.id, title=f"Diálogo con el Board{f' ({agent})' if agent else ''}",
                    content=json.dumps(turn, ensure_ascii=False), doc_type=DOC_TYPE, origin="generated_by_adan"))
    db.commit()
    turns.append(turn)
    return {"turn": turn, "thread": turns, "tally": tally(current_votes(consensus, turns))}


def as_context(db: Session, project: Project) -> str:
    """Lo conversado con el Board en la última sesión, para que la siguiente lo tenga en cuenta."""
    turns = thread(db, project)
    return ("\n\nLo que el fundador conversó con el Board después de la última sesión:\n" + _transcript(turns)) if turns else ""
