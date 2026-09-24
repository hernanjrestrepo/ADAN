"""
OOS Models — Entidades del dominio organizacional.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Float, Integer, DateTime, JSON, Boolean,
    ForeignKey, Index
)
from sqlalchemy.orm import relationship, DeclarativeBase


class OOSBase(DeclarativeBase):
    """Base separada para modelos OOS."""
    pass


def gen_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


# ============================================================
# Organization Structure
# ============================================================

class Organization(OOSBase):
    """Organización empresarial."""
    __tablename__ = "oos_organizations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    maturity_level = Column(Float, default=0.0)
    status = Column(String(20), default="active")
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    created_by = Column(String(36), nullable=True)
    version = Column(Integer, default=1)

    business_units = relationship("BusinessUnit", back_populates="organization", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="organization", cascade="all, delete-orphan")
    objectives = relationship("Objective", back_populates="organization", cascade="all, delete-orphan")
    kpis = relationship("KPI", back_populates="organization", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="organization", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="organization", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="organization", cascade="all, delete-orphan")


class BusinessUnit(OOSBase):
    """Unidad de negocio."""
    __tablename__ = "oos_business_units"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("oos_organizations.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    head_id = Column(String(36), nullable=True)
    status = Column(String(20), default="active")
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    organization = relationship("Organization", back_populates="business_units")
    departments = relationship("Department", back_populates="business_unit", cascade="all, delete-orphan")


class Department(OOSBase):
    """Departamento."""
    __tablename__ = "oos_departments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("oos_organizations.id"), nullable=False)
    business_unit_id = Column(String(36), ForeignKey("oos_business_units.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    head_id = Column(String(36), nullable=True)
    status = Column(String(20), default="active")
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    organization = relationship("Organization", back_populates="departments")
    business_unit = relationship("BusinessUnit", back_populates="departments")
    roles = relationship("Role", back_populates="department", cascade="all, delete-orphan")


class Role(OOSBase):
    """Rol organizacional."""
    __tablename__ = "oos_roles"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    department_id = Column(String(36), ForeignKey("oos_departments.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, default=1)
    agent_type = Column(String(50), nullable=True)  # CEO, CFO, COO, etc.
    permissions = Column(JSON, default=list)
    status = Column(String(20), default="active")
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    department = relationship("Department", back_populates="roles")


# ============================================================
# Strategy & Objectives
# ============================================================

class Objective(OOSBase):
    """Objetivo estratégico."""
    __tablename__ = "oos_objectives"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("oos_organizations.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), default="strategic")  # strategic, operational, tactical
    priority = Column(String(20), default="medium")  # critical, high, medium, low
    status = Column(String(20), default="active")  # active, achieved, abandoned, revised
    target_date = Column(DateTime, nullable=True)
    owner_id = Column(String(36), nullable=True)
    progress = Column(Float, default=0.0)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    version = Column(Integer, default=1)

    organization = relationship("Organization", back_populates="objectives")
    kpis = relationship("KPI", back_populates="objective", cascade="all, delete-orphan")
    initiatives = relationship("Initiative", back_populates="objective", cascade="all, delete-orphan")


class KPI(OOSBase):
    """Key Performance Indicator."""
    __tablename__ = "oos_kpis"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("oos_organizations.id"), nullable=False)
    objective_id = Column(String(36), ForeignKey("oos_objectives.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # revenue, pipeline, conversion, etc.
    metric_type = Column(String(20), default="number")  # number, percentage, currency
    current_value = Column(Float, default=0.0)
    target_value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    direction = Column(String(20), default="higher_better")  # higher_better, lower_better
    status = Column(String(20), default="active")  # active, achieved, missed
    history = Column(JSON, default=list)  # [{date, value}]
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    organization = relationship("Organization", back_populates="kpis")
    objective = relationship("Objective", back_populates="kpis")


class Initiative(OOSBase):
    """Iniciativa para lograr un objetivo."""
    __tablename__ = "oos_initiatives"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    objective_id = Column(String(36), ForeignKey("oos_objectives.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="planned")  # planned, in_progress, completed, cancelled
    owner_id = Column(String(36), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    objective = relationship("Objective", back_populates="initiatives")


# ============================================================
# Decisions & Work Orders
# ============================================================

class DecisionRecord(OOSBase):
    """Registro de decisión del Board."""
    __tablename__ = "oos_decisions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("oos_organizations.id"), nullable=False)
    topic = Column(String(500), nullable=False)
    participants = Column(JSON, default=list)
    votes = Column(JSON, default=dict)
    deliberation_summary = Column(Text, nullable=True)
    final_decision = Column(String(20), nullable=False)  # PROCEED, PIVOT, STOP
    final_score = Column(Float, default=0.0)
    final_confidence = Column(Float, default=0.0)
    key_objections = Column(JSON, default=list)
    key_agreements = Column(JSON, default=list)
    dissent_details = Column(Text, nullable=True)
    actions = Column(JSON, default=list)
    follow_up = Column(JSON, default=list)
    status = Column(String(20), default="active")  # active, executed, archived
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    version = Column(Integer, default=1)

    organization = relationship("Organization", back_populates="decisions" if hasattr(Organization, 'decisions') else None)
    work_orders = relationship("WorkOrder", back_populates="decision", cascade="all, delete-orphan")


class WorkOrder(OOSBase):
    """Orden de trabajo generada desde una decisión."""
    __tablename__ = "oos_work_orders"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("oos_organizations.id"), nullable=False)
    decision_id = Column(String(36), ForeignKey("oos_decisions.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="medium")  # critical, high, medium, low
    status = Column(String(20), default="pending")  # pending, assigned, in_progress, blocked, review, completed, cancelled
    assigned_to = Column(String(36), nullable=True)  # role_id or agent
    assigned_to_name = Column(String(200), nullable=True)
    due_date = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)
    dependencies = Column(JSON, default=list)  # [work_order_id]
    blocking_reason = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    version = Column(Integer, default=1)

    organization = relationship("Organization", back_populates="work_orders")
    decision = relationship("DecisionRecord", back_populates="work_orders")
    tasks = relationship("Task", back_populates="work_order", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="work_order", cascade="all, delete-orphan")
    progress_reports = relationship("ProgressReport", back_populates="work_order", cascade="all, delete-orphan")


class Task(OOSBase):
    """Tarea dentro de una Work Order."""
    __tablename__ = "oos_tasks"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    work_order_id = Column(String(36), ForeignKey("oos_work_orders.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    assigned_to = Column(String(36), nullable=True)
    assigned_to_name = Column(String(200), nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    work_order = relationship("WorkOrder", back_populates="tasks")


class Assignment(OOSBase):
    """Asignación de Work Order a un agente/rol."""
    __tablename__ = "oos_assignments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    work_order_id = Column(String(36), ForeignKey("oos_work_orders.id"), nullable=False)
    assigned_to = Column(String(36), nullable=False)
    assigned_to_name = Column(String(200), nullable=False)
    assigned_to_type = Column(String(50), nullable=False)  # agent, role, user
    status = Column(String(20), default="active")
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)

    work_order = relationship("WorkOrder", back_populates="assignments")


class ProgressReport(OOSBase):
    """Reporte de progreso de una Work Order."""
    __tablename__ = "oos_progress_reports"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    work_order_id = Column(String(36), ForeignKey("oos_work_orders.id"), nullable=False)
    reporter_id = Column(String(36), nullable=False)
    reporter_name = Column(String(200), nullable=False)
    progress = Column(Float, default=0.0)
    status_update = Column(String(200), nullable=True)
    problems = Column(JSON, default=list)
    evidence = Column(JSON, default=list)
    next_steps = Column(JSON, default=list)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)

    work_order = relationship("WorkOrder", back_populates="progress_reports")


# ============================================================
# Risk Management
# ============================================================

class Risk(OOSBase):
    """Riesgo identificado."""
    __tablename__ = "oos_risks"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("oos_organizations.id"), nullable=False)
    decision_id = Column(String(36), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # financial, operational, market, technical, legal, people
    probability = Column(String(20), default="medium")  # high, medium, low
    impact = Column(String(20), default="medium")  # high, medium, low
    severity = Column(Float, default=0.0)  # calculated
    status = Column(String(20), default="identified")  # identified, monitoring, mitigated, realized, accepted
    mitigation = Column(Text, nullable=True)
    owner_id = Column(String(36), nullable=True)
    owner_name = Column(String(200), nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    organization = relationship("Organization", back_populates="risks")


# ============================================================
# Meetings
# ============================================================

class Meeting(OOSBase):
    """Reunión del Board."""
    __tablename__ = "oos_meetings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("oos_organizations.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    meeting_type = Column(String(50), default="board")  # board, department, ad_hoc
    participants = Column(JSON, default=list)
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    agenda = Column(JSON, default=list)
    decisions = Column(JSON, default=list)
    action_items = Column(JSON, default=list)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    organization = relationship("Organization", back_populates="meetings")
    minutes = relationship("MeetingMinute", back_populates="meeting", cascade="all, delete-orphan")


class MeetingMinute(OOSBase):
    """Minuta de reunión."""
    __tablename__ = "oos_meeting_minutes"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    meeting_id = Column(String(36), ForeignKey("oos_meetings.id"), nullable=False)
    topic = Column(String(500), nullable=False)
    discussion = Column(Text, nullable=True)
    decision = Column(Text, nullable=True)
    action_item = Column(Text, nullable=True)
    owner = Column(String(200), nullable=True)
    due_date = Column(DateTime, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)

    meeting = relationship("Meeting", back_populates="minutes")
