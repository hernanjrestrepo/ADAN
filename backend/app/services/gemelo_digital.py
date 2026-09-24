"""Gemelo Digital Service — persists the complete digital twin.

Persists: empresa, proyecto, usuario, nivel, diagnóstico, decisiones,
board room, recomendaciones, memoria, entregables.

Every change updates the Gemelo Digital (AD-002 §1.5, §1.7).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.models import (
    Card, CardStatus, Company, Conversation, Decision, DecisionStatus,
    Document, Event, Level, NivelStatus, Message, Project, Score, ScoreType,
)


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
        """Mark level as completed and activate next."""
        level = self.get_or_create_level(project, level_number)
        level.status = NivelStatus.COMPLETED
        level.completed_at = datetime.now(timezone.utc)

        # Activate next level (create if doesn't exist)
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
            content=content,
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
    ) -> Decision:
        """Save Board Room result as a Decision."""
        decision_obj = Decision(
            project_id=project.id,
            title=f"Board Room: {decision}",
            description=summary,
            proposed_by="Board Room",
            status=DecisionStatus.APPROVED if decision == "PROCEED" else DecisionStatus.PROPOSED,
            reasoning=summary,
            confidence_level=score,
        )
        self.db.add(decision_obj)
        self.db.flush()  # Generate ID before using it

        self._record_event(
            project.id,
            "board_room_completed",
            "decision",
            decision_obj.id,
            {"decision": decision, "score": score, "agents": [v.get("agent") for v in votes]},
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
            content=content,
            doc_type="recommendation",
            origin="generated_by_adan",
        )
        self.db.add(doc)
        self.db.flush()  # Generate ID before using it

        self._record_event(
            "document",
            doc.id,
            {"title": title},
        )

        self.db.commit()
        self.db.refresh(doc)
        return doc

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
