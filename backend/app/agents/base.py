"""
Agent Base — Framework base para agentes ejecutivos.

Cada agente reutiliza: Cerebro (LLM) + EMS (Memoria) + TEF (Herramientas).
"""

import abc
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.ai.base import LLMAdapter, LLMMessage
from app.ems.memory import EnterpriseMemorySystem
from app.tef.executor import ToolExecutor
from app.tef.interfaces import ToolContext


@dataclass
class AgentMessage:
    """Mensaje interno del agente."""
    role: str                             # system, user, assistant, tool
    content: str
    agent_name: str | None = None
    tool_call: dict | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentPlan:
    """Plan de ejecución del agente."""
    goal: str
    steps: list[dict] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class AgentResponse:
    """Respuesta completa del agente."""
    agent: str
    response: str
    plan: AgentPlan | None = None
    tools_used: list[str] = field(default_factory=list)
    memory_context: str = ""
    justification: str = ""
    confidence: float = 0.0
    events_published: int = 0
    duration_ms: int = 0


class ExecutiveAgent(abc.ABC):
    """
    Framework base para agentes ejecutivos.
    
    Cada agente implementa:
    - system_prompt(): define el rol y comportamiento
    - process(): procesa una solicitud del usuario
    
    Utiliza:
    - LLM (Cerebro) para razonar
    - EMS (Memoria) para recuperar conocimiento
    - TEF (Herramientas) para ejecutar acciones
    """

    def __init__(
        self,
        llm: LLMAdapter,
        ems: EnterpriseMemorySystem,
        tool_executor: ToolExecutor,
    ):
        self.llm = llm
        self.ems = ems
        self.tool_executor = tool_executor

    @abc.abstractmethod
    def system_prompt(self) -> str:
        """Retorna el system prompt del agente."""
        ...

    @abc.abstractmethod
    async def process(
        self,
        message: str,
        company_id: str,
        user_id: str,
        context: dict | None = None,
    ) -> AgentResponse:
        """Procesa una solicitud del usuario."""
        ...

    async def _retrieve_memory(
        self,
        company_id: str,
        query: str,
    ) -> str:
        """Recupera contexto de memoria empresarial."""
        try:
            result = await self.ems.retrieve_for_llm(company_id, query)
            return result
        except Exception:
            return "Sin contexto de memoria disponible."

    async def _execute_tool(
        self,
        tool_id: str,
        params: dict,
        company_id: str,
        user_id: str,
        trace_id: str,
    ) -> dict:
        """Ejecuta una herramienta."""
        context = ToolContext(
            company_id=company_id,
            user_id=user_id,
            trace_id=trace_id,
        )
        result = await self.tool_executor.execute(tool_id, params, context)
        return {
            "status": result.status,
            "output": result.output,
            "error": result.error,
        }

    async def _llm_chat(
        self,
        messages: list[AgentMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Ejecuta una conversación con el LLM."""
        llm_messages = [
            LLMMessage(role=m.role, content=m.content)
            for m in messages
        ]
        response = await self.llm.chat(
            messages=llm_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content

    def _build_context(
        self,
        memory_context: str,
        tool_results: list[dict],
        user_message: str,
    ) -> str:
        """Construye el contexto combinado para el LLM."""
        parts = []

        if memory_context and memory_context != "Sin contexto de memoria disponible.":
            parts.append(f"CONOCIMIENTO DE LA EMPRESA:\n{memory_context}")

        if tool_results:
            parts.append("RESULTADOS DE HERRAMIENTAS:")
            for tr in tool_results:
                parts.append(f"  - {tr.get('tool_id', '?')}: {tr.get('status', '?')}")
                if tr.get("output"):
                    output_str = str(tr["output"])[:500]
                    parts.append(f"    Output: {output_str}")

        parts.append(f"PREGUNTA DEL USUARIO: {user_message}")

        return "\n\n".join(parts)
