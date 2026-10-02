"""Catálogo de las entidades de negocio del Gemelo expuestas por la API (WO-098).

Cada tipo define: el modelo, su nombre en el lenguaje del producto (AD-003), los campos
editables y a qué otra entidad de la misma empresa apunta cada referencia. La API
(app/twin/api.py) es genérica sobre este catálogo: agregar una entidad es agregar una
entrada aquí, no un router nuevo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from app.twin import models as m


@dataclass(frozen=True)
class Field:
    type: type
    required: bool = False
    max_length: int | None = None
    choices: tuple[str, ...] | None = None
    ref: str | None = None  # tipo del catálogo al que apunta (misma empresa)


@dataclass(frozen=True)
class EntityKind:
    key: str
    model: type
    label: str
    label_plural: str
    cluster: str
    fields: dict[str, Field] = field(default_factory=dict)

    @property
    def pattern(self) -> str | None:
        return getattr(self.model, "__pattern__", None)

    @property
    def state_attr(self) -> str | None:
        return getattr(self.model, "__state_attr__", None)


def _s(max_length: int = 255, required: bool = False, choices: tuple[str, ...] | None = None) -> Field:
    return Field(str, required=required, max_length=max_length, choices=choices)


TEXT = Field(str, max_length=20000)
NUMBER = Field(float)
INTEGER = Field(int)
DATE = Field(date)

PATTERN_A_STATES = ("proposed", "presented", "approved", "rejected", "executed")

KINDS: dict[str, EntityKind] = {k.key: k for k in [
    # AD-005 §2.1 Identidad y Gobernanza
    EntityKind("brands", m.Brand, "Marca", "Marcas", "identidad", {
        "name": _s(required=True), "positioning": TEXT, "reputation": TEXT}),
    EntityKind("shareholders", m.Shareholder, "Accionista o Inversionista", "Accionistas e Inversionistas", "identidad", {
        "name": _s(required=True), "participation_type": _s(100), "participation_pct": NUMBER, "since": DATE}),
    # AD-005 §2.2 Estructura Organizacional y Personas
    EntityKind("departments", m.CompanyDepartment, "Departamento", "Departamentos", "organizacion", {
        "name": _s(required=True), "function": TEXT, "parent_id": Field(str, ref="departments")}),
    EntityKind("positions", m.Position, "Cargo", "Cargos", "organizacion", {
        "name": _s(required=True), "department_id": Field(str, required=True, ref="departments"),
        "hierarchy_level": INTEGER, "reports_to_id": Field(str, ref="positions")}),
    EntityKind("functional_roles", m.FunctionalRole, "Rol Funcional", "Roles Funcionales", "organizacion", {
        "name": _s(required=True), "description": TEXT, "skills": TEXT}),
    EntityKind("employees", m.Employee, "Empleado", "Empleados", "organizacion", {
        "name": _s(required=True), "position_id": Field(str, ref="positions"), "hired_on": DATE}),
    # AD-005 §2.3 Mercado y Comercial
    EntityKind("end_customers", m.EndCustomer, "Cliente Final", "Clientes Finales", "mercado", {
        "name": _s(required=True), "segment": _s(), "relationship_notes": TEXT, "trust": TEXT}),
    EntityKind("offerings", m.Offering, "Producto o Servicio", "Productos y Servicios", "mercado", {
        "name": _s(required=True), "kind": _s(20, choices=("producto", "servicio")), "category": _s(),
        "value_proposition": TEXT, "market_id": Field(str, ref="markets")}),
    EntityKind("markets", m.Market, "Mercado", "Mercados", "mercado", {
        "name": _s(required=True), "segment_definition": TEXT, "size": _s(100), "trends": TEXT}),
    EntityKind("competitors", m.Competitor, "Competidor", "Competidores", "mercado", {
        "name": _s(required=True), "market_id": Field(str, required=True, ref="markets"), "notes": TEXT}),
    EntityKind("suppliers", m.Supplier, "Proveedor", "Proveedores", "mercado", {
        "name": _s(required=True), "supplies": TEXT, "criticality": _s(20, choices=("baja", "media", "alta"))}),
    # AD-005 §2.4 Operación
    EntityKind("processes", m.Process, "Proceso", "Procesos", "operacion", {
        "name": _s(required=True), "objective": TEXT, "frequency": _s(100)}),
    EntityKind("initiatives", m.CompanyInitiative, "Iniciativa", "Iniciativas", "operacion", {
        "name": _s(required=True), "objective": TEXT, "budget": NUMBER,
        "process_id": Field(str, ref="processes"), "state": _s(20, choices=PATTERN_A_STATES)}),
    EntityKind("business_occurrences", m.BusinessOccurrence, "Suceso Empresarial", "Sucesos Empresariales", "operacion", {
        "title": _s(required=True), "nature": _s(20, choices=("rutinario", "critico", "fundacional")),
        "occurred_on": DATE, "description": TEXT,
        "business_decision_id": Field(str, ref="business_decisions")}),
    EntityKind("business_contracts", m.BusinessContract, "Contrato", "Contratos", "operacion", {
        "title": _s(required=True),
        "counterparty_type": _s(20, required=True, choices=("proveedor", "cliente", "empleado", "socio")),
        "supplier_id": Field(str, ref="suppliers"), "end_customer_id": Field(str, ref="end_customers"),
        "employee_id": Field(str, ref="employees"), "counterparty_name": _s(),
        "valid_from": DATE, "valid_to": DATE, "state": _s(20, choices=PATTERN_A_STATES)}),
    # AD-005 §2.5 Dirección y Evidencia
    EntityKind("objectives", m.CompanyObjective, "Objetivo", "Objetivos", "direccion", {
        "statement": Field(str, required=True, max_length=5000), "horizon": _s(50)}),
    EntityKind("goals", m.Goal, "Meta", "Metas", "direccion", {
        "objective_id": Field(str, required=True, ref="objectives"),
        "description": Field(str, required=True, max_length=5000),
        "target_value": NUMBER, "unit": _s(50), "due_on": DATE}),
    EntityKind("indicators", m.Indicator, "Indicador", "Indicadores", "direccion", {
        "goal_id": Field(str, required=True, ref="goals"), "name": _s(required=True),
        "kind": _s(20, choices=("kpi", "otro")), "formula": TEXT, "frequency": _s(50), "current_value": NUMBER}),
    EntityKind("business_decisions", m.BusinessDecision, "Decisión de Negocio", "Decisiones de Negocio", "direccion", {
        "title": _s(required=True), "description": TEXT,
        "decided_by_employee_id": Field(str, ref="employees"),
        "learning_loop": _s(10, choices=("simple", "doble")), "state": _s(20, choices=PATTERN_A_STATES)}),
    # AD-005 §2.6 Finanzas
    EntityKind("assets", m.Asset, "Activo", "Activos", "finanzas", {
        "name": _s(required=True), "kind": _s(100), "value": NUMBER,
        "liquidity": _s(20, choices=("alta", "media", "baja"))}),
    EntityKind("liabilities", m.Liability, "Pasivo", "Pasivos", "finanzas", {
        "name": _s(required=True), "kind": _s(100), "amount": NUMBER, "term": _s(50)}),
    EntityKind("revenues", m.Revenue, "Ingreso", "Ingresos", "finanzas", {
        "source": _s(required=True), "amount": NUMBER, "periodicity": _s(50)}),
    EntityKind("expenses", m.Expense, "Gasto", "Gastos", "finanzas", {
        "category": _s(required=True), "amount": NUMBER, "periodicity": _s(50)}),
    # AD-005 §3 Propiedad transversal
    EntityKind("risks", m.TwinRisk, "Riesgo", "Riesgos", "transversal", {
        "subject_type": _s(30, required=True, choices=("company", "process", "initiative", "contract")),
        "subject_id": Field(str, required=True),
        "kind": _s(30, required=True, choices=("legal", "financiero", "operativo", "reputacional", "mercado", "otro")),
        "description": Field(str, required=True, max_length=5000),
        "severity": _s(10, choices=("baja", "media", "alta")), "probability": NUMBER,
        "materialized": Field(bool)}),
]}

# Campos del Contrato Base que el cliente o un agente pueden declarar (AD-006 §2)
CONTRACT_FIELDS: dict[str, Field] = {
    "evidence_source": TEXT,
    "confidence_level": NUMBER,
    "reasoning": TEXT,
}

# Sujetos válidos de un Riesgo → tipo del catálogo (o la propia Empresa)
RISK_SUBJECTS = {"process": "processes", "initiative": "initiatives", "contract": "business_contracts"}

CLUSTERS = {
    "identidad": "Identidad y Gobernanza",
    "organizacion": "Estructura Organizacional y Personas",
    "mercado": "Mercado y Comercial",
    "operacion": "Operación",
    "direccion": "Dirección y Evidencia",
    "finanzas": "Finanzas",
    "transversal": "Propiedades transversales",
}


def kind_or_none(key: str) -> EntityKind | None:
    return KINDS.get(key)


def describe(kind: EntityKind) -> dict[str, Any]:
    return {
        "key": kind.key,
        "label": kind.label,
        "label_plural": kind.label_plural,
        "cluster": kind.cluster,
        "cluster_label": CLUSTERS[kind.cluster],
        "pattern": kind.pattern,
        "fields": {
            name: {
                "type": f.type.__name__,
                "required": f.required,
                **({"choices": list(f.choices)} if f.choices else {}),
                **({"ref": f.ref} if f.ref else {}),
            }
            for name, f in kind.fields.items()
        },
    }
