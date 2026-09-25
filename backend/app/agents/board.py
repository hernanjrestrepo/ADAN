"""
Executive Board — el Board de la operación continua (OOS, `/board`), con el mismo motor
y los mismos 7 roles que el Board Room de los Niveles (AD-FUNC-02, WO-099).

Un solo Board Room: este módulo solo agrega lo propio del Board ejecutivo — la memoria de
la empresa y sus decisiones pasadas (EMS) como contexto, el Decision Record y su
persistencia en memoria. La deliberación (CEO que preside, seis especialistas que votan,
quórum, disenso, síntesis y acta) la hace `app.nivel1.board_room.BoardRoom`.
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.ai.base import LLMAdapter
from app.ems.memory import EnterpriseMemorySystem
from app.nivel1.board_room import SPECIALISTS, BoardConsensus, BoardRoom
from app.tef.executor import ToolExecutor


# Los 7 roles de AD-FUNC-02: el CEO preside y no vota; los seis especialistas votan
BOARD_AGENTS = {
    "CEO": {"name": "CEO Agent", "role": "Preside el Board: abre la sesión y da la síntesis (no vota)"},
    **{role: {"name": role, "role": focus} for role, focus in SPECIALISTS.items()},
}
DEBATE_ORDER = list(BOARD_AGENTS)


def _to_percent(value: Any) -> float:
    """Confianza en escala 0-100; los modelos a veces responden 0.0-1.0."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if 0 <= number <= 1:
        number *= 100
    return max(0.0, min(100.0, number))


@dataclass
class DebateRound:
    """La intervención de un agente en la sesión."""
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
    rounds: list[DebateRound] = field(default_factory=list)
    final_consensus: str = ""
    final_score: float = 0
    final_confidence: float = 0
    dissent_rounds: list[int] = field(default_factory=list)
    key_objections: list[str] = field(default_factory=list)
    key_agreements: list[str] = field(default_factory=list)
    opening: str = ""
    synthesis: str = ""
    minutes: str = ""


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
    deliberation: DeliberationResult
    decision_record: DecisionRecord
    duration_ms: int = 0
    memory_context: str = ""


class ExecutiveBoard:
    """Board de la operación continua sobre el motor único del Board Room."""

    def __init__(self, llm: LLMAdapter, ems: EnterpriseMemorySystem, tool_executor: ToolExecutor):
        self.llm = llm
        self.ems = ems
        self.tool_executor = tool_executor

    async def run(self, message: str, company_id: str, user_id: str) -> BoardResult:
        start_time = time.time()

        # 1. Memoria de la empresa y decisiones pasadas (consulta previa, AD-CMP-03 §2)
        memory_context = ""
        past_decisions = ""
        try:
            memory_context = await self.ems.retrieve_for_llm(company_id, message)
            past_decisions = await self._retrieve_past_decisions(company_id, message)
        except Exception:
            pass
        context = ""
        if memory_context:
            context += f"\n\nMemoria de la empresa:\n{memory_context}"
        if past_decisions:
            context += f"\n\nDecisiones anteriores del Board (no contradecirlas sin decirlo):\n{past_decisions}"

        # 2. La sesión: apertura del CEO, seis votos, consenso, síntesis y acta
        consensus = await BoardRoom(self.llm).run(message, context, client_question=message)
        deliberation = self._to_deliberation(consensus)

        # 3. Decision Record y memoria
        record = self._create_decision_record(
            deliberation,
            {"decision": consensus.decision, "score": round(consensus.score, 1),
             "confidence": round(consensus.confidence, 2)},
            message, company_id, consensus,
        )
        await self._persist_decision(record, company_id)

        return BoardResult(
            deliberation=deliberation,
            decision_record=record,
            duration_ms=int((time.time() - start_time) * 1000),
            memory_context=memory_context[:500] if memory_context else "",
        )

    @staticmethod
    def _to_deliberation(consensus: BoardConsensus) -> DeliberationResult:
        rounds = [
            DebateRound(
                agent=v.agent,
                role=BOARD_AGENTS.get(v.agent, {}).get("role", v.agent),
                round_number=i,
                analysis=v.analysis,
                response_to_previous=v.justification,
                vote=v.vote,
                confidence=v.confidence,
                objections=list(v.key_concerns),
                key_points=list(v.key_strengths),
                question_for_board=v.questions[0] if v.questions else "",
                duration_ms=int(v.duration_s * 1000),
            )
            for i, v in enumerate(consensus.votes, 1)
        ]
        return DeliberationResult(
            rounds=rounds,
            final_consensus=consensus.decision,
            final_score=consensus.score,
            final_confidence=consensus.confidence,
            dissent_rounds=[r.round_number for r in rounds
                            if r.vote not in ("ABSTAIN", consensus.decision)],
            key_objections=list(consensus.concerns_majority),
            key_agreements=list(consensus.strengths_unanimous),
            opening=f"{consensus.objective} — {consensus.decision_at_stake}",
            synthesis=consensus.synthesis,
            minutes=consensus.minutes,
        )

    def _create_decision_record(self, deliberation: DeliberationResult, consensus: dict, topic: str,
                                company_id: str, board: BoardConsensus | None = None) -> DecisionRecord:
        votes = {r.agent: r.vote for r in deliberation.rounds}
        actions = [{"action": step, "status": "pending"} for step in (board.next_steps if board else [])[:5]]
        follow_up = [{"question": e, "from": "CEO", "status": "pending"}
                     for e in (board.evidence_requests if board else [])]
        follow_up += [{"question": r.question_for_board, "from": r.agent, "status": "pending"}
                      for r in deliberation.rounds if r.question_for_board]
        dissent = board.dissent if board and board.dissent else (
            f"Disenso en rondas: {deliberation.dissent_rounds}" if deliberation.dissent_rounds else "")
        return DecisionRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            company_id=company_id,
            topic=topic,
            participants=list(BOARD_AGENTS),
            votes=votes,
            deliberation_summary=self._build_deliberation_summary(deliberation),
            final_decision=consensus["decision"],
            final_score=consensus["score"],
            final_confidence=consensus["confidence"],
            key_objections=deliberation.key_objections,
            key_agreements=deliberation.key_agreements,
            dissent_details=dissent,
            actions=actions,
            follow_up=follow_up,
        )

    def _build_deliberation_summary(self, deliberation: DeliberationResult) -> str:
        """Construye un resumen de la deliberación."""
        parts = [f"Preside: CEO Agent. Apertura: {deliberation.opening}" if deliberation.opening else "Preside: CEO Agent.",
                 f"Deliberación con {len(deliberation.rounds)} especialistas:", ""]

        for round in deliberation.rounds:
            parts.append(f"{round.role} ({round.agent}): {round.vote} ({round.confidence:.0f}%)")
            if round.analysis:
                parts.append(f"  Análisis: {round.analysis[:150]}")
            if round.objections:
                parts.append(f"  Objeciones: {'; '.join(round.objections[:2])}")
            parts.append("")

        if deliberation.synthesis:
            parts += ["Síntesis del CEO:", deliberation.synthesis]
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
