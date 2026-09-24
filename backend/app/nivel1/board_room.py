"""Board Room — 4 independent agents with analysis, justification, vote, and real consensus.

Each agent (CEO, CTO, CFO, CMO) analyzes independently.
Then a consensus round builds a unified position.
No simulation — real analysis from real LLM calls.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import asdict, dataclass, field

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_analysis_response


@dataclass
class AgentVote:
    agent: str
    analysis: str
    justification: str
    vote: str  # PROCEED, PIVOT, STOP, or ABSTAIN when the model gave no valid vote
    confidence: float  # 0-100
    key_concerns: list[str] = field(default_factory=list)
    key_strengths: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    model: str = ""
    duration_s: float = 0.0


@dataclass
class BoardConsensus:
    decision: str  # PROCEED, PIVOT, STOP, or NO_CONSENSUS when no agent gave a valid vote
    score: float  # 0-100 aggregate
    confidence: float  # 0-100
    summary: str
    votes: list[AgentVote]
    concerns_unanimous: list[str] = field(default_factory=list)
    concerns_majority: list[str] = field(default_factory=list)
    strengths_unanimous: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    dissent: str = ""  # Every agent that disagrees with the decision, one per line

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BoardConsensus":
        votes = [AgentVote(**v) for v in data.get("votes", [])]
        return cls(**{**data, "votes": votes})


# Agent system prompts — CONCISE for faster inference
AGENT_PROMPTS = {
    "CEO": {
        "name": "CEO",
        "system": (
            "CEO de ADÁN. Evalúa viabilidad GENERAL: visión, liderazgo, oportunidad. "
            "JSON: {analysis, justification, vote(PROCEED/PIVOT/STOP), confidence(0-100), "
            "key_strengths[], key_concerns[], questions[]}"
        ),
    },
    "CTO": {
        "name": "CTO",
        "system": (
            "CTO de ADÁN. Evalúa viabilidad TÉCNICA: factibilidad, riesgos, tecnología. "
            "JSON: {analysis, justification, vote(PROCEED/PIVOT/STOP), confidence(0-100), "
            "key_strengths[], key_concerns[], questions[]}"
        ),
    },
    "CFO": {
        "name": "CFO",
        "system": (
            "CFO de ADÁN. Evalúa viabilidad FINANCIERA: costos, ingresos, sostenibilidad. "
            "JSON: {analysis, justification, vote(PROCEED/PIVOT/STOP), confidence(0-100), "
            "key_strengths[], key_concerns[], questions[]}"
        ),
    },
    "CMO": {
        "name": "CMO",
        "system": (
            "CMO de ADÁN. Evalúa PROPUESTA DE VALOR: dolor real, demanda, diferenciación. "
            "JSON: {analysis, justification, vote(PROCEED/PIVOT/STOP), confidence(0-100), "
            "key_strengths[], key_concerns[], questions[]}"
        ),
    },
}


class BoardRoom:
    """Orchestrates 4 independent agents and builds real consensus."""

    def __init__(self, llm: LLMAdapter):
        self.llm = llm

    async def run(self, pain_description: str, conversation_context: str = "") -> BoardConsensus:
        """Run the complete Board Room cycle: concurrent analysis → consensus."""

        # Phase 1: Independent analysis by each agent — CONCURRENTLY
        tasks = [
            self._analyze_agent(agent_key, agent_config, pain_description, conversation_context)
            for agent_key, agent_config in AGENT_PROMPTS.items()
        ]
        votes = await asyncio.gather(*tasks)

        # Phase 2: Build consensus
        consensus = self._build_consensus(votes)

        return consensus

    async def _analyze_agent(
        self,
        agent_key: str,
        agent_config: dict,
        pain_description: str,
        conversation_context: str,
    ) -> AgentVote:
        """Run a single agent's independent analysis."""
        context_block = ""
        if conversation_context:
            context_block = f"\n\nContexto de la conversación:\n{conversation_context}"

        prompt = (
            f"Analiza la siguiente propuesta de negocio:\n\n"
            f"Descripción del problema/dolor:\n{pain_description}"
            f"{context_block}\n\n"
            f"Proporciona tu análisis como {agent_config['name']} del Board Room."
        )

        start = time.monotonic()
        try:
            response = await self.llm.chat(
                messages=[
                    LLMMessage(role="system", content=agent_config["system"]),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.6,
                max_tokens=512,
            )
        except Exception as exc:
            # Timeout o caída del modelo: el agente se abstiene y el Board sigue (antes era un 500)
            return AgentVote(
                agent=agent_key,
                analysis="",
                justification=f"El modelo no respondió ({type(exc).__name__}): se registra como abstención",
                vote="ABSTAIN",
                confidence=0,
                duration_s=time.monotonic() - start,
            )
        duration = time.monotonic() - start

        # Parse and NORMALIZE response through single layer
        try:
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            raw_data = json.loads(content)

            # SINGLE NORMALIZATION POINT — all data passes through here
            normalized = normalize_analysis_response(raw_data)

            return AgentVote(
                agent=agent_key,
                analysis=normalized["analysis"],
                justification=normalized["justification"],
                vote=normalized["vote"],
                confidence=normalized["confidence"],
                key_concerns=normalized["key_concerns"],
                key_strengths=normalized["key_strengths"],
                questions=normalized["questions"],
                model=response.model,
                duration_s=duration,
            )
        except (json.JSONDecodeError, KeyError, ValueError, AttributeError, TypeError):
            # Sin JSON válido no hay voto: se registra como abstención y no cuenta
            return AgentVote(
                agent=agent_key,
                analysis=response.content,
                justification="Respuesta sin formato válido: se registra como abstención y no cuenta como voto",
                vote="ABSTAIN",
                confidence=0,
                model=response.model,
                duration_s=duration,
            )

    def _build_consensus(self, votes: list[AgentVote]) -> BoardConsensus:
        """Build real consensus from independent votes. Abstentions are not counted."""
        abstentions = [v for v in votes if v.vote == "ABSTAIN"]
        votes_all, votes = votes, [v for v in votes if v.vote != "ABSTAIN"]
        # Quórum: al menos la mitad de los agentes debe votar; si no, uno solo decidiría por todo el Board
        if len(votes) * 2 < len(votes_all):
            return BoardConsensus(
                decision="NO_CONSENSUS",
                score=0.0,
                confidence=0.0,
                summary=(
                    "**Decisión del Board Room: sin consenso**\n"
                    f"Sin quórum: votaron {len(votes)} de {len(votes_all)} agentes. "
                    "Vuelve a ejecutar el Board Room."
                ),
                votes=votes_all,
                dissent="",
            )

        # Count votes
        vote_counts = {"PROCEED": 0, "PIVOT": 0, "STOP": 0}
        for v in votes:
            vote_counts[v.vote] = vote_counts.get(v.vote, 0) + 1

        total = len(votes)

        # Decision by majority
        if vote_counts["STOP"] >= total / 2:
            decision = "STOP"
        elif vote_counts["PIVOT"] >= total / 2:
            decision = "PIVOT"
        else:
            decision = "PROCEED"

        # Calculate aggregate score (average confidence, weighted by vote)
        vote_weights = {"PROCEED": 1.0, "PIVOT": 0.5, "STOP": 0.0}
        weighted_sum = sum(v.confidence * vote_weights.get(v.vote, 0.5) for v in votes)
        score = weighted_sum / total if total > 0 else 0

        # Average confidence
        avg_confidence = sum(v.confidence for v in votes) / total if total > 0 else 0

        # Find unanimous concerns and strengths
        all_concerns = [set(v.key_concerns) for v in votes if v.key_concerns]
        all_strengths = [set(v.key_strengths) for v in votes if v.key_strengths]

        concerns_unanimous = list(set.intersection(*all_concerns)) if len(all_concerns) == total else []
        concerns_majority = list(set.union(*all_concerns)) if all_concerns else []
        strengths_unanimous = list(set.intersection(*all_strengths)) if len(all_strengths) == total else []

        # Find dissent: every agent that disagrees, not only the last one (AD-FUNC-02)
        dissent = "\n".join(
            f"{v.agent} votó {v.vote}: {v.justification}" for v in votes if v.vote != decision
        )

        # Build summary
        summary_parts = []
        for v in votes:
            summary_parts.append(f"**{v.agent}** ({v.vote}, confianza {v.confidence:.0f}%): {v.justification}")

        summary = (
            f"**Decisión del Board Room: {decision}**\n"
            f"Score promedio: {score:.0f}/100 | Confianza promedio: {avg_confidence:.0f}%\n\n"
            + "\n\n".join(summary_parts)
        )

        if dissent:
            summary += f"\n\n**Disenso:**\n{dissent}"
        if abstentions:
            summary += "\n\n**Abstenciones:** " + ", ".join(v.agent for v in abstentions)

        return BoardConsensus(
            decision=decision,
            score=score,
            confidence=avg_confidence,
            summary=summary,
            votes=votes_all,
            concerns_unanimous=concerns_unanimous,
            concerns_majority=concerns_majority,
            strengths_unanimous=strengths_unanimous,
            dissent=dissent,
        )
