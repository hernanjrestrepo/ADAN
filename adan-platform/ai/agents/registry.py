"""Registro de Agentes disponibles - AD-003 entidad Agente, instancias concretas
(CEO/CTO/CFO/Diagnostico...). Sprint 4 agrega el primero real (Agente de Diagnostico,
Nivel 1 - El Dolor); este modulo existe desde Sprint 3 para que el worker tenga un punto
de resolucion agent_id -> AgentDefinition sin acoplarse a un agente especifico."""

from agents.base import AgentDefinition

_REGISTRY: dict[str, AgentDefinition] = {}


def register_agent(definition: AgentDefinition) -> None:
    _REGISTRY[definition.agent_id] = definition


def get_agent_definition(agent_id: str) -> AgentDefinition | None:
    return _REGISTRY.get(agent_id)


def list_agent_ids() -> list[str]:
    return list(_REGISTRY.keys())
