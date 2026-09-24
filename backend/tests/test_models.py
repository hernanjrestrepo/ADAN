"""Database model tests."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.models import (
    Company, Decision, Document, Event, FoundingNarrative, Level,
    Message, Conversation, Card, Project, Score, User, UserRole,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_user_creation(session):
    """User can be created."""
    user = User(
        email="test@test.com",
        name="Test",
        hashed_password="hashed",
        role=UserRole.PRIMARY_USER,
    )
    session.add(user)
    session.commit()
    assert user.id is not None
    assert user.version == 1


def test_company_creation(session):
    """Company with founding narrative can be created."""
    user = User(
        email="owner@test.com",
        name="Owner",
        hashed_password="hashed",
        role=UserRole.PRIMARY_USER,
    )
    session.add(user)
    session.flush()

    company = Company(
        name="Test Corp",
        created_by=user.id,
        primary_user_id=user.id,
    )
    session.add(company)
    session.flush()

    narrative = FoundingNarrative(company_id=company.id)
    session.add(narrative)
    session.commit()

    assert company.id is not None
    assert narrative.company_id == company.id


def test_project_with_levels(session):
    """Project with 7 levels can be created."""
    user = User(email="p@test.com", name="P", hashed_password="h", role=UserRole.PRIMARY_USER)
    session.add(user)
    session.flush()

    company = Company(name="C", created_by=user.id, primary_user_id=user.id)
    session.add(company)
    session.flush()

    project = Project(company_id=company.id, name="Proyecto C")
    session.add(project)
    session.flush()

    for i in range(1, 8):
        level = Level(project_id=project.id, number=i, name=f"Level {i}")
        session.add(level)

    session.commit()
    levels = session.query(Level).filter(Level.project_id == project.id).all()
    assert len(levels) == 7
