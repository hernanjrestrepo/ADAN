"""Gemelo Digital Service — persists the complete digital twin.

Persists: empresa, proyecto, usuario, nivel, diagnóstico, decisiones,
board room, recomendaciones, memoria, entregables.

Every change updates the Gemelo Digital (AD-002 §1.5, §1.7).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.disclaimer import with_disclaimer
from app.models.models import (
    Card, CardStatus, Company, Conversation, Decision, DecisionStatus,
    Document, Event, Level, NivelStatus, Message, Project, Score, ScoreType,
)


LAST_LEVEL = 7


class GemeloDigitalService:
    """Manages the complete digital twin persistence."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_project(self, company: Company) -> Project:
        """Get or create project for a company (1:1 per AD-006 §4)."""
        project = self.db.query(Project).filter(
            Project.company_id == company.id
        ).first()

        if not project:
            project = Project(
                company_id=company.id,
                name=f"Proyecto {company.name}",
            )
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)

        return project

    def get_or_create_level(self, project: Project, level_number: int) -> Level:
        """Get or create a specific level."""
        level = self.db.query(Level).filter(
            Level.project_id == project.id,
            Level.number == level_number,
        ).first()

        if not level:
            level = Level(
                project_id=project.id,
                number=level_number,
                name=self._get_level_name(level_number),
                status=NivelStatus.BLOCKED,
            )
            self.db.add(level)
            self.db.commit()
            self.db.refresh(level)

        return level

    def activate_level(self, project: Project, level_number: int) -> Level:
        """Activate a specific level."""
        level = self.get_or_create_level(project, level_number)
        level.status = NivelStatus.ACTIVE
        self.db.commit()
        self.db.refresh(level)
        return level

    def complete_level(self, project: Project, level_number: int) -> Level:
        """Mark level as completed and activate next (Nivel 7 is the last one)."""
        level = self.get_or_create_level(project, level_number)
        level.status = NivelStatus.COMPLETED
        level.completed_at = datetime.now(timezone.utc)

        # Activate next level (create if doesn't exist)
        if level_number < LAST_LEVEL:
            next_level = self.get_or_create_level(project, level_number + 1)
            next_level.status = NivelStatus.ACTIVE

        # Record event
        self._record_event(
            project.id,
            "level_completed",
            "level",
            level.id,
            {"level_number": level_number, "level_name": level.name},
        )

        self.db.commit()
        self.db.refresh(level)
        return level

    def save_diagnosis(self, project: Project, title: str, content: str) -> Document:
        """Save a diagnosis document."""
        doc = Document(
            project_id=project.id,
            title=title,
            content=with_disclaimer(content),
            doc_type="diagnosis",
            origin="generated_by_adan",
        )
        self.db.add(doc)
        self.db.flush()  # Generate ID before using it

        self._record_event(
            project.id,
            "diagnosis_saved",
            "document",
            doc.id,
            {"title": title},
        )

        self.db.commit()
        self.db.refresh(doc)
        return doc

    def save_board_room_result(
        self,
        project: Project,
        decision: str,
        score: float,
        summary: str,
        votes: list[dict],
        consensus: dict | None = None,
    ) -> Decision:
        """Save Board Room result as a proposed Decision: only the client approves (Patrón A)."""
        decision_obj = Decision(
            project_id=project.id,
            title=f"Board Room: {decision}",
            description=summary,
            proposed_by="Board Room",
            status=DecisionStatus.PROPOSED,
            reasoning=summary,
            confidence_level=score,
        )
        self.db.add(decision_obj)
        self.db.flush()  # Generate ID before using it

        data = {"decision": decision, "score": score, "agents": [v.get("agent") for v in votes]}
        if consensus is not None:
            data["consensus"] = consensus
        self._record_event(
            project.id,
            "board_room_completed",
            "decision",
            decision_obj.id,
            data,
        )

        self.db.commit()
        self.db.refresh(decision_obj)
        return decision_obj

    def save_score(
        self,
        project: Project,
        score_type: str,
        value: float,
        confidence: float,
        reasoning: str = "",
    ) -> Score:
        """Save a score."""
        score = Score(
            project_id=project.id,
            score_type=ScoreType(score_type),
            value=value,
            confidence_level=confidence,
            reasoning=reasoning,
        )
        self.db.add(score)
        self.db.flush()  # Generate ID before using it

        self._record_event(
            project.id,
            "score_calculated",
            "score",
            score.id,
            {"type": score_type, "value": value, "confidence": confidence},
        )

        self.db.commit()
        self.db.refresh(score)
        return score

    def save_recommendation(
        self,
        project: Project,
        title: str,
        content: str,
    ) -> Document:
        """Save a recommendation document."""
        doc = Document(
            project_id=project.id,
            title=title,
            content=with_disclaimer(content),
            doc_type="recommendation",
            origin="generated_by_adan",
        )
        self.db.add(doc)
        self.db.flush()  # Generate ID before using it

        self._record_event(
            project.id,
            "recommendation_saved",
            "document",
            doc.id,
            {"title": title},
        )

        self.db.commit()
        self.db.refresh(doc)
        return doc

    def save_board_minutes(self, project: Project, minutes: str) -> Document:
        """Acta del Board Room (AD-FUNC-02): documento generado por ADÁN, con aviso de IA."""
        doc = Document(
            project_id=project.id,
            title="Acta del Board Room",
            content=with_disclaimer(minutes),
            doc_type="board_minutes",
            origin="generated_by_adan",
        )
        self.db.add(doc)
        self.db.flush()
        self._record_event(project.id, "board_minutes_saved", "document", doc.id, {"title": doc.title})
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_last_board_consensus(self, project: Project) -> dict | None:
        """Último resultado completo del Board Room, para no volver a ejecutarlo."""
        events = self.db.query(Event).filter(
            Event.project_id == project.id,
            Event.event_type == "board_room_completed",
        ).order_by(Event.created_at.desc()).all()
        for event in events:
            if event.data and event.data.get("consensus"):
                return event.data["consensus"]
        return None

    def propose_level_completion(
        self, project: Project, level_number: int, score: float, message: str,
    ) -> Decision:
        """Propone cerrar el Nivel; solo se completa cuando el cliente aprueba (AD-FUNC-01)."""
        pending = self.get_pending_level_completion(project, level_number)
        if pending:
            return pending

        decision_obj = Decision(
            project_id=project.id,
            title=f"Cerrar Nivel {level_number}",
            description=message,
            proposed_by="Gate Review",
            status=DecisionStatus.PROPOSED,
            reasoning=message,
            confidence_level=score,
        )
        self.db.add(decision_obj)
        self.db.flush()
        self._record_event(
            project.id,
            "level_completion_proposed",
            "decision",
            decision_obj.id,
            {"level_number": level_number, "score": score},
        )
        self.db.commit()
        self.db.refresh(decision_obj)
        return decision_obj

    def get_pending_level_completion(self, project: Project, level_number: int) -> Decision | None:
        """Decisión de cierre de Nivel que espera la aprobación del cliente, si existe."""
        for event in self._level_completion_events(project):
            if (event.data or {}).get("level_number") == level_number:
                decision_obj = self.db.query(Decision).filter(Decision.id == event.entity_id).first()
                if decision_obj and decision_obj.status == DecisionStatus.PROPOSED:
                    return decision_obj
        return None

    def decide(self, project: Project, decision_obj: Decision, approve: bool, user_id: str) -> Decision:
        """El cliente aprueba o rechaza una decisión propuesta (Patrón A, AD-008).

        Si aprueba el cierre de un Nivel, el Nivel se completa y la decisión queda ejecutada.
        """
        if decision_obj.status != DecisionStatus.PROPOSED:
            raise ValueError("Solo se puede aprobar o rechazar una decisión propuesta")

        decision_obj.status = DecisionStatus.APPROVED if approve else DecisionStatus.REJECTED
        decision_obj.approved_by = user_id
        self._record_event(
            project.id,
            "decision_approved" if approve else "decision_rejected",
            "decision",
            decision_obj.id,
            {"title": decision_obj.title},
        )

        if approve:
            level_number = next(
                ((e.data or {}).get("level_number") for e in self._level_completion_events(project)
                 if e.entity_id == decision_obj.id),
                None,
            )
            if level_number is not None:
                self.complete_level(project, level_number)
                decision_obj.status = DecisionStatus.EXECUTED

        self.db.commit()
        self.db.refresh(decision_obj)
        return decision_obj

    def _level_completion_events(self, project: Project) -> list[Event]:
        return self.db.query(Event).filter(
            Event.project_id == project.id,
            Event.event_type == "level_completion_proposed",
        ).order_by(Event.created_at.desc()).all()

    def get_gemelo_state(self, company: Company) -> dict:
        """Get the complete Gemelo Digital state."""
        project = self.db.query(Project).filter(
            Project.company_id == company.id
        ).first()

        if not project:
            return {"company": company, "project": None}

        levels = self.db.query(Level).filter(
            Level.project_id == project.id
        ).order_by(Level.number).all()

        scores = self.db.query(Score).filter(
            Score.project_id == project.id
        ).all()

        decisions = self.db.query(Decision).filter(
            Decision.project_id == project.id
        ).all()

        documents = self.db.query(Document).filter(
            Document.project_id == project.id
        ).all()

        events = self.db.query(Event).filter(
            Event.project_id == project.id
        ).order_by(Event.created_at.desc()).limit(50).all()

        return {
            "company": company,
            "project": project,
            "levels": levels,
            "scores": scores,
            "decisions": decisions,
            "documents": documents,
            "events": events,
            "current_level": next((l for l in levels if l.status == "active"), None),
            "completed_levels": sum(1 for l in levels if l.status == "completed"),
            "total_levels": len(levels),
        }

    def _record_event(
        self,
        project_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        data: dict = None,
    ):
        """Record an event in the Gemelo Digital."""
        event = Event(
            project_id=project_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data or {},
        )
        self.db.add(event)

    def _get_level_name(self, number: int) -> str:
        """Get the name for a level number."""
        names = {
            1: "El Dolor",
            2: "Propuesta de Valor",
            3: "Plan de Negocios",
            4: "MVP",
            5: "Validación Simulada",
            6: "Lanzamiento",
            7: "Escalamiento",
        }
        return names.get(number, f"Nivel {number}")
