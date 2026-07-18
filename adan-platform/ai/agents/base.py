"""Runtime de agentes propio y ligero - BP-0007 (AD-006 SS4, entidad Agente).
Prohibido explicitamente por el Plan Maestro: LangChain/LangGraph/CrewAI o equivalentes.

Un Agente (AD-003: "la unidad interna de especializacion de ADAN, ej. rol de CEO, CTO,
CFO") se define declarativamente: rol, instrucciones, herramientas disponibles, y limites.
Este modulo NO conoce Ollama - recibe un ModelBackend ya construido (capa de Sprint 1)."""

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from models.base import GenerateResult, ModelBackend

logger = logging.getLogger("adan.ai.agents")


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Tool:
    """Una herramienta que un Agente puede invocar. Minimo indispensable en esta version -
    el conjunto real de herramientas (kg_read, kg_write, memory_search...) llega en WO-003."""

    name: str
    description: str
    fn: Callable[[str], str]


@dataclass
class MemoryHook:
    """Punto de enganche a la jerarquia de 5 capas de AD-CMP-04 (Global/Proyecto/Nivel/
    Card/Conversacion). Implementacion real (semantica, pgvector) llega en WO-003 - aqui
    es un contrato minimo para que el runtime de agentes no necesite reescribirse despues."""

    fetch_context: Callable[[str], str] | None = None
    store_result: Callable[[str, str], None] | None = None


@dataclass
class AgentDefinition:
    """Definicion declarativa de un Agente - AD-003 entidad Agente."""

    agent_id: str
    rol: str  # ej. "CEO", "CTO", "CFO" (AD-003)
    instrucciones: str  # instrucciones del blueprint (AD-FUNC especifico que lo define)
    tools: list[Tool] = field(default_factory=list)
    max_steps: int = 5
    max_tokens: int = 4000


@dataclass
class StepRecord:
    step_number: int
    prompt: str
    output: str
    call_record: object  # ModelCallRecord, tipado laxo para no acoplar el dataclass


@dataclass
class RunResult:
    status: RunStatus
    steps: list[StepRecord]
    final_output: str | None
    error: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None


class CancellationToken:
    """Cooperativo - el runtime revisa este flag entre pasos, nunca interrumpe a mitad
    de una llamada de inferencia en curso (evita estado inconsistente)."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()


class AgentRuntime:
    """Ejecuta una AgentDefinition contra un input, paso a paso, respetando limites y
    cancelacion cooperativa. Un 'paso' = una llamada de inferencia real."""

    def __init__(self, model_backend: ModelBackend, memory_hook: MemoryHook | None = None):
        self.model_backend = model_backend
        self.memory_hook = memory_hook or MemoryHook()

    def run(
        self,
        definition: AgentDefinition,
        user_input: str,
        *,
        cancellation_token: CancellationToken | None = None,
    ) -> RunResult:
        cancellation_token = cancellation_token or CancellationToken()
        result = RunResult(status=RunStatus.RUNNING, steps=[], final_output=None)

        context = ""
        if self.memory_hook.fetch_context:
            context = self.memory_hook.fetch_context(definition.agent_id)

        prompt = self._build_prompt(definition, user_input, context)

        try:
            for step_number in range(1, definition.max_steps + 1):
                if cancellation_token.is_cancelled:
                    result.status = RunStatus.CANCELLED
                    result.finished_at = datetime.now(UTC)
                    return result

                gen_result: GenerateResult = self.model_backend.generate(prompt)
                result.steps.append(
                    StepRecord(
                        step_number=step_number,
                        prompt=prompt,
                        output=gen_result.text,
                        call_record=gen_result.call_record,
                    )
                )

                # Runtime de un solo paso por ahora (sin bucle de herramientas todavia -
                # WO-003 agrega tool-calling real cuando existan herramientas de KG)
                result.final_output = gen_result.text
                break

            result.status = RunStatus.COMPLETED
        except Exception as exc:  # noqa: BLE001
            logger.exception("Agent run failed: %s", definition.agent_id)
            result.status = RunStatus.FAILED
            result.error = str(exc)

        result.finished_at = datetime.now(UTC)

        if self.memory_hook.store_result and result.final_output:
            self.memory_hook.store_result(definition.agent_id, result.final_output)

        return result

    @staticmethod
    def _build_prompt(definition: AgentDefinition, user_input: str, context: str) -> str:
        parts = [f"Eres el Agente {definition.rol} de ADAN.", definition.instrucciones]
        if context:
            parts.append(f"Contexto relevante:\n{context}")
        parts.append(f"Entrada del usuario:\n{user_input}")
        return "\n\n".join(parts)
