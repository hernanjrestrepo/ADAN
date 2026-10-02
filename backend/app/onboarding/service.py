"""Onboarding (AD-FUNC-06, WO-108): llegar a la primera pregunta real, no llenar un formulario.

- Antes de la primera pregunta se captura lo mínimo (§2): nombre, correo y una señal de que
  existe una Empresa o la intención de crearla. Todo lo demás se difiere.
- La primera pregunta real de ADÁN queda escrita en la conversación del Nivel 1 en cuanto nace
  la Empresa (§3), y el tiempo desde el registro se mide (§3.4, meta < 30 s).
- La Identidad Progresiva (§3.1) es una etiqueta derivada de lo que ya hay en el Gemelo, nunca
  un campo guardado.
- Recuperación (§3.3): el paso siguiente se lee de lo que ya existe; nada se vuelve a preguntar.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core import privacy
from app.models.models import (
    Card, CardStatus, Company, Consent, Conversation, Decision, DecisionStatus, Document, Event, Level, Message,
    Project, User,
)
from app.twin.models import BusinessDecision

FIRST_QUESTION_AGENT = "ADÁN"

# Escalera de AD-FUNC-06 §3.1 (Anónimo y Visitante existen antes del registro)
IDENTITY = [
    ("usuario", "Usuario", "Registro mínimo completado"),
    ("responsable", "Responsable de Empresa", "Confirmaste que eres responsable de una Empresa"),
    ("lider_activo", "Líder Activo", "Recibiste tu primer Diagnóstico real del Nivel 1"),
    ("cliente_activo", "Cliente Activo", "Registraste tu primera Decisión de Negocio real"),
    ("embajador", "Embajador", "Una recomendación de ADÁN que aceptaste se sostuvo en el tiempo"),
]
SUSTAINED_DAYS = 30


def first_question(user: User, company: Company) -> str:
    first_name = (user.name or "").split(" ")[0] or "hola"
    return (f"Hola, {first_name}. Soy ADÁN y voy a acompañarte con «{company.name}». Empecemos por lo "
            "importante: ¿qué problema quieres resolver y a quién le duele? Cuéntamelo con tus palabras, "
            "no hace falta que esté pulido.")


def _utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def seed_first_question(db: Session, user: User, company: Company) -> Message | None:
    """ADÁN hace la primera pregunta real del Nivel 1 apenas nace la Empresa (AD-FUNC-06 §1)."""
    project = db.query(Project).filter(Project.company_id == company.id).first()
    level = db.query(Level).filter(Level.project_id == project.id, Level.number == 1).first() if project else None
    if level is None:
        return None
    card = db.query(Card).filter(Card.project_id == project.id, Card.card_type == "pain_discovery").first()
    if card is None:
        card = Card(project_id=project.id, level_id=level.id, title="Descubrimiento del Dolor",
                    description="¿Qué problema real resuelve tu empresa? ¿A quién afecta? ¿Qué tan urgente es?",
                    card_type="pain_discovery", status=CardStatus.ACTIVE)
        db.add(card)
        db.flush()
    conv = db.query(Conversation).filter(Conversation.card_id == card.id).first()
    if conv is None:
        conv = Conversation(card_id=card.id, title="Conversación de Descubrimiento")
        db.add(conv)
        db.flush()
    if db.query(Message).filter(Message.conversation_id == conv.id).count():
        return None  # Regla de no repetición: si ya hay conversación, no se vuelve a preguntar
    message = Message(conversation_id=conv.id, role="assistant", agent_name=FIRST_QUESTION_AGENT,
                      content=first_question(user, company), metadata_json={"onboarding": True})
    db.add(message)
    seconds = (datetime.now(timezone.utc) - _utc(user.created_at)).total_seconds() if user.created_at else None
    db.add(Event(project_id=project.id, company_id=company.id, event_type="onboarding_first_question",
                 entity_type="conversations", entity_id=conv.id, category="domain", actor_type="system",
                 actor_id=FIRST_QUESTION_AGENT,
                 data={"label": company.name, "seconds_since_signup": round(seconds, 1) if seconds is not None else None,
                       "target_seconds": 30}))
    db.flush()
    return message


def identity(db: Session, user: User) -> dict:
    """Etiqueta de Identidad Progresiva, leída del Gemelo (AD-FUNC-06 §3.1)."""
    companies = db.query(Company).filter(Company.primary_user_id == user.id).all()
    company_ids = [c.id for c in companies]
    project_ids = [p for (p,) in db.query(Project.id).filter(Project.company_id.in_(company_ids)).all()] \
        if company_ids else []
    reached = {"usuario": True, "responsable": bool(companies)}
    reached["lider_activo"] = bool(project_ids) and db.query(Document).filter(
        Document.project_id.in_(project_ids), Document.doc_type == "diagnosis").count() > 0
    reached["cliente_activo"] = bool(company_ids) and db.query(BusinessDecision).filter(
        BusinessDecision.company_id.in_(company_ids)).count() > 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=SUSTAINED_DAYS)
    sustained = [d for d in (db.query(Decision).filter(Decision.project_id.in_(project_ids),
                                                       Decision.status == DecisionStatus.EXECUTED).all()
                             if project_ids else [])
                 if not d.divergence and d.executed_at and _utc(d.executed_at) <= cutoff]
    reached["embajador"] = bool(sustained)

    current = IDENTITY[0]
    for step in IDENTITY:  # Patrón B: una etiqueta exige las anteriores
        if not reached[step[0]]:
            break
        current = step
    index = IDENTITY.index(current)
    nxt = IDENTITY[index + 1] if index + 1 < len(IDENTITY) else None
    return {"key": current[0], "label": current[1], "step": index + 1, "of": len(IDENTITY),
            "next": None if nxt is None else {"key": nxt[0], "label": nxt[1], "milestone": nxt[2]}}


def current_consents(db: Session, user: User) -> dict[str, dict]:
    out = {}
    for purpose, text in privacy.PURPOSES.items():
        row = db.query(Consent).filter(Consent.user_id == user.id, Consent.purpose == purpose) \
            .order_by(Consent.created_at.desc()).first()
        out[purpose] = {"purpose": purpose, "text": text, "granted": bool(row and row.granted),
                        "policy_version": row.policy_version if row else None,
                        "since": row.created_at.isoformat() if row else None}
    return out


def next_step(db: Session, user: User) -> dict:
    """Recuperación de Onboarding (§3.3): el último paso real completado decide el siguiente."""
    company = db.query(Company).filter(Company.primary_user_id == user.id).order_by(Company.created_at).first()
    if company is None:
        return {"step": "company", "company_id": None}
    project = db.query(Project).filter(Project.company_id == company.id).first()
    answered = project is not None and db.query(Message).join(Conversation).join(Card).filter(
        Card.project_id == project.id, Message.role == "user").count() > 0
    return {"step": "done" if answered else "first_answer", "company_id": company.id}
