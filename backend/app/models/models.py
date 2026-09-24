"""SQLAlchemy models — maps AD-005/AD-006/AD-007 entities to tables.

Every entity inherits the Contrato Base (AD-006 §2):
- id (UUID)
- version (integer, auto-incremented per entity)
- status (active/archived, never deleted)
- created_at, updated_at
- created_by
- confidence_level (when applicable)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, Boolean,
    JSON, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


# --- Enums ---

class EntityStatus(str, PyEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class UserRole(str, PyEnum):
    USER = "user"
    PRIMARY_USER = "primary_user"  # Usuario Principal (AD-006)


class NivelStatus(str, PyEnum):
    BLOCKED = "blocked"
    ACTIVE = "active"
    COMPLETED = "completed"


class CardStatus(str, PyEnum):
    BLOCKED = "blocked"
    ACTIVE = "active"
    COMPLETED = "completed"


class DecisionStatus(str, PyEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


class ScoreType(str, PyEnum):
    PROBLEM = "problem"
    SOLUTION = "solution"
    BUSINESS = "business"
    PRODUCT = "product"
    MARKET = "market"
    EXECUTION = "execution"


# --- Users (AD-006 §4) ---

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(EntityStatus), default=EntityStatus.ACTIVE, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    created_by = Column(String(36), nullable=True)

    # Relationships
    companies = relationship("Company", back_populates="primary_user", foreign_keys="Company.primary_user_id")


# --- Companies (AD-005 §2.1) ---

class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    industry = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    legal_structure = Column(String(100), nullable=True)
    founding_narrative = Column(Text, nullable=True)  # Narrativa Fundacional
    maturity = Column(Float, default=0.0, nullable=False)  # Madurez Organizacional (0-1)
    status = Column(Enum(EntityStatus), default=EntityStatus.ACTIVE, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    confidence_level = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    primary_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Relationships
    primary_user = relationship("User", foreign_keys=[primary_user_id])
    projects = relationship("Project", back_populates="company")
    founding_narrative_entity = relationship("FoundingNarrative", back_populates="company", uselist=False)


class FoundingNarrative(Base):
    __tablename__ = "founding_narratives"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), unique=True, nullable=False)
    origin_story = Column(Text, nullable=True)
    founding_motivation = Column(Text, nullable=True)
    irreversible_commitment = Column(Text, nullable=True)
    status = Column(Enum(EntityStatus), default=EntityStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    company = relationship("Company", back_populates="founding_narrative_entity")


# --- Projects (AD-006 §4) ---

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Enum(EntityStatus), default=EntityStatus.ACTIVE, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    company = relationship("Company", back_populates="projects")
    levels = relationship("Level", back_populates="project")
    cards = relationship("Card", back_populates="project")
    scores = relationship("Score", back_populates="project")
    decisions = relationship("Decision", back_populates="project")
    documents = relationship("Document", back_populates="project")
    events = relationship("Event", back_populates="project")


# --- Levels (AD-006 §4) ---

class Level(Base):
    __tablename__ = "levels"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    number = Column(Integer, nullable=False)  # 1-7
    name = Column(String(255), nullable=False)
    status = Column(Enum(NivelStatus), default=NivelStatus.BLOCKED, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("project_id", "number"),)

    project = relationship("Project", back_populates="levels")
    cards = relationship("Card", back_populates="level")


# --- Cards (AD-006 §4) ---

class Card(Base):
    __tablename__ = "cards"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    level_id = Column(String(36), ForeignKey("levels.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    card_type = Column(String(100), nullable=False)  # e.g., "pain_discovery", "diagnosis"
    status = Column(Enum(CardStatus), default=CardStatus.BLOCKED, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    project = relationship("Project", back_populates="cards")
    level = relationship("Level", back_populates="cards")
    conversations = relationship("Conversation", back_populates="card")


# --- Conversations (AD-006 §4) ---

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    card_id = Column(String(36), ForeignKey("cards.id"), nullable=False)
    title = Column(String(255), nullable=True)
    status = Column(Enum(EntityStatus), default=EntityStatus.ACTIVE, nullable=False)
    summary = Column(Text, nullable=True)  # Generated when conversation completes
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    card = relationship("Card", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


# --- Messages (within a Conversation) ---

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # "user", "assistant", "system", "agent"
    agent_name = Column(String(100), nullable=True)  # e.g., "CEO", "CTO", "CFO"
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)  # tokens, model used, etc.
    created_at = Column(DateTime, default=utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


# --- Scores (AD-006 §4) ---

class Score(Base):
    __tablename__ = "scores"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    score_type = Column(Enum(ScoreType), nullable=False)
    value = Column(Float, nullable=False)  # 0-100
    confidence_level = Column(Float, nullable=False)  # 0-100
    reasoning = Column(Text, nullable=True)  # Why this score
    evidence = Column(JSON, nullable=True)  # Supporting evidence
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    project = relationship("Project", back_populates="scores")


# --- Decisions (AD-006 §4) ---

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    proposed_by = Column(String(100), nullable=True)  # Agent name or "user"
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    status = Column(Enum(DecisionStatus), default=DecisionStatus.PROPOSED, nullable=False)
    reasoning = Column(Text, nullable=True)
    disagreement = Column(Text, nullable=True)  # From AD-CMP-03 §3
    confidence_level = Column(Float, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    project = relationship("Project", back_populates="decisions")


# --- Documents (AD-005 §2.4) ---

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    doc_type = Column(String(100), nullable=False)  # "diagnosis", "business_plan", "blueprint"
    origin = Column(String(100), nullable=False)  # "generated_by_adan" or "received_from_client"
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    project = relationship("Project", back_populates="documents")


# --- Events (AD-006 §4) — append-only ---

class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    event_type = Column(String(100), nullable=False)  # "level_completed", "card_completed", etc.
    entity_type = Column(String(100), nullable=False)  # "level", "card", "score", etc.
    entity_id = Column(String(36), nullable=False)
    data = Column(JSON, nullable=True)  # Event payload
    created_at = Column(DateTime, default=utcnow, nullable=False)

    project = relationship("Project", back_populates="events")
