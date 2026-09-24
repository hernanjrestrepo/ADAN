"""
Agent Factory — Construye agentes mediante configuración.

Sin escribir código nuevo. Solo definir: name, personality, tools, permissions, goals.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from app.ai.base import LLMAdapter, LLMMessage
from app.ems.memory import EnterpriseMemorySystem
from app.tef.executor import ToolExecutor
from app.agents.base import ExecutiveAgent, AgentMessage, AgentPlan, AgentResponse


@dataclass
class AgentConfig:
    """Configuración de un agente."""
    name: str
    role: str
    personality: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    kpis: list[str] = field(default_factory=list)
    memory_focus: list[str] = field(default_factory=list)


class ConfigurableAgent(ExecutiveAgent):
    """Agente configurable desde AgentConfig."""

    def __init__(
        self,
        config: AgentConfig,
        llm: LLMAdapter,
        ems: EnterpriseMemorySystem,
        tool_executor: ToolExecutor,
    ):
        super().__init__(llm, ems, tool_executor)
        self.config = config

    def system_prompt(self) -> str:
        return self.config.system_prompt

    async def process(
        self,
        message: str,
        company_id: str,
        user_id: str,
        context: dict | None = None,
    ) -> AgentResponse:
        """Procesa una solicitud usando la configuración del agente."""
        import time
        start_time = time.time()

        # Recuperar memoria
        memory_context = ""
        try:
            memory_context = await self.ems.retrieve_for_llm(company_id, message)
        except Exception:
            pass

        # Construir contexto
        context_parts = []
        if memory_context:
            context_parts.append(f"CONOCIMIENTO:\n{memory_context[:1500]}")
        context_parts.append(f"SOLICITUD: {message}")

        full_context = "\n\n".join(context_parts)

        # Generar respuesta
        messages = [
            AgentMessage(role="system", content=self.system_prompt()),
            AgentMessage(role="user", content=full_context),
        ]

        response_text = await self._llm_chat(messages, temperature=0.7, max_tokens=2048)

        duration_ms = int((time.time() - start_time) * 1000)

        return AgentResponse(
            agent=self.config.name.lower().replace(" ", "_"),
            response=response_text,
            plan=AgentPlan(goal=response_text[:200], steps=[], reasoning=response_text),
            tools_used=[],
            memory_context=memory_context[:500] if memory_context else "",
            justification=response_text,
            confidence=0.7,
            duration_ms=duration_ms,
        )


class AgentFactory:
    """
    Fábrica que construye agentes desde configuración.
    
    Ejemplo:
        factory = AgentFactory(llm, ems, executor)
        agent = factory.create(AgentConfig(
            name="Finance Director",
            role="CFO",
            personality="Analítico, conservador, enfocado en ROI",
            system_prompt="Eres el CFO...",
            tools=["sql_query", "calculator"],
            goals=["Optimizar flujo de caja", "Reducir costos"],
        ))
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
        self._agents: dict[str, ConfigurableAgent] = {}

    def create(self, config: AgentConfig) -> ConfigurableAgent:
        """Crea un agente desde configuración."""
        agent = ConfigurableAgent(
            config=config,
            llm=self.llm,
            ems=self.ems,
            tool_executor=self.tool_executor,
        )
        self._agents[config.name.lower().replace(" ", "_")] = agent
        return agent

    def get(self, agent_id: str) -> ConfigurableAgent | None:
        """Obtiene un agente por ID."""
        return self._agents.get(agent_id)

    def list_all(self) -> list[dict]:
        """Lista todos los agentes creados."""
        return [
            {
                "id": agent_id,
                "name": agent.config.name,
                "role": agent.config.role,
                "tools": agent.config.tools,
                "goals": agent.config.goals,
            }
            for agent_id, agent in self._agents.items()
        ]
