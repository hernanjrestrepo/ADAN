"""
Knowledge Engine — Motor de conocimiento del sistema cognitivo.

Recupera conocimiento relevante de las fuentes de datos existentes
(Gemelo Digital, modelos, conversaciones) para enriquecer el contexto.
"""

from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.models.models import (
    Company, Project, Level, Card, Score, Decision, Document, Message, Event
)


@dataclass
class KnowledgeUnit:
    """Unidad de conocimiento recuperada."""
    source: str
    entity_type: str
    entity_id: str
    content: str
    relevance: float  # 0-1
    metadata: dict = field(default_factory=dict)


@dataclass
class KnowledgeContext:
    """Contexto completo de conocimiento para una empresa."""
    company_info: dict = field(default_factory=dict)
    project_info: dict = field(default_factory=dict)
    current_level: dict = field(default_factory=dict)
    scores: list[dict] = field(default_factory=list)
    recent_decisions: list[dict] = field(default_factory=list)
    recent_documents: list[dict] = field(default_factory=list)
    conversation_history: list[dict] = field(default_factory=list)
    recent_events: list[dict] = field(default_factory=list)
    units: list[KnowledgeUnit] = field(default_factory=list)


class KnowledgeEngine:
    """
    Motor de conocimiento que recopila toda la información
    relevante de una empresa para enriquecer el contexto.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_knowledge_context(self, company_id: str) -> KnowledgeContext:
        """Recopila todo el conocimiento relevante de una empresa."""
        ctx = KnowledgeContext()

        # 1. Información de la empresa
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if company:
            ctx.company_info = {
                "id": str(company.id),
                "name": company.name,
                "description": company.description,
                "industry": company.industry,
                "country": company.country,
                "maturity": company.maturity,
            }
            ctx.units.append(KnowledgeUnit(
                source="company",
                entity_type="Company",
                entity_id=str(company.id),
                content=f"Empresa: {company.name}, industria: {company.industry}, país: {company.country}",
                relevance=1.0,
            ))

        # 2. Proyecto asociado
        project = self.db.query(Project).filter(Project.company_id == company_id).first()
        if project:
            ctx.project_info = {
                "id": str(project.id),
                "name": project.name,
                "status": project.status,
            }

            # 3. Nivel actual
            current_level = (
                self.db.query(Level)
                .filter(Level.project_id == project.id, Level.status == "active")
                .first()
            )
            if current_level:
                ctx.current_level = {
                    "number": current_level.number,
                    "name": current_level.name,
                    "status": current_level.status,
                }
                ctx.units.append(KnowledgeUnit(
                    source="level",
                    entity_type="Level",
                    entity_id=str(current_level.id),
                    content=f"Nivel actual: {current_level.name} (nivel {current_level.number})",
                    relevance=0.9,
                ))

            # 4. Scores del proyecto
            scores = self.db.query(Score).filter(Score.project_id == project.id).all()
            for score in scores:
                score_data = {
                    "type": score.score_type,
                    "value": score.value,
                    "confidence": score.confidence_level,
                    "reasoning": score.reasoning,
                }
                ctx.scores.append(score_data)
                ctx.units.append(KnowledgeUnit(
                    source="score",
                    entity_type="Score",
                    entity_id=str(score.id),
                    content=f"Score {score.score_type}: {score.value}/100 (confianza: {score.confidence_level}%)",
                    relevance=0.7,
                ))

            # 5. Decisiones recientes
            decisions = (
                self.db.query(Decision)
                .filter(Decision.project_id == project.id)
                .order_by(Decision.created_at.desc())
                .limit(5)
                .all()
            )
            for dec in decisions:
                dec_data = {
                    "title": dec.title,
                    "description": dec.description,
                    "status": dec.status,
                    "proposed_by": dec.proposed_by,
                    "reasoning": dec.reasoning,
                }
                ctx.recent_decisions.append(dec_data)
                ctx.units.append(KnowledgeUnit(
                    source="decision",
                    entity_type="Decision",
                    entity_id=str(dec.id),
                    content=f"Decisión: {dec.title} — {dec.status}",
                    relevance=0.6,
                ))

            # 6. Documentos recientes
            documents = (
                self.db.query(Document)
                .filter(Document.project_id == project.id)
                .order_by(Document.created_at.desc())
                .limit(3)
                .all()
            )
            for doc in documents:
                doc_data = {
                    "title": doc.title,
                    "doc_type": doc.doc_type,
                    "content_preview": doc.content[:500] if doc.content else "",
                }
                ctx.recent_documents.append(doc_data)

            # 7. Historial de conversaciones (últimos 10 mensajes)
            from app.models.models import Conversation as ConversationModel
            messages = (
                self.db.query(Message)
                .join(ConversationModel, Message.conversation_id == ConversationModel.id)
                .join(Card, ConversationModel.card_id == Card.id)
                .filter(Card.project_id == project.id)
                .order_by(Message.created_at.desc())
                .limit(10)
                .all()
            )
            for msg in reversed(messages):  # Orden cronológico
                ctx.conversation_history.append({
                    "role": msg.role,
                    "content": msg.content[:300],
                    "agent_name": msg.agent_name,
                })

            # 8. Eventos recientes
            events = (
                self.db.query(Event)
                .filter(Event.project_id == project.id)
                .order_by(Event.created_at.desc())
                .limit(10)
                .all()
            )
            for event in events:
                ctx.recent_events.append({
                    "type": event.event_type,
                    "entity_type": event.entity_type,
                    "timestamp": event.created_at.isoformat() if event.created_at else None,
                })

        return ctx

    def build_knowledge_prompt(self, ctx: KnowledgeContext) -> str:
        """Construye un prompt enriquecido con el conocimiento disponible."""
        parts = []

        # Empresa
        if ctx.company_info:
            name = ctx.company_info.get("name", "desconocida")
            industry = ctx.company_info.get("industry", "desconocida")
            country = ctx.company_info.get("country", "desconocido")
            parts.append(f"Empresa: {name} ({industry}, {country})")

        # Proyecto
        if ctx.project_info:
            parts.append(f"Proyecto: {ctx.project_info.get('name', 'sin nombre')}")

        # Nivel
        if ctx.current_level:
            parts.append(f"Nivel actual: {ctx.current_level.get('name', '?')} (nivel {ctx.current_level.get('number', '?')})")

        # Scores
        if ctx.scores:
            scores_text = ", ".join(
                f"{s['type']}: {s['value']}/100" for s in ctx.scores
            )
            parts.append(f"Scores: {scores_text}")

        # Decisiones
        if ctx.recent_decisions:
            dec_text = "; ".join(
                f"{d['title']} ({d['status']})" for d in ctx.recent_decisions[:3]
            )
            parts.append(f"Decisiones recientes: {dec_text}")

        # Documentos
        if ctx.recent_documents:
            doc_text = "; ".join(
                f"{d['title']} ({d['doc_type']})" for d in ctx.recent_documents[:2]
            )
            parts.append(f"Documentos: {doc_text}")

        # Conversación reciente
        if ctx.conversation_history:
            parts.append("Historial reciente de conversación:")
            for msg in ctx.conversation_history[-5:]:
                role = "Usuario" if msg["role"] == "user" else "ADÁN"
                parts.append(f"  {role}: {msg['content'][:200]}")

        return "\n".join(parts)
