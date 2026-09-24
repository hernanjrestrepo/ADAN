"""
Executive Board — Multi-Agent Board con Deliberación Real.

No son 7 votos independientes.
Es un debate donde cada agente:
1. Escucha a los anteriores
2. Evalúa argumentos
3. Puede objetar, modificar o apoyar
4. Contribuye al consenso final
"""

import json
import uuid
import time
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_list, normalize_string, normalize_vote
from app.ems.memory import EnterpriseMemorySystem
from app.tef.executor import ToolExecutor


# ============================================================
# Agent Definitions
# ============================================================

BOARD_AGENTS = {
    "CEO": {
        "name": "Director Ejecutivo",
        "order": 1,
        "focus": "Visión general, estrategia, liderazgo, oportunidades",
        "system_prompt": """Eres el CEO de una empresa. Tu rol es liderar la discusión.

PROCESO:
1. Analiza la solicitud del usuario
2. Presenta tu perspectiva estratégica
3. Propón una dirección inicial

FORMATO DE RESPUESTA (JSON):
{
    "analysis": "Tu análisis estratégico",
    "proposal": "Qué propones hacer",
    "vote": "PROCEED|PIVOT|STOP",
    "confidence": 0.0-1.0,
    "key_points": ["Punto 1", "Punto 2"],
    "concerns": ["Preocupación 1"],
    "question_for_board": "Pregunta que quieres que el board responda"
}

REGLAS:
- Sé directo y ejecutivo.
- Propón acciones concretas.
- Identifica riesgos desde el inicio.
- Responde en español.""",
    },
    "CFO": {
        "name": "Director Financiero",
        "order": 2,
        "focus": "Finanzas, costos, ingresos, sostenibilidad, ROI",
        "system_prompt": """Eres el CFO de una empresa. Respondes al CEO y al board.

CONTEXTO: Ya escuchaste al CEO. Ahora analizas desde la perspectiva financiera.

PROCESO:
1. Evalúa la propuesta del CEO
2. Analiza impacto financiero
3. Objeta si hay problemas de caja, ROI o sostenibilidad
4. Propón alternativas financieras si es necesario

FORMATO DE RESPUESTA (JSON):
{
    "analysis": "Tu análisis financiero",
    "response_to_ceo": "Qué piensas de la propuesta del CEO",
    "objections": ["Objeción financiera 1"] o [],
    "financial_constraints": ["Restricción 1"] o [],
    "vote": "PROCEED|PIVOT|STOP",
    "confidence": 0.0-1.0,
    "alternative": "Alternativa financiera (si aplica)" o null,
    "question_for_board": "Pregunta financiera para el board"
}

REGLAS:
- Si no hay caja, di que no hay caja.
- Si el ROI es negativo, di que es negativo.
- No suavices la realidad financiera.
- Responde en español.""",
    },
    "COO": {
        "name": "Director de Operaciones",
        "order": 3,
        "focus": "Procesos, eficiencia, operaciones, ejecución",
        "system_prompt": """Eres el COO de una empresa. Respondes a las opiniones anteriores.

CONTEXTO: Ya escuchaste al CEO y CFO. Ahora analizas la viabilidad operativa.

PROCESO:
1. Evalúa si la propuesta es ejecutable operativamente
2. Identifica recursos necesarios
3. Objeta si la operación no puede absorber el cambio
4. Propón plan operativo si es viable

FORMATO DE RESPUESTA (JSON):
{
    "analysis": "Tu análisis operativo",
    "response_to_previous": "Qué piensas de las opiniones anteriores",
    "operational_feasibility": "Factibilidad operativa",
    "resource_requirements": ["Recurso 1", "Recurso 2"],
    "objections": ["Objeción operativa"] o [],
    "vote": "PROCEED|PIVOT|STOP",
    "confidence": 0.0-1.0,
    "question_for_board": "Pregunta operativa para el board"
}

REGLAS:
- Sé realista sobre capacidades operativas.
- Identifica cuellos de botella.
- No prometas lo que no puedes ejecutar.
- Responde en español.""",
    },
    "CMO": {
        "name": "Director de Marketing",
        "order": 4,
        "focus": "Mercado, clientes, marca, adquisición, retención",
        "system_prompt": """Eres el CMO de una empresa. Respondes a las opiniones anteriores.

CONTEXTO: Ya escuchaste CEO, CFO y COO. Ahora analizas desde marketing.

PROCESO:
1. Evalúa el impacto en clientes y mercado
2. Analiza si hay demanda real
3. Objeta si el posicionamiento no es correcto
4. Propón estrategia de go-to-market

FORMATO DE RESPUESTA (JSON):
{
    "analysis": "Tu análisis de mercado",
    "response_to_previous": "Qué piensas de las opiniones anteriores",
    "market_assessment": "Estado del mercado",
    "customer_impact": "Impacto en clientes",
    "objections": ["Objeción de mercado"] o [],
    "vote": "PROCEED|PIVOT|STOP",
    "confidence": 0.0-1.0,
    "question_for_board": "Pregunta de mercado para el board"
}

REGLAS:
- Basa tu análisis en datos de mercado, no en suposiciones.
- Si no hay demanda, di que no hay demanda.
- Responde en español.""",
    },
    "CTO": {
        "name": "Director Tecnológico",
        "order": 5,
        "focus": "Tecnología, factibilidad, arquitectura, deuda técnica",
        "system_prompt": """Eres el CTO de una empresa. Respondes a las opiniones anteriores.

CONTEXTO: Ya escuchaste CEO, CFO, COO y CMO. Ahora analizas la factibilidad técnica.

PROCESO:
1. Evalúa si es técnicamente factible
2. Identifica riesgos técnicos
3. Objeta si hay deuda técnica que bloquea
4. Propón arquitectura técnica

FORMATO DE RESPUESTA (JSON):
{
    "analysis": "Tu análisis técnico",
    "response_to_previous": "Qué piensas de las opiniones anteriores",
    "technical_feasibility": "Factibilidad técnica",
    "technical_risks": ["Riesgo 1", "Riesgo 2"],
    "objections": ["Objeción técnica"] o [],
    "vote": "PROCEED|PIVOT|STOP",
    "confidence": 0.0-1.0,
    "question_for_board": "Pregunta técnica para el board"
}

REGLAS:
- Sé honesto sobre limitaciones técnicas.
- Si no puedes construirlo, di que no puedes.
- Responde en español.""",
    },
    "CLO": {
        "name": "Director Legal",
        "order": 6,
        "focus": "Legal, compliance, regulaciones, contratos, riesgo legal",
        "system_prompt": """Eres el CLO (Chief Legal Officer) de una empresa. Respondes a las opiniones anteriores.

CONTEXTO: Ya escuchaste CEO, CFO, COO, CMO y CTO. Ahora analizas riesgos legales.

PROCESO:
1. Evalúa riesgos legales y de compliance
2. Identifica requisitos regulatorios
3. Objeta si hay riesgo legal alto
4. Propón medidas de protección legal

FORMATO DE RESPUESTA (JSON):
{
    "analysis": "Tu análisis legal",
    "response_to_previous": "Qué piensas de las opiniones anteriores",
    "legal_risks": ["Riesgo legal 1"],
    "compliance_requirements": ["Requisito 1"],
    "objections": ["Objeción legal"] o [],
    "vote": "PROCEED|PIVOT|STOP",
    "confidence": 0.0-1.0,
    "question_for_board": "Pregunta legal para el board"
}

REGLAS:
- Si hay riesgo legal alto, di que hay riesgo legal alto.
- No minimices issues de compliance.
- Responde en español.""",
    },
    "CHRO": {
        "name": "Director de Recursos Humanos",
        "order": 7,
        "focus": "Personas, talento, cultura, organizacional, bienestar",
        "system_prompt": """Eres el CHRO (Chief Human Resources Officer) de una empresa. Respondes a TODAS las opiniones anteriores.

CONTEXTO: Ya escuchaste a TODOS los directores. Ahora analizas el impacto en personas y organizacional.

PROCESO:
1. Resume las posturas del board
2. Analiza impacto en el equipo
3. Identifica necesidades de talento
4. Propón plan de ejecución considerando personas

FORMATO DE RESPUESTA (JSON):
{
    "analysis": "Tu análisis organizacional",
    "board_summary": "Resumen de posturas del board",
    "people_impact": "Impacto en personas",
    "talent_needs": ["Necesidad 1", "Necesidad 2"],
    "objections": ["Objeción organizacional"] o [],
    "vote": "PROCEED|PIVOT|STOP",
    "confidence": 0.0-1.0,
    "execution_plan": "Plan de ejecución considerando personas"
}

REGLAS:
- Si el equipo no está preparado, di que no está preparado.
- Considera cultura y bienestar, no solo productividad.
- Responde en español.""",
    },
}

def _to_percent(value: Any) -> float:
    """Confianza en escala 0-100; los prompts piden 0.0-1.0 pero el modelo a veces responde 0-100."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if 0 <= number <= 1:
        number *= 100
    return max(0.0, min(100.0, number))


# ============================================================
# Debate Order
# ============================================================

DEBATE_ORDER = ["CEO", "CFO", "COO", "CMO", "CTO", "CLO", "CHRO"]


# ============================================================
# Data Classes
# ============================================================

@dataclass
class DebateRound:
    """Una ronda de debate de un agente."""
    agent: str
    role: str
    round_number: int
    analysis: str
    response_to_previous: str
    vote: str
    confidence: float
    objections: list[str] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)
    question_for_board: str = ""
    duration_ms: int = 0


@dataclass
class DeliberationResult:
    """Resultado de la deliberación completa."""
    rounds: list[DebateRound] = field(default_factory=list)
    final_consensus: str = ""
    final_score: float = 0
    final_confidence: float = 0
    dissent_rounds: list[int] = field(default_factory=list)
    key_objections: list[str] = field(default_factory=list)
    key_agreements: list[str] = field(default_factory=list)


@dataclass
class DecisionRecord:
    """Registro persistente de una decisión del Board."""
    id: str
    timestamp: datetime
    company_id: str
    topic: str
    participants: list[str]
    votes: dict[str, str]                 # agent -> vote
    deliberation_summary: str
    final_decision: str
    final_score: float
    final_confidence: float
    key_objections: list[str]
    key_agreements: list[str]
    dissent_details: str
    actions: list[dict] = field(default_factory=list)
    follow_up: list[dict] = field(default_factory=list)


@dataclass
class BoardResult:
    """Resultado completo del Board."""
    deliberation: DeliberationResult
    decision_record: DecisionRecord
    duration_ms: int = 0
    memory_context: str = ""


# ============================================================
# Executive Board
# ============================================================

class ExecutiveBoard:
    """
    Board Ejecutivo con deliberación real.
    
    No ejecuta agentes en paralelo.
    Los ejecuta en secuencia, donde cada agente:
    1. Escucha a los anteriores
    2. Responde a sus argumentos
    3. Puede objetar o apoyar
    4. Contribuye al debate
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

    async def run(
        self,
        message: str,
        company_id: str,
        user_id: str,
    ) -> BoardResult:
        """
        Ejecuta el Board con deliberación secuencial.
        
        Flujo:
        1. Recuperar memoria (incluyendo decisiones pasadas)
        2. CEO presenta la solicitud
        3. CFO responde
        4. COO responde
        5. CMO responde
        6. CTO responde
        7. CLO responde
        8. CHRO responde (resume todo)
        9. Consenso final
        10. Crear Decision Record
        11. Persistir en memoria
        """
        start_time = time.time()

        # ============================================================
        # PASO 1: Recuperar memoria
        # ============================================================
        memory_context = ""
        past_decisions = ""
        try:
            memory_context = await self.ems.retrieve_for_llm(company_id, message)
            # Buscar decisiones pasadas del Board
            past_decisions = await self._retrieve_past_decisions(company_id, message)
        except Exception:
            pass

        # ============================================================
        # PASO 2-8: Deliberación secuencial
        # ============================================================
        deliberation = await self._run_deliberation(
            message, memory_context, past_decisions, company_id, user_id
        )

        # ============================================================
        # PASO 9: Consenso final
        # ============================================================
        consensus = self._calculate_final_consensus(deliberation)

        # ============================================================
        # PASO 10: Crear Decision Record
        # ============================================================
        decision_record = self._create_decision_record(
            deliberation, consensus, message, company_id
        )

        # ============================================================
        # PASO 11: Persistir en memoria
        # ============================================================
        await self._persist_decision(decision_record, company_id)

        duration_ms = int((time.time() - start_time) * 1000)

        return BoardResult(
            deliberation=deliberation,
            decision_record=decision_record,
            duration_ms=duration_ms,
            memory_context=memory_context[:500] if memory_context else "",
        )

    async def _run_deliberation(
        self,
        message: str,
        memory_context: str,
        past_decisions: str,
        company_id: str,
        user_id: str,
    ) -> DeliberationResult:
        """Ejecuta la deliberación secuencial."""
        deliberation = DeliberationResult()
        debate_history = []

        for agent_key in DEBATE_ORDER:
            agent_config = BOARD_AGENTS[agent_key]

            # Construir contexto con historial del debate
            context = self._build_debate_context(
                message, memory_context, past_decisions, debate_history, agent_key
            )

            # Ejecutar agente
            round_result = await self._run_agent_round(
                agent_key, agent_config, context
            )

            deliberation.rounds.append(round_result)
            debate_history.append(round_result)

            # Detectar disenso (una abstención no es disenso)
            if round_result.vote not in ("PROCEED", "ABSTAIN"):
                deliberation.dissent_rounds.append(round_result.round_number)

            # Recoger objeciones
            deliberation.key_objections.extend(round_result.objections)

        return deliberation

    def _build_debate_context(
        self,
        message: str,
        memory_context: str,
        past_decisions: str,
        debate_history: list[DebateRound],
        current_agent: str,
    ) -> str:
        """Construye el contexto para un agente específico."""
        parts = []

        # Solicitud original
        parts.append(f"SOLICITUD: {message}")

        # Memoria de la empresa
        if memory_context:
            parts.append(f"CONOCIMIENTO DE LA EMPRESA:\n{memory_context[:1500]}")

        # Decisiones pasadas
        if past_decisions:
            parts.append(f"DECISIONES PASADAS DEL BOARD:\n{past_decisions[:1000]}")

        # Historial del debate hasta ahora
        if debate_history:
            parts.append("DEBATE HASTA AHORA:")
            for round in debate_history:
                parts.append(f"\n--- {round.role} ({round.agent}) ---")
                parts.append(f"Análisis: {round.analysis[:300]}")
                if round.response_to_previous:
                    parts.append(f"Respuesta a anteriores: {round.response_to_previous[:200]}")
                parts.append(f"Voto: {round.vote} (confianza: {round.confidence:.0f}%)")
                if round.objections:
                    parts.append(f"Objeciones: {'; '.join(round.objections[:3])}")
                if round.question_for_board:
                    parts.append(f"Pregunta: {round.question_for_board}")

        # Agente actual
        parts.append(f"\nAhora te toca a TI ({current_agent}). Analiza todo lo anterior y responde.")

        return "\n".join(parts)

    async def _run_agent_round(
        self,
        agent_key: str,
        agent_config: dict,
        context: str,
    ) -> DebateRound:
        """Ejecuta una ronda de debate de un agente."""
        start_time = time.time()

        try:
            messages = [
                LLMMessage(role="system", content=agent_config["system_prompt"]),
                LLMMessage(role="user", content=context),
            ]

            response = await self.llm.chat(
                messages=messages,
                temperature=0.6,
                max_tokens=768,
            )

            data = self._parse_json_response(response.content)

            duration_ms = int((time.time() - start_time) * 1000)

            return DebateRound(
                agent=agent_key,
                role=agent_config["name"],
                round_number=agent_config["order"],
                analysis=normalize_string(data.get("analysis")),
                response_to_previous=normalize_string(
                    data.get("response_to_ceo") or data.get("response_to_previous") or data.get("board_summary")
                ),
                vote=normalize_vote(data.get("vote")),
                confidence=_to_percent(data.get("confidence")),
                objections=normalize_list(data.get("objections")),
                key_points=normalize_list(
                    data.get("key_points") or data.get("financial_constraints") or data.get("resource_requirements")
                ),
                question_for_board=normalize_string(data.get("question_for_board")),
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return DebateRound(
                agent=agent_key,
                role=agent_config["name"],
                round_number=agent_config["order"],
                analysis=f"Error: {str(e)}",
                response_to_previous="",
                vote="ABSTAIN",
                confidence=0.0,
                duration_ms=duration_ms,
            )

    def _calculate_final_consensus(self, deliberation: DeliberationResult) -> dict:
        """Calcula el consenso final desde la deliberación. Las abstenciones no cuentan."""
        valid_rounds = [r for r in deliberation.rounds if r.vote != "ABSTAIN"]
        # Quórum: al menos la mitad de los agentes debe votar
        if not valid_rounds or len(valid_rounds) * 2 < len(deliberation.rounds):
            return {"decision": "NO_CONSENSUS", "score": 0.0, "confidence": 0.0}

        votes = {}
        for rnd in valid_rounds:
            votes[rnd.agent] = rnd.vote

        # Contar votos
        proceed_count = sum(1 for v in votes.values() if v == "PROCEED")
        pivot_count = sum(1 for v in votes.values() if v == "PIVOT")
        stop_count = sum(1 for v in votes.values() if v == "STOP")
        total = len(votes)

        # Decisión mayoritaria
        if stop_count >= total / 2:
            decision = "STOP"
        elif pivot_count >= total / 2:
            decision = "PIVOT"
        else:
            decision = "PROCEED"

        # Score promedio
        vote_scores = {"PROCEED": 1.0, "PIVOT": 0.5, "STOP": 0.0}
        avg_score = sum(vote_scores.get(v, 0) for v in votes.values()) / total * 100

        # Confianza promedio (0-100)
        avg_confidence = sum(r.confidence for r in valid_rounds) / total

        return {
            "decision": decision,
            "score": round(avg_score, 1),
            "confidence": round(avg_confidence, 2),
        }

    def _create_decision_record(
        self,
        deliberation: DeliberationResult,
        consensus: dict,
        topic: str,
        company_id: str,
    ) -> DecisionRecord:
        """Crea un registro persistente de la decisión."""
        votes = {r.agent: r.vote for r in deliberation.rounds}

        # Generar acciones y follow-up desde el análisis del CHRO
        chro_round = next((r for r in deliberation.rounds if r.agent == "CHRO"), None)
        actions = []
        follow_up = []

        if chro_round and chro_round.key_points:
            actions = [{"action": kp, "status": "pending"} for kp in chro_round.key_points[:5]]

        # Generar seguimiento desde preguntas del board
        for r in deliberation.rounds:
            if r.question_for_board:
                follow_up.append({
                    "question": r.question_for_board,
                    "from": r.agent,
                    "status": "pending",
                })

        return DecisionRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            company_id=company_id,
            topic=topic,
            participants=list(votes.keys()),
            votes=votes,
            deliberation_summary=self._build_deliberation_summary(deliberation),
            final_decision=consensus["decision"],
            final_score=consensus["score"],
            final_confidence=consensus["confidence"],
            key_objections=deliberation.key_objections,
            key_agreements=[],
            dissent_details=f"Disenso en rondas: {deliberation.dissent_rounds}" if deliberation.dissent_rounds else "",
            actions=actions,
            follow_up=follow_up,
        )

    def _build_deliberation_summary(self, deliberation: DeliberationResult) -> str:
        """Construye un resumen de la deliberación."""
        parts = []
        parts.append(f"Deliberación con {len(deliberation.rounds)} participantes:")
        parts.append("")

        for round in deliberation.rounds:
            parts.append(f"{round.role} ({round.agent}): {round.vote} ({round.confidence:.0f}%)")
            if round.analysis:
                parts.append(f"  Análisis: {round.analysis[:150]}")
            if round.objections:
                parts.append(f"  Objeciones: {'; '.join(round.objections[:2])}")
            parts.append("")

        return "\n".join(parts)

    async def _retrieve_past_decisions(self, company_id: str, query: str) -> str:
        """Recupera decisiones pasadas del Board."""
        try:
            result = await self.ems.retrieve_for_llm(
                company_id,
                f"decisiones del board directivo {query}"
            )
            return result
        except Exception:
            return ""

    async def _persist_decision(self, record: DecisionRecord, company_id: str):
        """Persiste el Decision Record en memoria."""
        try:
            # Guardar como hecho en el knowledge graph
            self.ems.add_fact(
                company_id=company_id,
                fact_type="decision",
                subject=f"Board Decision: {record.topic[:100]}",
                predicate="decidió",
                object_value=record.final_decision,
                confidence=record.final_confidence / 100,
                source="board_deliberation",
            )

            # Guardar como documento
            content = self._format_decision_record(record)
            await self.ems.ingest(
                company_id=company_id,
                text=content,
                title=f"Board Decision: {record.topic[:100]}",
                source_type="board_decision",
                metadata={
                    "decision_id": record.id,
                    "decision": record.final_decision,
                    "score": record.final_score,
                    "participants": record.participants,
                },
            )
        except Exception:
            pass  # La persistencia no debe bloquear el Board

    def _format_decision_record(self, record: DecisionRecord) -> str:
        """Formatea el Decision Record como texto persistente."""
        parts = [
            f"DECISIÓN DEL BOARD — {record.timestamp.strftime('%Y-%m-%d %H:%M')}",
            f"",
            f"TEMa: {record.topic}",
            f"DECISIÓN: {record.final_decision}",
            f"SCORE: {record.final_score}/100",
            f"CONFIANZA: {record.final_confidence:.0f}%",
            f"",
            f"PARTICIPANTES: {', '.join(record.participants)}",
            f"",
            f"VOTOS:",
        ]
        for agent, vote in record.votes.items():
            parts.append(f"  {agent}: {vote}")

        parts.append(f"")
        parts.append(f"RESUMEN DE DELIBERACIÓN:")
        parts.append(record.deliberation_summary)

        if record.key_objections:
            parts.append(f"")
            parts.append(f"OBJECIONES CLAVE:")
            for obj in record.key_objections:
                parts.append(f"  - {obj}")

        if record.actions:
            parts.append(f"")
            parts.append(f"ACCIONES:")
            for action in record.actions:
                parts.append(f"  - {action.get('action', '')}")

        return "\n".join(parts)

    def _parse_json_response(self, content: str) -> dict:
        """Parsea respuesta JSON de forma robusta."""
        try:
            text = content.strip()
            if "```json" in text:
                start = text.index("```json") + 7
                end = text.index("```", start)
                text = text[start:end].strip()
            elif "```" in text:
                start = text.index("```") + 3
                end = text.index("```", start)
                text = text[start:end].strip()
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            # Sin JSON válido no hay voto: queda como abstención
            return {"analysis": content[:200]}
