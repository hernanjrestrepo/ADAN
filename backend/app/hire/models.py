"""Agentes por tiempo (WO-109, AD-DEC-0002 decisión 1): catálogo, contratos y registro de trabajo.

- `hire_offerings`: el catálogo de agentes que ADÁN suministra (rol, habilidades, herramientas de
  TEF y nivel de modelo de WO-099). Lleva a persistencia la `agent_factory`, que solo existía en
  memoria.
- `hire_contracts`: contratación por hora, día, semana o mes. La capacidad se mide en horas de
  trabajo efectivo del agente. El precio lo fija WO-100: aquí no se inventa.
- `hire_work_logs`: cada ejecución deja su constancia (Registro Permanente): tiempo real, tokens,
  costo del modelo para ADÁN y herramientas usadas. De ahí sale el reporte al cliente.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.core.database import Base, JSONType


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


# Horas de trabajo efectivo que incluye cada unidad de período
PERIOD_HOURS = {"hour": 1, "day": 8, "week": 40, "month": 160}


class AgentOffering(Base):
    __tablename__ = "hire_offerings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    role = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    skills = Column(JSONType, nullable=False, default=list)
    tools = Column(JSONType, nullable=False, default=list)  # ids de TEF
    tier = Column(String(20), nullable=False, default="standard")  # simple | fast | standard | complex
    system_prompt = Column(Text, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)


class AgentContract(Base):
    __tablename__ = "hire_contracts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    offering_id = Column(String(36), ForeignKey("hire_offerings.id"), nullable=False)
    period = Column(String(10), nullable=False)  # hour | day | week | month
    units = Column(Integer, nullable=False)
    hours_capacity = Column(Float, nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active | cancelled
    hired_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    price_note = Column(String(200), nullable=False, default="Precio por definir (WO-100)")
    created_at = Column(DateTime, default=utcnow, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)


class AgentWorkLog(Base):
    __tablename__ = "hire_work_logs"
    __pattern__ = "C"  # constancia de trabajo: no se edita ni se borra

    id = Column(String(36), primary_key=True, default=gen_uuid)
    contract_id = Column(String(36), ForeignKey("hire_contracts.id"), nullable=False, index=True)
    work_order_id = Column(String(36), ForeignKey("oos_work_orders.id"), nullable=False)
    started_at = Column(DateTime, nullable=False)
    seconds = Column(Float, nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    model = Column(String(120), nullable=True)
    degraded = Column(Boolean, default=False, nullable=False)
    tools_used = Column(JSONType, nullable=False, default=list)
    outcome = Column(String(20), nullable=False)  # delivered | failed
    created_at = Column(DateTime, default=utcnow, nullable=False)
