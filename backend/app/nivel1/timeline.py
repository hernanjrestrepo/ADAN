"""Una sola sala: la conversación del Nivel 1 es la línea de tiempo de todo lo que pasa. Lo que dicen los
especialistas, las sesiones del Board Room y La Arena quedan como mensajes de la misma conversación, cada uno con
quién habla y en qué escena (oficina, board o arena), para que la oficina 3D se mueva a ese espacio."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.models import Card, CardStatus, Conversation, Level, Message, Project

# Quién es quién en el equipo (los mismos personajes de la oficina)
TEAM = {
    "ceo": ("ADÁN", "CEO"), "cto": ("Mateo", "CTO"), "cfo": ("Camila", "CFO"), "cmo": ("Santiago", "CMO"),
    "legal": ("Lucía", "Legal"), "producto": ("Andrés", "Producto"), "operaciones": ("Sofía", "Operaciones"),
    "csi": ("Orión", "CSI"), "eva": ("Eva", "EVA"), "investigador": ("Iris", "Investigadora"), "analista": ("Teo", "Analista"),
    "genexis": ("Forja", "Genexis"),
}
ROLE_TO_ID = {"CTO": "cto", "CFO": "cfo", "CMO": "cmo", "Legal": "legal", "Producto": "producto", "Operaciones": "operaciones"}


def label(agent_id: str) -> str:
    name, role = TEAM.get(agent_id, TEAM["ceo"])
    return name if agent_id == "ceo" else f"{name} · {role}"


def conversation(db: Session, project: Project, nivel: int = 1) -> Conversation:
    kind = "pain_discovery" if nivel == 1 else f"nivel{nivel}"
    card = db.query(Card).filter(Card.project_id == project.id, Card.card_type == kind).first()
    if card is None:
        level = db.query(Level).filter(Level.project_id == project.id, Level.number == nivel).first()
        card = Card(project_id=project.id, level_id=level.id, title="Descubrimiento del Dolor" if nivel == 1 else f"Nivel {nivel}",
                    description="¿Qué problema real resuelve tu empresa?", card_type=kind,
                    status=CardStatus.ACTIVE)
        db.add(card)
        db.flush()
    conv = db.query(Conversation).filter(Conversation.card_id == card.id).first()
    if conv is None:
        conv = Conversation(card_id=card.id, title="Conversación de Descubrimiento")
        db.add(conv)
        db.flush()
    return conv


def post(db: Session, project: Project, content: str, *, agent: str = "ceo", role: str = "assistant",
         scene: str = "oficina", nivel: int = 1, **meta) -> Message:
    msg = Message(conversation_id=conversation(db, project, nivel).id, role=role,
                  agent_name=None if role == "user" else label(agent), content=content,
                  metadata_json={"agente": agent, "escena": scene, **meta})
    db.add(msg)
    return msg


def board_session(db: Session, project: Project, consensus, nivel: int = 1) -> None:
    """La sesión del Board, contada en la conversación: abre el CEO, vota cada especialista y cierra el CEO."""
    opening = "🏛️ **Abrimos sesión del Board Room.**"
    if consensus.objective:
        opening += f"\n\n**Objetivo:** {consensus.objective}"
    if consensus.decision_at_stake:
        opening += f"\n\n**En juego:** {consensus.decision_at_stake}"
    post(db, project, opening, agent="ceo", scene="board", nivel=nivel)
    for v in consensus.votes:
        text = f"**{ {'PROCEED': 'A favor', 'PIVOT': 'Pivotar', 'STOP': 'Detener'}.get(v.vote, v.vote) }.** {v.justification}"
        if v.failure_mode:
            text += f"\n\n⚠️ Podría cerrar por: {v.failure_mode}"
        if v.questions:
            text += "\n\nCambiaría mi voto si: " + "; ".join(v.questions)
        post(db, project, text, agent=ROLE_TO_ID.get(v.agent, "ceo"), scene="board", voto=v.vote,
             abogado_del_diablo=bool(getattr(v, "devils_advocate", False)), nivel=nivel)
    synthesis = f"**Decisión del Board: {consensus.decision}** (score {consensus.score:.0f}/100, confianza {consensus.confidence:.0f} %).\n\n{consensus.synthesis}"
    if consensus.evidence_requests:
        synthesis += "\n\n**Lo que el Board pide:** " + "; ".join(consensus.evidence_requests)
    synthesis += ("\n\nPuedes responderle aquí al Board (a todos o a uno: «Camila, …»). Si no tienes más que aportar, "
                  "puedes continuar bajo tu responsabilidad.")
    post(db, project, synthesis, agent="ceo", scene="board", decision=consensus.decision, nivel=nivel)
    db.commit()


def board_turn(db: Session, project: Project, turn: dict, nivel: int = 1) -> None:
    post(db, project, turn["message"], role="user", scene="board", nivel=nivel)
    for r in turn.get("replies", []):
        text = r["reply"] + (f"\n\n✅ Cambio mi voto a **{r['vote']}**: {r['reason']}" if r.get("changed") else "")
        post(db, project, text, agent=ROLE_TO_ID.get(r["agent"], "ceo"), scene="board", voto=r.get("vote"), nivel=nivel)
    if turn.get("ceo"):
        post(db, project, turn["ceo"] + (f"\n\n_Consenso: {turn['consensus']}_" if turn.get("consensus") else ""),
             agent="ceo", scene="board", nivel=nivel)
    db.commit()


def arena_questions(db: Session, project: Project, session: dict, nivel: int = 1) -> None:
    post(db, project, "🥊 **Entramos a La Arena.** Cuatro inversionistas escucharon tu empresa. Respóndeles aquí en un "
         "solo mensaje, con datos: cifras, clientes, ventas, contratos.", agent="ceo", scene="arena", nivel=nivel)
    for inv in session.get("investors", []):
        qs = "\n".join(f"- {q}" for q in inv.get("questions", []))
        flags = ("\n\n🚩 " + "; ".join(inv["red_flags"])) if inv.get("red_flags") else ""
        db.add(Message(conversation_id=conversation(db, project, nivel).id, role="assistant",
                       agent_name=f"{inv['name']} · {inv['role']}", content=f"{inv['first_impression']}\n\n{qs}{flags}",
                       metadata_json={"agente": f"inv-{inv['id']}", "escena": "arena", "sesion_arena": session["id"]}))
    db.commit()


def arena_verdicts(db: Session, project: Project, answer: str, session: dict, nivel: int = 1) -> None:
    post(db, project, answer, role="user", scene="arena", nivel=nivel)
    labels = {"INVIERTE": "💰 Invierto", "CON_CONDICIONES": "🤝 Invierto con condiciones", "NO_INVIERTE": "❌ No invierto",
              "SIN_RESPUESTA": "… No pude decidir"}
    for inv in session.get("investors", []):
        text = f"**{labels.get(inv['decision'], inv['decision'])}.** {inv.get('reason', '')}"
        if inv.get("amount_usd"):
            text += f"\n\nPondría USD {inv['amount_usd']:,} · {inv.get('terms', '')}"
        if inv.get("conditions"):
            text += "\n\nCondiciones: " + "; ".join(inv["conditions"])
        if inv.get("fatal_flaw"):
            text += f"\n\n☠️ Falla fatal: {inv['fatal_flaw']}"
        db.add(Message(conversation_id=conversation(db, project, nivel).id, role="assistant",
                       agent_name=f"{inv['name']} · {inv['role']}", content=text,
                       metadata_json={"agente": f"inv-{inv['id']}", "escena": "arena", "decision": inv["decision"]}))
    post(db, project, ("🏆 " if session.get("passed") else "🛡️ ") + session.get("verdict", ""), agent="ceo", scene="arena",
         arena_passed=bool(session.get("passed")), nivel=nivel)
    db.commit()
