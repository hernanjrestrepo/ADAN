"""Memoria y contexto en cinco capas (AD-CMP-04, WO-099).

    Global → Proyecto → Nivel → Card → Conversación

Cada capa hereda de la que la contiene. Lo que asciende de una capa a la siguiente es el
resumen (qué se decidió, con qué evidencia, qué queda pendiente), nunca la conversación
completa: así el contexto no crece sin control y nada se pierde (la conversación queda en
la base). La capa Conversación (mensajes recientes y resumen de lo antiguo) la arma
`Nivel1Service.build_llm_messages`; este módulo arma las otras cuatro.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.disclaimer import strip_disclaimer
from app.models.models import (
    Card, Company, Conversation, Decision, DecisionStatus, Document, Level, Project, Score,
)

MAX_LAYER_CHARS = 1500

# Lo que ADÁN sabe con independencia de la empresa (el aprendizaje entre empresas llega en WO-118)
GLOBAL_LAYER = (
    "ADÁN acompaña a una empresa por 7 Niveles: 1 El Dolor, 2 Propuesta de Valor, 3 Plan de "
    "Negocios, 4 MVP, 5 Validación Simulada, 6 Lanzamiento, 7 Escalamiento. Se avanza por "
    "evidencia, nunca por pago, y toda decisión importante la aprueba el cliente."
)

NO_REPETITION_RULE = (
    "Regla de no repetición (AD-CMP-04 §4): antes de preguntar algo al cliente, revisa este "
    "contexto. Si la respuesta ya está aquí, no la vuelvas a pedir: di lo que estás asumiendo "
    "para que el cliente lo corrija si cambió."
)


def _clip(text: str, limit: int = MAX_LAYER_CHARS) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


class ContextLayers:
    def __init__(self, db: Session):
        self.db = db

    def project_layer(self, project: Project) -> str:
        """Lo permanente de la empresa (Gemelo Digital): perfil, decisiones y scores."""
        company = self.db.get(Company, project.company_id)
        lines = [f"Empresa: {company.name}"]
        for label, value in (("Industria", company.industry), ("País", company.country),
                             ("Descripción", company.description)):
            if value:
                lines.append(f"{label}: {value}")
        narrative = company.founding_narrative_entity
        if narrative and narrative.origin_story:
            lines.append(f"Narrativa fundacional: {narrative.origin_story}")
        decisions = self.db.query(Decision).filter(
            Decision.project_id == project.id,
            Decision.status.in_([DecisionStatus.APPROVED, DecisionStatus.EXECUTED]),
        ).order_by(Decision.created_at).all()
        if decisions:
            lines.append("Decisiones aprobadas por el cliente (no contradecirlas sin decirlo): "
                         + "; ".join(d.title for d in decisions[-10:]))
        scores = self.db.query(Score).filter(Score.project_id == project.id).order_by(Score.created_at).all()
        latest = {}
        for score in scores:
            latest[getattr(score.score_type, "value", score.score_type)] = score
        if latest:
            lines.append("Scores: " + ", ".join(f"{k} {s.value:.0f} (confianza {s.confidence_level:.0f}%)"
                                                for k, s in latest.items()))
        summaries = self.db.query(Document).filter(
            Document.project_id == project.id, Document.doc_type == "level_summary",
        ).order_by(Document.created_at).all()
        for doc in summaries:
            lines.append(_clip(strip_disclaimer(doc.content or ""), 600))
        return _clip("\n".join(lines))

    def level_layer(self, level: Level) -> str:
        """La etapa actual: nombre, estado y lo que dejó el último Board Room."""
        lines = [f"Nivel {level.number} — {level.name} ({getattr(level.status, 'value', level.status)})"]
        minutes = self.db.query(Document).filter(
            Document.project_id == level.project_id, Document.doc_type == "board_minutes",
        ).order_by(Document.created_at.desc()).first()
        if minutes:
            text = strip_disclaimer(minutes.content or "")
            for section in ("## Resultado", "## Síntesis del CEO", "## Evidencia que el Board pide"):
                if section in text:
                    part = text.split(section, 1)[1].split("\n## ", 1)[0].lstrip(": ")
                    lines.append(f"{section[3:]}: {_clip(' '.join(part.split()), 400)}")
        return _clip("\n".join(lines))

    def card_layer(self, card: Card, current: Conversation | None = None) -> str:
        """El proceso de la Card y los resúmenes de sus otras conversaciones."""
        lines = [f"Card: {card.title}"]
        if card.description:
            lines.append(card.description)
        others = self.db.query(Conversation).filter(
            Conversation.card_id == card.id, Conversation.summary.isnot(None),
        ).all()
        for conv in others:
            if current is None or conv.id != current.id:
                lines.append(f"Conversación anterior: {_clip(conv.summary, 400)}")
        return _clip("\n".join(lines))

    def for_conversation(self, conversation: Conversation) -> str:
        """Las cuatro capas que contienen a una conversación, de la más amplia a la más cercana."""
        card = self.db.get(Card, conversation.card_id)
        level = self.db.get(Level, card.level_id)
        project = self.db.get(Project, card.project_id)
        return "\n\n".join([
            f"[Global]\n{GLOBAL_LAYER}",
            f"[Proyecto]\n{self.project_layer(project)}",
            f"[Nivel]\n{self.level_layer(level)}",
            f"[Card]\n{self.card_layer(card, conversation)}",
            NO_REPETITION_RULE,
        ])

    def level_summary(self, project: Project, level: Level) -> str:
        """Resumen que asciende al Proyecto cuando un Nivel se completa (AD-CMP-04 §3)."""
        decisions = self.db.query(Decision).filter(Decision.project_id == project.id).order_by(Decision.created_at).all()
        decided = [d for d in decisions if d.status in (DecisionStatus.APPROVED, DecisionStatus.EXECUTED)]
        pending = [d for d in decisions if d.status == DecisionStatus.PROPOSED]
        lines = [f"Resumen del Nivel {level.number} — {level.name}"]
        lines.append("Se decidió: " + ("; ".join(d.title for d in decided) or "nada registrado"))
        diag = self.db.query(Document).filter(
            Document.project_id == project.id, Document.doc_type == "diagnosis",
        ).order_by(Document.created_at.desc()).first()
        if diag:
            lines.append("Evidencia: " + _clip(strip_disclaimer(diag.content or ""), 500))
        minutes = self.db.query(Document).filter(
            Document.project_id == project.id, Document.doc_type == "board_minutes",
        ).order_by(Document.created_at.desc()).first()
        if minutes and "## Evidencia que el Board pide" in (minutes.content or ""):
            asks = minutes.content.split("## Evidencia que el Board pide", 1)[1].split("\n## ", 1)[0]
            lines.append("Pendiente (evidencia pedida): " + _clip(" ".join(asks.split()), 400))
        if pending:
            lines.append("Pendiente (decisiones sin respuesta): " + "; ".join(d.title for d in pending))
        return "\n".join(lines)
