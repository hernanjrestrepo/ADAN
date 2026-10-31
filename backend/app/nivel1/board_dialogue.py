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


def _system(agent: str | None, objectors: list[str]) -> str:
    lenses = "\n".join(f"- {role}: {FAILURE_LENS.get(role, focus)}" for role, focus in SPECIALISTS.items())
    who = (f"Responde SOLO {agent}, en primera persona, sobre su especialidad." if agent else
           "Responden los especialistas a los que les toca lo que dijo el fundador. Si el fundador está respondiendo "
           "a las objeciones del Board, responde CADA especialista que votó en contra ("
           + ", ".join(objectors or ["los que objetaron"]) + "), uno por uno, diciendo si su explicación le basta o "
           "qué le falta exactamente. Después el CEO modera.")
    return (
        "Eres el Board Room de ADAN conversando con el fundador después de votar. Cada especialista habla desde su área "
        "y con los datos de ESTA empresa. Explica con claridad a alguien que no sabe del tema: por qué votó así, qué "
        "evidencia concreta pide (qué medir, con quién, cuántos) y cómo conseguirla rápido y barato. "
        f"{who}\n"
        "Regla de voto: " + VOTE_RULES + " Un especialista solo cambia su voto (`changed`: true) si el fundador aporta "
        "datos o evidencia verificable que resuelve su preocupación; la insistencia o las opiniones no cambian votos. "
        "Si no cambia, `vote` es su voto vigente.\n"
        "Lentes de falla de cada especialista:\n" + lenses + "\n"
        "`agent` debe ser exactamente uno de: " + ", ".join(SPECIALISTS) + ". `reply`: máximo 120 palabras, directo y "
        "respetuoso, sobre lo que dijo el fundador (nunca solo el nombre de la empresa). `ceo`: 2 a 4 frases: qué quedó "
        "claro, en qué hay consenso y qué falta para avanzar; recuerda que si el fundador no tiene más que aportar puede "
        "decidir continuar bajo su responsabilidad. `consensus`: una frase con el acuerdo o 'sin consenso todavía'. "
        "Español."
    )


def _clean_replies(raw: list, agent: str | None, votes: dict[str, str]) -> list[dict]:
    names = {k.lower(): k for k in SPECIALISTS}
    out = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        name = names.get(str(r.get("agent", "")).strip().lower())
        text = str(r.get("reply", "")).strip()
        if not name or (agent and name != agent) or len(text) < 15:
            continue
        vote = r.get("vote") if r.get("vote") in VOTES else votes.get(name, "PIVOT")
        changed = bool(r.get("changed")) and vote != votes.get(name)
        out.append({"agent": name, "reply": text[:1500], "vote": vote if changed else votes.get(name),
                    "changed": changed, "reason": str(r.get("reason", ""))[:300] if changed else ""})
    return out


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
    objectors = [a for a, v in votes.items() if v != "PROCEED"]
    msgs = [LLMMessage(role="system", content=_system(agent, objectors)), LLMMessage(role="user", content=prompt)]
    data, replies = {}, []
    for attempt in range(2):
        response = await llm.chat_json(msgs, REPLY_SCHEMA, temperature=0.4 + 0.2 * attempt, max_tokens=3000)
        data = response.parsed if isinstance(response.parsed, dict) else {}
        replies = _clean_replies(data.get("replies") or [], agent, votes)
        if replies or len(str(data.get("ceo", "")).strip()) >= 40:
            break
        # Respuesta vacía o sin sentido (p. ej., solo el nombre de la empresa): se pide de nuevo, más claro
        msgs = msgs + [LLMMessage(role="user", content=(
            "[Nota interna: tu respuesta llegó vacía. Responde al fundador: cada especialista que objetó, en "
            "`replies`, y el CEO en 2 a 4 frases.]"))]
    else:
        raise RuntimeError("El Board no pudo responder bien esta vez; intenta de nuevo en un momento.")
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


def continue_anyway(db: Session, project: Project, consensus: BoardConsensus, reason: str) -> dict:
    """El fundador decide seguir aunque el Board no aprobó. ADAN no lo bloquea: deja constancia de las objeciones que
    quedan abiertas y de su motivo, y eso entra como inferencia en contra que baja la calificación (Problem Score)."""
    from app.scoring import service as scoring
    from app.scoring import engine

    turns = thread(db, project)
    votes = current_votes(consensus, turns)
    open_objections = [f"{v.agent}: {v.justification}" for v in consensus.votes if votes.get(v.agent) != "PROCEED"]
    record = {"reason": reason, "open_objections": open_objections, "votes": votes,
              "at": datetime.now(timezone.utc).isoformat()}
    db.add(Document(project_id=project.id, title="El fundador continúa bajo su responsabilidad",
                    content=json.dumps(record, ensure_ascii=False), doc_type="board_override", origin="generated_by_adan"))
    db.commit()
    penalty = min(90.0, 40.0 + 10.0 * len(open_objections))
    scoring.record_agent_inference(
        db, project, "Board Room", dimension="problem", polarity=engine.CONTRADICTS, confidence=penalty,
        claim=(f"El fundador decidió continuar pese a {len(open_objections)} objeción(es) abiertas del Board"
               + (f": {'; '.join(o[:120] for o in open_objections)}" if open_objections else "") + f". Motivo: {reason[:300]}"))
    return {"recorded": True, "open_objections": open_objections, "penalty_confidence": penalty}
