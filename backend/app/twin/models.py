"""Entidades del Gemelo Digital que faltaban en Build C (WO-098).

AD-005 define 26 entidades de negocio y AD-006 v1.2 agrega 12 operativas: 38 en total.
Build C tenía 11 (Empresa, Narrativa Fundacional, Documento, Usuario, Proyecto, Nivel,
Card, Conversación, Score, Decisión y Evento). Aquí están las 26 restantes:

- 23 de negocio (AD-005 §2): Marca, Accionista, Departamento, Cargo, Rol Funcional,
  Empleado, Cliente Final, Producto/Servicio, Mercado, Competidor, Proveedor, Proceso,
  Iniciativa, Suceso Empresarial, Contrato, Objetivo, Meta, Indicador, Decisión de
  Negocio, Activo, Pasivo, Ingreso y Gasto.
- 3 operativas (AD-006 §4): Workspace, Agente y Tarea.

Más dos estructuras que no son entidades: Riesgo (propiedad transversal polimórfica,
AD-005 §3) y la tabla de versiones (Contrato Base, AD-002 regla 1.7).

Decisiones de traducción (registradas en docs/wo/WO-098_REPORTE.md):
- Nombres de tablas y columnas en inglés, como el resto de Build C; los nombres de
  dominio en español viven en el catálogo de la API (app/twin/registry.py).
- Toda entidad de negocio lleva `company_id`, aunque cuelgue de otra (Cargo de
  Departamento, Meta de Objetivo): el Gemelo es el límite de agregación (AD-007 §1) y
  así la autorización por empresa es una sola condición.
- Accionista y Mercado son N:M con Empresa en AD-006, pero un registro de otra empresa
  cruzaría la frontera del Gemelo; se modelan por empresa hasta que exista multiempresa
  (WO-101).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, Table, Text, Boolean,
    UniqueConstraint,
)

from app.core.database import Base, JSONType


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


# Estados de los Patrones de AD-008
class PatternA:
    """Ciclo de Aprobación: Propuesto → (Presentado) → Aprobado / Rechazado → Ejecutado."""
    PROPOSED = "proposed"
    PRESENTED = "presented"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


class PatternB:
    """Progreso Secuencial: Bloqueado → Activo → Completado."""
    BLOCKED = "blocked"
    ACTIVE = "active"
    COMPLETED = "completed"


class PatternD:
    """Contenedor Continuo: Activo → Pausado → Archivado."""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ContratoBase:
    """Contrato Base de AD-006 §2, heredado por toda entidad del Gemelo.

    | Atributo | Regla de AD-002 |
    |---|---|
    | id | — |
    | version (+ tabla entity_versions) | 1.7 Todo tiene versión |
    | status: active / archived, nunca se borra | 1.5 Nada se pierde |
    | updated_by: responsable del último cambio | 1.4 Toda decisión tiene responsable |
    | evidence_source | 1.1 Todo genera evidencia |
    | confidence_level | 1.9 Nivel de confianza declarado |
    | reasoning | 1.6 Toda IA debe justificar |

    `version`, `updated_by` y la historia los mantiene el hook de app/twin/hooks.py.
    """

    # Patrón de AD-008 ("A", "B", "C" o "D"); None = solo el Contrato Base
    __pattern__: str | None = None
    # Columna que guarda el estado del patrón (A y B: "state"; D: "status")
    __state_attr__: str | None = None

    id = Column(String(36), primary_key=True, default=gen_uuid)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active | archived
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)   # actor que lo creó (user:<id>, agent:<nombre>, system)
    updated_by = Column(String(120), nullable=True)   # responsable del último cambio
    evidence_source = Column(Text, nullable=True)
    confidence_level = Column(Float, nullable=True)   # 0-100, cuando proviene de una inferencia
    reasoning = Column(Text, nullable=True)           # razonamiento, cuando lo generó un Agente


def _company_fk():
    return Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)


# ============================================================
# AD-005 §2.1 Identidad y Gobernanza
# ============================================================

class Brand(ContratoBase, Base):
    """Marca — 1:N con Empresa. Su Reputación es un Intangible (AD-005 §3, §6)."""
    __tablename__ = "brands"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    positioning = Column(Text, nullable=True)
    reputation = Column(Text, nullable=True)  # atributo intangible (es_intangible)


class Shareholder(ContratoBase, Base):
    """Accionista / Inversionista."""
    __tablename__ = "shareholders"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    participation_type = Column(String(100), nullable=True)  # acciones, deuda convertible, SAFE…
    participation_pct = Column(Float, nullable=True)
    since = Column(Date, nullable=True)


# ============================================================
# AD-005 §2.2 Estructura Organizacional y Personas
# ============================================================

class CompanyDepartment(ContratoBase, Base):
    """Departamento — 1:N con Empresa, con jerarquía (auto-relación)."""
    __tablename__ = "departments"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    function = Column(Text, nullable=True)
    parent_id = Column(String(36), ForeignKey("departments.id"), nullable=True)


position_roles = Table(
    "position_roles",
    Base.metadata,
    Column("position_id", String(36), ForeignKey("positions.id"), primary_key=True),
    Column("functional_role_id", String(36), ForeignKey("functional_roles.id"), primary_key=True),
)


class Position(ContratoBase, Base):
    """Cargo — 1:N con Departamento; puede reportar a otro Cargo."""
    __tablename__ = "positions"

    company_id = _company_fk()
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False)
    name = Column(String(255), nullable=False)
    hierarchy_level = Column(Integer, nullable=True)
    reports_to_id = Column(String(36), ForeignKey("positions.id"), nullable=True)


class FunctionalRole(ContratoBase, Base):
    """Rol Funcional — N:M con Cargo (tabla position_roles)."""
    __tablename__ = "functional_roles"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)


class Employee(ContratoBase, Base):
    """Empleado — 1:N con Empresa. El historial de Cargos sale de entity_versions."""
    __tablename__ = "employees"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    position_id = Column(String(36), ForeignKey("positions.id"), nullable=True)
    hired_on = Column(Date, nullable=True)


# ============================================================
# AD-005 §2.3 Mercado y Comercial
# ============================================================

class EndCustomer(ContratoBase, Base):
    """Cliente Final — 1:N con Empresa. La Confianza es un atributo intangible."""
    __tablename__ = "end_customers"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    segment = Column(String(255), nullable=True)
    relationship_notes = Column(Text, nullable=True)
    trust = Column(Text, nullable=True)  # atributo intangible


class Offering(ContratoBase, Base):
    """Producto / Servicio — 1:N con Empresa."""
    __tablename__ = "offerings"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    kind = Column(String(20), nullable=True)  # producto | servicio
    category = Column(String(255), nullable=True)
    value_proposition = Column(Text, nullable=True)
    market_id = Column(String(36), ForeignKey("markets.id"), nullable=True)


class Market(ContratoBase, Base):
    """Mercado — el espacio de intercambio donde la Empresa y sus Competidores operan."""
    __tablename__ = "markets"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    segment_definition = Column(Text, nullable=True)
    size = Column(String(100), nullable=True)
    trends = Column(Text, nullable=True)


class Competitor(ContratoBase, Base):
    """Competidor — relación ternaria con Empresa y Mercado (AD-005 §2.3)."""
    __tablename__ = "competitors"

    company_id = _company_fk()
    market_id = Column(String(36), ForeignKey("markets.id"), nullable=False)
    name = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)


class Supplier(ContratoBase, Base):
    """Proveedor — N:1 con Empresa; la criticidad es atributo de la relación."""
    __tablename__ = "suppliers"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    supplies = Column(Text, nullable=True)
    criticality = Column(String(20), nullable=True)  # baja | media | alta


# ============================================================
# AD-005 §2.4 Operación
# ============================================================

class Process(ContratoBase, Base):
    """Proceso — secuencia repetible de actividad; puede originar Iniciativas."""
    __tablename__ = "processes"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    objective = Column(Text, nullable=True)
    frequency = Column(String(100), nullable=True)


class CompanyInitiative(ContratoBase, Base):
    """Iniciativa — esfuerzo delimitado en el tiempo (nunca "Proyecto"). Patrón A.

    `spun_off_company_id`: si la Iniciativa se separó como Empresa nueva (AD-CMP-06 §4),
    la referencia "separada hacia" que nunca se borra.
    """
    __tablename__ = "initiatives"
    __pattern__ = "A"
    __state_attr__ = "state"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    objective = Column(Text, nullable=True)
    budget = Column(Float, nullable=True)
    process_id = Column(String(36), ForeignKey("processes.id"), nullable=True)
    state = Column(String(20), default=PatternA.PROPOSED, nullable=False)
    spun_off_company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)


class BusinessOccurrence(ContratoBase, Base):
    """Suceso Empresarial — algo que ocurrió (nunca "Evento"). Patrón C: no se edita."""
    __tablename__ = "business_occurrences"
    __pattern__ = "C"

    company_id = _company_fk()
    title = Column(String(255), nullable=False)
    nature = Column(String(20), nullable=False, default="rutinario")  # rutinario | critico | fundacional
    occurred_on = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    business_decision_id = Column(String(36), ForeignKey("business_decisions.id"), nullable=True)


contract_documents = Table(
    "contract_documents",
    Base.metadata,
    Column("contract_id", String(36), ForeignKey("business_contracts.id"), primary_key=True),
    Column("document_id", String(36), ForeignKey("documents.id"), primary_key=True),
)


class BusinessContract(ContratoBase, Base):
    """Contrato (de negocio) — con un Proveedor, Cliente Final, Empleado o Socio. Patrón A."""
    __tablename__ = "business_contracts"
    __pattern__ = "A"
    __state_attr__ = "state"

    company_id = _company_fk()
    title = Column(String(255), nullable=False)
    counterparty_type = Column(String(20), nullable=False)  # proveedor | cliente | empleado | socio
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True)
    end_customer_id = Column(String(36), ForeignKey("end_customers.id"), nullable=True)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=True)
    counterparty_name = Column(String(255), nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    state = Column(String(20), default=PatternA.PROPOSED, nullable=False)


# ============================================================
# AD-005 §2.5 Dirección y Evidencia
# ============================================================

class CompanyObjective(ContratoBase, Base):
    """Objetivo — declaración cualitativa de dirección estratégica."""
    __tablename__ = "objectives"

    company_id = _company_fk()
    statement = Column(Text, nullable=False)
    horizon = Column(String(50), nullable=True)


class Goal(ContratoBase, Base):
    """Meta — cuantificación de un Objetivo (equivalente a un Key Result)."""
    __tablename__ = "goals"

    company_id = _company_fk()
    objective_id = Column(String(36), ForeignKey("objectives.id"), nullable=False)
    description = Column(Text, nullable=False)
    target_value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    due_on = Column(Date, nullable=True)


class Indicator(ContratoBase, Base):
    """Indicador — lo que se mide para verificar una Meta (KPI es un tipo, no otra entidad)."""
    __tablename__ = "indicators"

    company_id = _company_fk()
    goal_id = Column(String(36), ForeignKey("goals.id"), nullable=False)
    name = Column(String(255), nullable=False)
    kind = Column(String(20), nullable=True)  # kpi | otro
    formula = Column(Text, nullable=True)
    frequency = Column(String(50), nullable=True)
    current_value = Column(Float, nullable=True)


class BusinessDecision(ContratoBase, Base):
    """Decisión de Negocio — elección real de la Empresa (distinta de la Decisión de ADÁN). Patrón A.

    `adan_decision_id`: la Decisión de ADÁN que la originó, si existe (AD-CMP-03 §4).
    Relación explícita, nunca fusión.
    """
    __tablename__ = "business_decisions"
    __pattern__ = "A"
    __state_attr__ = "state"

    company_id = _company_fk()
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    decided_by_employee_id = Column(String(36), ForeignKey("employees.id"), nullable=True)
    learning_loop = Column(String(10), nullable=True)  # simple | doble (Ley 2)
    adan_decision_id = Column(String(36), ForeignKey("decisions.id"), nullable=True)
    state = Column(String(20), default=PatternA.PROPOSED, nullable=False)


# ============================================================
# AD-005 §2.6 Finanzas
# ============================================================

class Asset(ContratoBase, Base):
    """Activo — algo de valor que la Empresa posee."""
    __tablename__ = "assets"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    kind = Column(String(100), nullable=True)
    value = Column(Float, nullable=True)
    liquidity = Column(String(20), nullable=True)  # alta | media | baja (Ley 6)


class Liability(ContratoBase, Base):
    """Pasivo — una obligación de la Empresa."""
    __tablename__ = "liabilities"

    company_id = _company_fk()
    name = Column(String(255), nullable=False)
    kind = Column(String(100), nullable=True)
    amount = Column(Float, nullable=True)
    term = Column(String(50), nullable=True)


class Revenue(ContratoBase, Base):
    """Ingreso — valor que entra a la Empresa."""
    __tablename__ = "revenues"

    company_id = _company_fk()
    source = Column(String(255), nullable=False)
    amount = Column(Float, nullable=True)
    periodicity = Column(String(50), nullable=True)


class Expense(ContratoBase, Base):
    """Gasto — valor que sale de la Empresa."""
    __tablename__ = "expenses"

    company_id = _company_fk()
    category = Column(String(255), nullable=False)
    amount = Column(Float, nullable=True)
    periodicity = Column(String(50), nullable=True)


# ============================================================
# AD-005 §3 Propiedad transversal: Riesgo (polimórfica)
# ============================================================

class TwinRisk(ContratoBase, Base):
    """Riesgo — se predica de Empresa, Proceso, Iniciativa o Contrato (no es una entidad núcleo).

    Se modela como tabla polimórfica (`subject_type`, `subject_id`) en lugar de una FK por
    entidad, igual que Score con su sujeto (AD-006 v1.2 Hallazgo 4).
    """
    __tablename__ = "twin_risks"

    company_id = _company_fk()
    subject_type = Column(String(30), nullable=False)  # company | process | initiative | contract | decision
    subject_id = Column(String(36), nullable=False)
    kind = Column(String(30), nullable=False)  # legal | financiero | operativo | reputacional | mercado | otro
    description = Column(Text, nullable=False)
    severity = Column(String(10), nullable=True)  # baja | media | alta
    probability = Column(Float, nullable=True)  # 0-1
    materialized = Column(Boolean, default=False, nullable=False)

    __table_args__ = (Index("idx_twin_risks_subject", "subject_type", "subject_id"),)


# ============================================================
# AD-006 §4 Entidades operativas que faltaban
# ============================================================

class Workspace(ContratoBase, Base):
    """Workspace — la interfaz que envuelve un Proyecto (1:1). Patrón D."""
    __tablename__ = "workspaces"
    __pattern__ = "D"
    __state_attr__ = "status"

    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, unique=True)
    company_id = _company_fk()
    preferences = Column(JSONType, nullable=True)


class Agent(ContratoBase, Base):
    """Agente — rol interno especializado (los 7 del Board y ADÁN). Catálogo global."""
    __tablename__ = "agents"

    code = Column(String(20), nullable=False, unique=True)  # CEO, CFO, COO, CMO, CTO, CLO, CHRO, ADAN
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)


conversation_agents = Table(
    "conversation_agents",
    Base.metadata,
    Column("conversation_id", String(36), ForeignKey("conversations.id"), primary_key=True),
    Column("agent_id", String(36), ForeignKey("agents.id"), primary_key=True),
)


class LevelTask(ContratoBase, Base):
    """Tarea — unidad operativa de trabajo dentro de un Nivel o una Card. Patrón B."""
    __tablename__ = "tasks"
    __pattern__ = "B"
    __state_attr__ = "state"

    company_id = _company_fk()
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    level_id = Column(String(36), ForeignKey("levels.id"), nullable=False)
    card_id = Column(String(36), ForeignKey("cards.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    state = Column(String(20), default=PatternB.BLOCKED, nullable=False)


# ============================================================
# Historia de versiones (Contrato Base, AD-002 regla 1.7) — append-only
# ============================================================

class EntityVersion(Base):
    """Una fila por cada versión de cada entidad del Gemelo: qué cambió, quién y por qué.

    Append-only: el ORM lo impide (hooks.py) y, en bases migradas, también triggers.
    """
    __tablename__ = "entity_versions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    version = Column(Integer, nullable=False)
    change = Column(String(20), nullable=False)  # created | updated | archived | restored
    changes = Column(JSONType, nullable=True)    # {campo: [antes, después]}
    snapshot = Column(JSONType, nullable=False)  # estado completo tras el cambio
    actor_type = Column(String(10), nullable=False)  # user | agent | system
    actor_id = Column(String(120), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "version", name="uq_entity_version"),
        Index("idx_entity_versions_entity", "entity_type", "entity_id"),
    )


# ============================================================
# Linaje del Gemelo (AD-CMP-06 §4-5): división y fusión por referencia, no por copia
# ============================================================

class TwinLineage(Base):
    """Relación entre Gemelos: `company_id` nació de `source_company_id`.

    relation: "split_from" (se separó de una Iniciativa de la fuente) o "merged_from" (una
    de las Empresas que se fusionaron). Append-only, como el resto del historial.
    """
    __tablename__ = "twin_lineage"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    source_company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    relation = Column(String(20), nullable=False)  # split_from | merged_from
    initiative_id = Column(String(36), ForeignKey("initiatives.id"), nullable=True)
    note = Column(Text, nullable=True)
    actor_type = Column(String(10), nullable=False)
    actor_id = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)


# Las reglas del Gemelo (patrones, versionado, eventos) se registran con los modelos
from app.twin import hooks as _hooks  # noqa: E402,F401
