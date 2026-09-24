"""
Planner — Determina qué hacer antes de hacerlo.

Analiza la solicitud del usuario y produce un plan de ejecución
con pasos, agentes requeridos, herramientas y fallback.
"""

import json
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_string


@dataclass
class PlanStep:
    """Un paso del plan de ejecución."""
    order: int
    description: str
    component: str  # "knowledge_engine", "board_room", "llm", "tool_manager"
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    optional: bool = False


@dataclass
class Plan:
    """Plan de ejecución para una solicitud."""
    goal: str
    steps: list[PlanStep]
    required_components: list[str]
    estimated_iterations: int
    fallback_strategy: str
    reasoning: str


PLANNER_SYSTEM_PROMPT = """Eres el Planner de ADÁN. Tu trabajo es analizar la solicitud del usuario y generar un plan de ejecución.

CONTEXTO DEL SISTEMA:
- Tienes acceso a: Knowledge Engine (datos de la empresa), Board Room (4 agentes: CEO, CTO, CFO, CMO), LLM (generación de texto), Tool Manager (herramientas).
- El Gate Review es determinístico (sin LLM).
- El sistema tiene memoria de conversaciones previas.

RESPUESTA REQUERIDA:
Responde EXCLUSIVAMENTE con un JSON válido con esta estructura:
{
    "goal": "objetivo claro de la solicitud",
    "steps": [
        {
            "order": 1,
            "description": "descripción del paso",
            "component": "knowledge_engine|board_room|llm|tool_manager",
            "optional": false
        }
    ],
    "reasoning": "por qué este plan es apropiado"
}

REGLAS:
- Si la solicitud es simple (pregunta directa), usa 1-2 pasos.
- Si la solicitud requiere análisis, usa 3-5 pasos.
- Siempre incluye knowledge_engine como primer paso si hay contexto de empresa.
- Para análisis de problemas, usa board_room.
- Para generación de respuesta final, usa llm.
- No inventes herramientas que no existen."""


class Planner:
    """
    Planificador que determina qué pasos ejecutar
    para satisfacer la solicitud del usuario.
    """

    def __init__(self, llm: LLMAdapter):
        self.llm = llm

    async def create_plan(
        self, user_message: str, knowledge_context: str
    ) -> Plan:
        """Genera un plan de ejecución para la solicitud del usuario."""
        # Para solicitudes simples, generar plan rápido sin LLM
        if self._is_simple_query(user_message):
            return self._create_simple_plan(user_message)

        # Para solicitudes complejas, usar LLM para planificar
        return await self._create_llm_plan(user_message, knowledge_context)

    def _is_simple_query(self, message: str) -> bool:
        """Determina si la solicitud es simple (sin análisis profundo)."""
        simple_patterns = [
            "qué sabes", "cuéntame", "resumen", "estado",
            "qué nivel", "cómo va", "cuántos", "cuál es",
        ]
        msg_lower = message.lower()
        return any(p in msg_lower for p in simple_patterns)

    def _create_simple_plan(self, user_message: str) -> Plan:
        """Crea un plan simple para preguntas directas."""
        return Plan(
            goal=user_message,
            steps=[
                PlanStep(
                    order=1,
                    description="Recuperar conocimiento de la empresa",
                    component="knowledge_engine",
                    inputs=["company_id"],
                    outputs=["knowledge_context"],
                ),
                PlanStep(
                    order=2,
                    description="Generar respuesta con contexto",
                    component="llm",
                    inputs=["knowledge_context", "user_message"],
                    outputs=["response"],
                ),
            ],
            required_components=["knowledge_engine", "llm"],
            estimated_iterations=1,
            fallback_strategy="Responder con información disponible sin LLM",
            reasoning="Solicitud simple: pregunta directa sobre estado de la empresa",
        )

    async def _create_llm_plan(
        self, user_message: str, knowledge_context: str
    ) -> Plan:
        """Crea un plan usando LLM para solicitudes complejas."""
        context_snippet = knowledge_context[:1000] if knowledge_context else "Sin contexto disponible"

        user_prompt = f"""SOLICITUD DEL USUARIO: {user_message}

CONTEXTO DISPONIBLE:
{context_snippet}

Genera el plan de ejecución en JSON:"""

        try:
            response = await self.llm.chat(
                messages=[
                    LLMMessage(role="system", content=PLANNER_SYSTEM_PROMPT),
                    LLMMessage(role="user", content=user_prompt),
                ],
                temperature=0.3,
                max_tokens=512,
            )

            # Parsear la respuesta del LLM
            plan_data = self._parse_plan_response(response.content)

            # Convertir a objeto Plan
            steps = []
            for step_data in plan_data.get("steps", []):
                steps.append(PlanStep(
                    order=step_data.get("order", 0),
                    description=step_data.get("description", ""),
                    component=step_data.get("component", "llm"),
                    optional=step_data.get("optional", False),
                ))

            return Plan(
                goal=plan_data.get("goal", user_message),
                steps=steps,
                required_components=list(set(s.component for s in steps)),
                estimated_iterations=len(steps),
                fallback_strategy="Ejecutar pasos no-optional, omitir los opcionales",
                reasoning=plan_data.get("reasoning", "Plan generado por LLM"),
            )

        except Exception:
            # Fallback: plan por defecto para análisis
            return self._create_analysis_plan(user_message)

    def _create_analysis_plan(self, user_message: str) -> Plan:
        """Plan por defecto para solicitudes de análisis."""
        return Plan(
            goal=user_message,
            steps=[
                PlanStep(
                    order=1,
                    description="Recuperar conocimiento completo de la empresa",
                    component="knowledge_engine",
                    inputs=["company_id"],
                    outputs=["knowledge_context"],
                ),
                PlanStep(
                    order=2,
                    description="Ejecutar Board Room para análisis multi-perspectiva",
                    component="board_room",
                    inputs=["knowledge_context"],
                    outputs=["board_consensus"],
                ),
                PlanStep(
                    order=3,
                    description="Generar respuesta consolidada con análisis",
                    component="llm",
                    inputs=["board_consensus", "knowledge_context"],
                    outputs=["response"],
                ),
            ],
            required_components=["knowledge_engine", "board_room", "llm"],
            estimated_iterations=3,
            fallback_strategy="Si Board Room falla, usar LLM directamente con contexto",
            reasoning="Plan de análisis: recuperar contexto → analizar con Board Room → consolidar respuesta",
        )

    def _parse_plan_response(self, content: str) -> dict:
        """Parsea la respuesta del LLM a un dict de plan."""
        # Intentar extraer JSON del contenido
        content = content.strip()

        # Si hay code fences, extraer
        if "```json" in content:
            start = content.index("```json") + 7
            end = content.index("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.index("```") + 3
            end = content.index("```", start)
            content = content[start:end].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Si no es JSON válido, crear plan por defecto
            return {
                "goal": "Analizar solicitud",
                "steps": [
                    {"order": 1, "description": "Recuperar contexto", "component": "knowledge_engine"},
                    {"order": 2, "description": "Generar respuesta", "component": "llm"},
                ],
                "reasoning": "Fallback: plan por defecto por error de parsing",
            }
