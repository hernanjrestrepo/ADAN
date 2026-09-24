"""Herramientas reales de Agente sobre el Knowledge Graph y la memoria semantica -
WO-003 Sprint 4. Cierra el MemoryHook que el runtime de agentes (WO-002 Sprint 2) dejo
preparado sin implementacion real.

Permisos por Agente: AgentDefinition.allowed_tools (WO-002 Sprint 2, agents/base.py)
declara que herramientas puede usar cada Agente - kg_write en particular se restringe,
porque escribir en el grafo es una accion con efecto permanente (AD-002 regla 1.5, nada
se pierde) y no todo Agente deberia poder hacerlo sin razon explicita."""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from memory.hybrid_query import HybridResult, hybrid_query
from memory.ingestion import ingest_text
from memory.repository import create_edge, create_node, traverse
from models.base import ModelBackend

ALL_TOOL_NAMES = {"kg_read", "kg_write", "memory_search", "memory_store"}


class ToolPermissionError(Exception):
    def __init__(self, agent_id: str, tool_name: str):
        super().__init__(f"Agent '{agent_id}' is not allowed to use tool '{tool_name}'")
        self.agent_id = agent_id
        self.tool_name = tool_name


def check_permission(agent_id: str, allowed_tools: list[str], tool_name: str) -> None:
    if tool_name not in allowed_tools:
        raise ToolPermissionError(agent_id, tool_name)


@dataclass
class AgentTools:
    """Conjunto de herramientas ligado a un Agente concreto - cada llamada verifica
    permiso antes de tocar la base de datos."""

    db: Session
    model_backend: ModelBackend
    agent_id: str
    allowed_tools: list[str]

    def kg_read(self, node_id: uuid.UUID, max_depth: int = 1) -> dict:
        check_permission(self.agent_id, self.allowed_tools, "kg_read")
        return traverse(self.db, node_id, max_depth=max_depth)

    def kg_write(
        self,
        tipo: str,
        nombre: str,
        proyecto_id: uuid.UUID | None = None,
        relacionado_con: uuid.UUID | None = None,
        tipo_relacion: str = "relacionado_con",
    ) -> uuid.UUID:
        check_permission(self.agent_id, self.allowed_tools, "kg_write")
        node = create_node(self.db, tipo=tipo, nombre=nombre, proyecto_id=proyecto_id)
        if relacionado_con is not None:
            create_edge(self.db, relacionado_con, node.id, tipo_relacion)
        return node.id

    def memory_search(self, query: str, proyecto_id: uuid.UUID | None = None, top_k: int = 5) -> list[HybridResult]:
        check_permission(self.agent_id, self.allowed_tools, "memory_search")
        return hybrid_query(self.db, self.model_backend, query, proyecto_id=proyecto_id, top_k_semantic=top_k)

    def memory_store(self, text: str, origen: str, proyecto_id: uuid.UUID | None = None) -> int:
        check_permission(self.agent_id, self.allowed_tools, "memory_store")
        rows = ingest_text(self.db, self.model_backend, text, origen=origen, proyecto_id=proyecto_id)
        return len(rows)
