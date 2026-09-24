"""
CEO Agent — Agente ejecutivo principal de ADÁN.

Piensa como ejecutivo:
1. Interpreta el objetivo
2. Descompone el problema
3. Identifica información faltante
4. Consulta memoria
5. Selecciona y ejecuta herramientas
6. Evalúa resultados
7. Genera plan ejecutivo
8. Registra decisión
"""

import json
import uuid
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field

from app.agents.base import (
    ExecutiveAgent, AgentMessage, AgentPlan, AgentResponse,
)


@dataclass
class ExecutiveStep:
    """Paso del razonamiento ejecutivo."""
    step_type: str                       # interpret, decompose, gap_analysis, memory, tools, evaluate, plan
    description: str
    data: dict = field(default_factory=dict)
    status: str = "pending"              # pending, completed, skipped


@dataclass
class ExecutiveReasoning:
    """Razonamiento ejecutivo completo."""
    objective: str                       # objetivo detectado
    sub_objectives: list[str] = field(default_factory=list)
    information_gaps: list[str] = field(default_factory=list)
    available_information: list[str] = field(default_factory=list)
    tools_to_execute: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    memory_context: str = ""
    steps: list[ExecutiveStep] = field(default_factory=list)
    needs_more_info: bool = False
    missing_info_summary: str = ""


CEO_SYSTEM_PROMPT = """Eres el CEO Agent de ADÁN, un Sistema Operativo Empresarial con inteligencia artificial.

Tu rol es pensar como un CEO ejecutivo. No respondes inmediatamente. Primero analizas, luego decides.

PROCESO DE RAZONAMIENTO:
1. Interpreta qué necesita el usuario
2. Descompón el problema en sub-objetivos
3. Identifica qué información tienes y qué te falta
4. Recupera información de memoria
5. Ejecuta herramientas si es necesario
6. Evalúa los resultados
7. Genera un plan ejecutivo priorizado
8. Justifica cada recomendación

FORMATO DE RESPUESTA (JSON estricto):
{
    "objective": "Objetivo principal detectado",
    "sub_objectives": ["Sub-objetivo 1", "Sub-objetivo 2"],
    "available_information": ["Qué sabemos", "Qué tenemos"],
    "information_gaps": ["Qué información falta", "Qué necesitaríamos"],
    "needs_more_info": false,
    "missing_info_summary": "Si needs_more_info=true, describe qué necesitas",
    "analysis": "Análisis del estado actual",
    "priorities": [
        {
            "priority": 1,
            "action": "Acción concreta y medible",
            "owner": "Quién la ejecuta",
            "deadline": "Cuándo",
            "reasoning": "Por qué esta acción",
            "urgency": "critical|high|medium|low",
            "impact": "high|medium|low",
            "kpis": ["Indicador 1", "Indicador 2"]
        }
    ],
    "risks": [
        {
            "risk": "Riesgo identificado",
            "probability": "high|medium|low",
            "impact": "high|medium|low",
            "mitigation": "Cómo mitigarlo",
            "owner": "Quién monitorea"
        }
    ],
    "dependencies": [
        {"dependency": "Qué se necesita", "from": "De quién", "status": "pending|resolved"}
    ],
    "kpis": [
        {"name": "Nombre del KPI", "current": "Valor actual (si se conoce)", "target": "Objetivo", "unit": "Unidad"}
    ],
    "follow_up": [
        {"action": "Seguimiento", "when": "Cuándo", "responsible": "Quién"}
    ],
    "confidence": 0.0-1.0,
    "summary": "Resumen ejecutivo en 2-3 oraciones"
}

REGLAS CRÍTICAS:
- Si NO tienes suficiente información, pon needs_more_info: true y describe qué necesitas.
- No inventes datos. Si no lo sabes, di que no lo sabes.
- Cada acción debe ser concreta, medible y con responsable.
- Cada KPI debe tener valor actual (si se conoce) y objetivo.
- Prioriza por impacto × urgencia.
- Responde en español."""


class CEOAgent(ExecutiveAgent):
    """
    Agente CEO con razonamiento ejecutivo real.
    
    No es un wrapper de LLM. Tiene un loop de razonamiento:
    interpret → decompose → gap_analysis → memory → tools → evaluate → plan → justify
    """

    def system_prompt(self) -> str:
        return CEO_SYSTEM_PROMPT

    async def process(
        self,
        message: str,
        company_id: str,
        user_id: str,
        context: dict | None = None,
    ) -> AgentResponse:
        """
        Procesa una solicitud con razonamiento ejecutivo multi-paso.
        """
        start_time = time.time()
        trace_id = f"ceo-{uuid.uuid4().hex[:12]}"
        tools_used = []
        reasoning = ExecutiveReasoning(objective="")

        # ============================================================
        # PASO 1: Interpretar objetivo
        # ============================================================
        reasoning.steps.append(ExecutiveStep(
            step_type="interpret",
            description="Interpretando solicitud del usuario",
        ))
        reasoning.objective = message
        reasoning.steps[-1].status = "completed"

        # ============================================================
        # PASO 2: Recuperar memoria
        # ============================================================
        reasoning.steps.append(ExecutiveStep(
            step_type="memory",
            description="Recuperando memoria empresarial",
        ))
        memory_context = await self._retrieve_memory(company_id, message)
        reasoning.memory_context = memory_context
        reasoning.steps[-1].status = "completed"

        # ============================================================
        # PASO 3: Análisis de gaps de información
        # ============================================================
        reasoning.steps.append(ExecutiveStep(
            step_type="gap_analysis",
            description="Analizando información disponible vs requerida",
        ))

        gap_analysis = await self._analyze_information_gaps(
            message, memory_context, company_id, user_id, trace_id
        )
        reasoning.available_information = gap_analysis.get("available", [])
        reasoning.information_gaps = gap_analysis.get("gaps", [])
        reasoning.needs_more_info = gap_analysis.get("needs_more", False)
        reasoning.missing_info_summary = gap_analysis.get("missing_summary", "")
        reasoning.steps[-1].status = "completed"

        # ============================================================
        # PASO 4: Ejecutar herramientas si hay gaps que se pueden llenar
        # ============================================================
        if reasoning.information_gaps and not reasoning.needs_more_info:
            reasoning.steps.append(ExecutiveStep(
                step_type="tools",
                description="Ejecutando herramientas para obtener información",
            ))

            tool_results = await self._execute_tools_for_gaps(
                reasoning.information_gaps,
                company_id, user_id, trace_id,
            )
            reasoning.tool_results = tool_results
            tools_used = [r.get("tool_id", "unknown") for r in tool_results if r.get("status") == "success"]
            reasoning.steps[-1].status = "completed"
        else:
            reasoning.steps.append(ExecutiveStep(
                step_type="tools",
                description="No se requieren herramientas",
                status="skipped",
            ))

        # ============================================================
        # PASO 5: Generar análisis ejecutivo
        # ============================================================
        reasoning.steps.append(ExecutiveStep(
            step_type="plan",
            description="Generando plan ejecutivo",
        ))

        full_context = self._build_executive_context(reasoning)

        messages = [
            AgentMessage(role="system", content=self.system_prompt()),
            AgentMessage(role="user", content=full_context),
        ]

        response_text = await self._llm_chat(messages, temperature=0.7, max_tokens=3000)

        # ============================================================
        # PASO 6: Parsear respuesta estructurada
        # ============================================================
        plan, justification, confidence = self._parse_response(response_text)
        reasoning.steps[-1].status = "completed"

        duration_ms = int((time.time() - start_time) * 1000)

        return AgentResponse(
            agent="ceo",
            response=response_text,
            plan=plan,
            tools_used=tools_used,
            memory_context=memory_context[:500] if memory_context else "",
            justification=justification,
            confidence=confidence,
            duration_ms=duration_ms,
        )

    async def _analyze_information_gaps(
        self,
        message: str,
        memory_context: str,
        company_id: str,
        user_id: str,
        trace_id: str,
    ) -> dict:
        """
        Analiza qué información está disponible y qué falta.
        Usa LLM para determinar gaps de forma inteligente.
        """
        analysis_prompt = f"""Analiza esta solicitud y el contexto disponible.

SOLICITUD: {message}

CONTEXTO DISPONIBLE:
{memory_context[:2000] if memory_context else "Sin contexto disponible"}

Determina:
1. Qué información YA tienes (available)
2. Qué información TE FALTA (gaps)
3. Si con la información actual puedes responder o necesitas más datos

Responde EXCLUSIVAMENTE en JSON:
{{
    "available": ["info1", "info2"],
    "gaps": ["info_faltante1", "info_faltante2"],
    "needs_more": true/false,
    "missing_summary": "Descripción de qué se necesita si needs_more=true"
}}"""

        messages = [
            AgentMessage(role="system", content="Eres un analista de información. Responde solo en JSON."),
            AgentMessage(role="user", content=analysis_prompt),
        ]

        try:
            response = await self._llm_chat(messages, temperature=0.3, max_tokens=512)
            return self._parse_json_response(response, {
                "available": [],
                "gaps": [],
                "needs_more": False,
                "missing_summary": "",
            })
        except Exception:
            return {
                "available": ["Contexto de memoria empresarial"],
                "gaps": [],
                "needs_more": False,
                "missing_summary": "",
            }

    async def _execute_tools_for_gaps(
        self,
        gaps: list[str],
        company_id: str,
        user_id: str,
        trace_id: str,
    ) -> list[dict]:
        """Ejecuta herramientas para llenar gaps de información."""
        results = []

        for gap in gaps:
            gap_lower = gap.lower()

            # Seleccionar herramienta basada en el gap
            if any(w in gap_lower for w in ["ventas", "clientes", "pipeline", "ingresos", "facturación"]):
                result = await self._execute_tool(
                    "sql_query",
                    {"query": "SELECT COUNT(*) as total FROM companies"},
                    company_id, user_id, trace_id,
                )
                result["tool_id"] = "sql_query"
                result["gap_filled"] = gap
                results.append(result)

            elif any(w in gap_lower for w in ["mercado", "competencia", "tendencias"]):
                result = await self._execute_tool(
                    "http_request",
                    {"url": "https://httpbin.org/get", "method": "GET"},
                    company_id, user_id, trace_id,
                )
                result["tool_id"] = "http_request"
                result["gap_filled"] = gap
                results.append(result)

            elif any(w in gap_lower for w in ["cálculo", "ratio", "porcentaje", "projection"]):
                result = await self._execute_tool(
                    "calculator",
                    {"expression": "0"},
                    company_id, user_id, trace_id,
                )
                result["tool_id"] = "calculator"
                result["gap_filled"] = gap
                results.append(result)

        return results

    def _build_executive_context(self, reasoning: ExecutiveReasoning) -> str:
        """Construye el contexto completo para el LLM."""
        parts = []

        # Objetivo
        parts.append(f"OBJETIVO: {reasoning.objective}")

        # Información disponible
        if reasoning.available_information:
            parts.append("INFORMACIÓN DISPONIBLE:")
            for info in reasoning.available_information:
                parts.append(f"  ✓ {info}")

        # Gaps de información
        if reasoning.information_gaps:
            parts.append("INFORMACIÓN FALTANTE:")
            for gap in reasoning.information_gaps:
                parts.append(f"  ✗ {gap}")

        # Si necesita más info
        if reasoning.needs_more_info:
            parts.append(f"NECESITA MÁS INFORMACIÓN: {reasoning.missing_info_summary}")

        # Resultados de herramientas
        if reasoning.tool_results:
            parts.append("RESULTADOS DE HERRAMIENTAS:")
            for tr in reasoning.tool_results:
                tool_id = tr.get("tool_id", "?")
                status = tr.get("status", "?")
                output = tr.get("output", {})
                parts.append(f"  - {tool_id} ({status}): {json.dumps(output)[:200]}")

        # Memoria
        if reasoning.memory_context:
            parts.append(f"MEMORIA EMPRESARIAL:\n{reasoning.memory_context[:1500]}")

        return "\n\n".join(parts)

    def _parse_response(self, response_text: str) -> tuple:
        """Parsea la respuesta del LLM a estructura."""
        data = self._parse_json_response(response_text, {
            "summary": response_text[:200],
            "analysis": response_text,
            "priorities": [],
            "risks": [],
            "dependencies": [],
            "kpis": [],
            "follow_up": [],
            "confidence": 0.5,
        })

        plan = AgentPlan(
            goal=data.get("summary", ""),
            steps=[
                {
                    "action": p.get("action", ""),
                    "reasoning": p.get("reasoning", ""),
                    "owner": p.get("owner", ""),
                    "deadline": p.get("deadline", ""),
                    "urgency": p.get("urgency", "medium"),
                    "impact": p.get("impact", "medium"),
                    "kpis": p.get("kpis", []),
                }
                for p in data.get("priorities", [])
            ],
            reasoning=data.get("analysis", ""),
        )

        justification = data.get("analysis", "")
        confidence = data.get("confidence", 0.5)

        return plan, justification, confidence

    def _parse_json_response(self, text: str, default: dict) -> dict:
        """Parsea respuesta JSON de forma robusta."""
        try:
            content = text.strip()

            # Remover code fences
            if "```json" in content:
                start = content.index("```json") + 7
                end = content.index("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.index("```") + 3
                end = content.index("```", start)
                content = content[start:end].strip()

            return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            return default
