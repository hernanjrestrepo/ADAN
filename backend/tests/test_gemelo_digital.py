"""Gemelo Digital tests — verifies persistence and state management."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.models import (
    Company, Document, Event, Level, Project, Score, ScoreType, User, UserRole,
)
from app.services.gemelo_digital import GemeloDigitalService


@pytest.fixture
def db():
    engine = create_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create test user and company
    user = User(email="test@test.com", name="Test", hashed_password="hash", role=UserRole.PRIMARY_USER)
    session.add(user)
    session.flush()

    company = Company(name="Test Corp", created_by=user.id, primary_user_id=user.id)
    session.add(company)
    session.commit()
    session.refresh(company)

    yield session, company
    session.close()


def test_get_or_create_project(db):
    """Project is created for company."""
    session, company = db
    service = GemeloDigitalService(session)
    project = service.get_or_create_project(company)
    assert project is not None
    assert project.company_id == company.id
    assert project.name == f"Proyecto {company.name}"


def test_get_or_create_level(db):
    """Levels are created correctly."""
    session, company = db
    service = GemeloDigitalService(session)
    project = service.get_or_create_project(company)
    level = service.get_or_create_level(project, 1)
    assert level is not None
    assert level.number == 1
    assert level.name == "El Dolor"


def test_complete_level(db):
    """Completing a level activates the next."""
    session, company = db
    service = GemeloDigitalService(session)
    project = service.get_or_create_project(company)

    # Activate and complete level 1
    service.activate_level(project, 1)
    level1 = service.complete_level(project, 1)
    assert level1.status == "completed"
    assert level1.completed_at is not None

    # Level 2 should be active
    level2 = service.get_or_create_level(project, 2)
    assert level2.status == "active"


def test_save_diagnosis(db):
    """Diagnosis is persisted with event."""
    session, company = db
    service = GemeloDigitalService(session)
    project = service.get_or_create_project(company)
    doc = service.save_diagnosis(project, "Test Diagnosis", "Content here")
    assert doc is not None
    assert doc.title == "Test Diagnosis"
    assert doc.doc_type == "diagnosis"

    # Event should be recorded
    events = session.query(Event).filter(Event.project_id == project.id).all()
    assert len(events) == 1
    assert events[0].event_type == "diagnosis_saved"


def test_save_score(db):
    """Score is persisted with event."""
    session, company = db
    service = GemeloDigitalService(session)
    project = service.get_or_create_project(company)
    score = service.save_score(project, "problem", 75.0, 80.0, "Test reasoning")
    assert score is not None
    assert score.value == 75.0
    assert score.confidence_level == 80.0

    events = session.query(Event).filter(Event.project_id == project.id).all()
    assert len(events) == 1
    assert events[0].event_type == "score_calculated"


def test_save_board_room_result(db):
    """Board Room result is persisted as Decision."""
    session, company = db
    service = GemeloDigitalService(session)
    project = service.get_or_create_project(company)
    decision = service.save_board_room_result(
        project, "PROCEED", 75.0, "Summary", [{"agent": "CEO", "vote": "PROCEED"}]
    )
    assert decision is not None
    assert decision.title == "Board Room: PROCEED"

    events = session.query(Event).filter(Event.project_id == project.id).all()
    assert len(events) == 1
    assert events[0].event_type == "board_room_completed"


def test_get_gemelo_state(db):
    """Gemelo state includes all entities."""
    session, company = db
    service = GemeloDigitalService(session)
    project = service.get_or_create_project(company)
    service.activate_level(project, 1)
    service.save_score(project, "problem", 75.0, 80.0, "Test")

    state = service.get_gemelo_state(company)
    assert state["company"] is not None
    assert state["project"] is not None
    assert len(state["levels"]) > 0
    assert len(state["scores"]) > 0
    assert state["completed_levels"] == 0
    assert state["total_levels"] >= 1
