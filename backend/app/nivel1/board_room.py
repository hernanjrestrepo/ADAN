"""Board Room (AD-FUNC-02, WO-099): siete roles y el Flujo Maestro de Orquestación.

- **CEO**: preside. Abre la sesión con el objetivo y la decisión en juego, y la cierra con la
  síntesis que el cliente escucha como "ADÁN". No es una voz más: no vota (AD-FUNC-02 §2.3).
- **Seis especialistas** (CTO, CFO, CMO, Legal, Producto, Operaciones): analizan en paralelo,
  cada uno desde su especialidad, y votan PROCEED, PIVOT o STOP con su confianza.
- **El cliente** participa desde el inicio: puede plantear la pregunta y su posición.
- **Consenso** por mayoría, con quórum; el disenso nunca se oculta.
- **Acta**: apertura, votos, síntesis, disenso y evidencia pedida quedan registrados.
Es una recomendación: la decisión es del cliente (Patrón A).
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import asdict, dataclass, field

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.router import for_tier
from app.ai.normalize import normalize_analysis_response, normalize_list, normalize_string


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
    decision: str  # PROCEED, PIVOT, STOP, or NO_CONSENSUS when there is no quorum
    score: float  # 0-100 aggregate
    confidence: float  # 0-100
    summary: str
    votes: list[AgentVote]
    concerns_unanimous: list[str] = field(default_factory=list)
    concerns_majority: list[str] = field(default_factory=list)
    strengths_unanimous: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    dissent: str = ""  # Every agent that disagrees with the decision, one per line
    # Flujo Maestro (AD-FUNC-02 §3)
    objective: str = ""            # apertura del CEO: objetivo de la sesión
    decision_at_stake: str = ""    # apertura del CEO: qué se decide
    synthesis: str = ""            # cierre del CEO: la voz de ADÁN
    evidence_requests: list[str] = field(default_factory=list)  # evidencia que el Board pide al cliente
    client_question: str = ""
    client_position: str = ""
    minutes: str = ""              # acta de la sesión

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BoardConsensus":
        votes = [AgentVote(**v) for v in data.get("votes", [])]
        known = set(cls.__dataclass_fields__)
        return cls(**{**{k: v for k, v in data.items() if k in known}, "votes": votes})


# El CEO preside; estos seis votan (AD-FUNC-02 §1)
SPECIALISTS = {
    "CTO": "viabilidad TÉCNICA: factibilidad, arquitectura, riesgos tecnológicos",
    "CFO": "viabilidad FINANCIERA: costos, ingresos, caja, sostenibilidad",
    "CMO": "MERCADO: dolor real, demanda, diferenciación, canales",
    "Legal": "riesgos LEGALES: regulación, contratos, propiedad intelectual, datos personales",
    "Producto": "PRODUCTO: problema-solución, usuario, alcance del MVP, experiencia",
    "Operaciones": "OPERACIÓN: procesos, recursos, proveedores, capacidad de ejecutar",
}

# Compatibilidad: quien importe AGENT_PROMPTS ve los roles que votan
AGENT_PROMPTS = {
    role: {
        "name": role,
        "system": (
            f"Eres el {role} del Board Room de ADÁN. Evalúas la {focus}. Decides con evidencia, no por "
            "preferencia: si falta evidencia, dilo y baja tu confianza. Responde en español con JSON: "
            "{analysis, justification, vote(PROCEED/PIVOT/STOP), confidence(0-100), key_strengths[], "
            "key_concerns[], questions[]}"
        ),
    }
    for role, focus in SPECIALISTS.items()
}

CEO_SYSTEM = (
    "Eres el CEO Agent de ADÁN y presides el Board Room (CEO, CTO, CFO, CMO, Legal, Producto, "
    "Operaciones). No votas: das la voz de ADÁN al cliente. Hablas en español, claro y breve."
)

# Esquema del voto: con salidas estructuradas el modelo no puede devolver JSON cortado o
# mal formado (WO-099; con qwen2.5:0.5b y 512 tokens todos los agentes se abstenían).
VOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "analysis": {"type": "string"},
        "justification": {"type": "string"},
        "vote": {"type": "string", "enum": ["PROCEED", "PIVOT", "STOP"]},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
        "key_strengths": {"type": "array", "items": {"type": "string"}},
        "key_concerns": {"type": "array", "items": {"type": "string"}},
        "questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["analysis", "justification", "vote", "confidence", "key_strengths", "key_concerns", "questions"],
    "additionalProperties": False,
}

OPENING_SCHEMA = {
    "type": "object",
    "properties": {
        "objective": {"type": "string"},
        "decision_at_stake": {"type": "string"},
    },
    "required": ["objective", "decision_at_stake"],
    "additionalProperties": False,
}

CLOSING_SCHEMA = {
    "type": "object",
    "properties": {
        "synthesis": {"type": "string"},
        "evidence_requests": {"type": "array", "items": {"type": "string"}},
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["synthesis", "evidence_requests", "next_steps"],
    "additionalProperties": False,
}


class BoardRoom:
    """Una sesión de Board Room según el Flujo Maestro de Orquestación (AD-FUNC-02 §3)."""

    def __init__(self, llm: LLMAdapter):
        # Votos: nivel "complex" (Claude Opus si hay clave). Apertura y cierre: "standard".
        self.llm = for_tier(llm, "complex")
        self.chair_llm = for_tier(llm, "standard")

    async def run(self, pain_description: str, conversation_context: str = "",
                  client_question: str = "", client_position: str = "") -> BoardConsensus:
        # 1. Habla primero el CEO: objetivo y decisión en juego
        opening = await self._open(pain_description, client_question, client_position)

        # 2. Los especialistas deliberan en paralelo, con la apertura y la posición del cliente
        briefing = self._briefing(opening, client_question, client_position)
        votes = await asyncio.gather(*[
            self._analyze_agent(role, config, pain_description, conversation_context + briefing)
            for role, config in AGENT_PROMPTS.items()
        ])

        # 3. Consenso por mayoría, con quórum y disenso visible
        consensus = self._build_consensus(list(votes))
        consensus.objective = opening["objective"]
        consensus.decision_at_stake = opening["decision_at_stake"]
        consensus.client_question = client_question
        consensus.client_position = client_position

        # 4. El CEO cierra: síntesis y evidencia que falta (antes de presentar la decisión)
        if consensus.decision != "NO_CONSENSUS":
            closing = await self._close(consensus, pain_description)
            consensus.synthesis = closing["synthesis"]
            consensus.evidence_requests = closing["evidence_requests"]
            consensus.next_steps = closing["next_steps"]
        consensus.minutes = self._minutes(consensus)
        return consensus

    async def _ask_json(self, llm, system: str, prompt: str, schema: dict, max_tokens: int) -> dict | None:
        messages = [LLMMessage(role="system", content=system), LLMMessage(role="user", content=prompt)]
        try:
            if isinstance(llm, LLMAdapter):
                response = await llm.chat_json(messages, schema, temperature=0.4, max_tokens=max_tokens)
                data = response.parsed
            else:
                response = await llm.chat(messages=messages, temperature=0.4, max_tokens=max_tokens)
                data = json.loads(response.content)
        except Exception:
            return None
        return data if isinstance(data, dict) else None

    async def _open(self, pain: str, question: str, position: str) -> dict:
        prompt = (
            f"Abre la sesión del Board Room.\n\nDolor o propuesta del cliente:\n{pain}\n\n"
            + (f"Pregunta del cliente: {question}\n" if question else "")
            + (f"Posición del cliente: {position}\n" if position else "")
            + "\nDeclara el objetivo de la sesión y la decisión concreta que está en juego. "
            "JSON: {objective, decision_at_stake}"
        )
        data = await self._ask_json(self.chair_llm, CEO_SYSTEM, prompt, OPENING_SCHEMA, 800) or {}
        return {
            "objective": normalize_string(data.get("objective"))
            or "Evaluar si el dolor planteado justifica avanzar con la empresa",
            "decision_at_stake": normalize_string(data.get("decision_at_stake"))
            or (question or "¿Avanzar (PROCEED), ajustar el rumbo (PIVOT) o detenerse (STOP)?"),
        }

    @staticmethod
    def _briefing(opening: dict, question: str, position: str) -> str:
        parts = [f"\n\nApertura del CEO — objetivo: {opening['objective']}. "
                 f"Decisión en juego: {opening['decision_at_stake']}"]
        if question:
            parts.append(f"Pregunta del cliente: {question}")
        if position:
            parts.append(f"Posición del cliente (tenla en cuenta, pero vota según la evidencia): {position}")
        return "\n".join(parts)

    async def _close(self, consensus: BoardConsensus, pain: str) -> dict:
        votes = "\n".join(f"- {v.agent}: {v.vote} ({v.confidence:.0f}%): {v.justification}"
                          for v in consensus.votes if v.vote != "ABSTAIN")
        prompt = (
            f"Cierra la sesión del Board Room.\n\nDolor del cliente:\n{pain}\n\n"
            f"Decisión del Board: {consensus.decision} (confianza promedio {consensus.confidence:.0f}%).\n"
            f"Votos:\n{votes}\n"
            + (f"\nDisenso:\n{consensus.dissent}\n" if consensus.dissent else "")
            + "\nEscribe la síntesis para el cliente: qué recomienda el Board y por qué, sin ocultar el "
            "disenso. Di qué evidencia falta pedirle al cliente para decidir mejor (datos verificables, "
            "no opiniones) y los próximos pasos. Recuerda que la decisión es del cliente. "
            "JSON: {synthesis, evidence_requests[], next_steps[]}"
        )
        data = await self._ask_json(self.chair_llm, CEO_SYSTEM, prompt, CLOSING_SCHEMA, 1500) or {}
        return {
            "synthesis": normalize_string(data.get("synthesis")),
            "evidence_requests": normalize_list(data.get("evidence_requests")),
            "next_steps": normalize_list(data.get("next_steps")),
        }

    @staticmethod
    def _minutes(c: BoardConsensus) -> str:
        """Acta de la sesión (AD-FUNC-02): queda en el Gemelo Digital como documento."""
        lines = [
            "# Acta del Board Room",
            "",
            "**Preside:** CEO Agent · **Votan:** " + ", ".join(SPECIALISTS) + " · **Participa:** el cliente",
            "",
            f"**Objetivo:** {c.objective}",
            f"**Decisión en juego:** {c.decision_at_stake}",
        ]
        if c.client_question or c.client_position:
            lines += ["", "## Cliente"]
            if c.client_question:
                lines.append(f"- Pregunta: {c.client_question}")
            if c.client_position:
                lines.append(f"- Posición: {c.client_position}")
        lines += ["", "## Votos"]
        for v in c.votes:
            lines.append(f"- **{v.agent}**: {v.vote} ({v.confidence:.0f}%). {v.justification}")
        lines += ["", f"## Resultado: {c.decision}",
                  f"Score {c.score:.0f}/100 · confianza promedio {c.confidence:.0f}%"]
        if c.dissent:
            lines += ["", "## Disenso", c.dissent]
        if c.synthesis:
            lines += ["", "## Síntesis del CEO", c.synthesis]
        if c.evidence_requests:
            lines += ["", "## Evidencia que el Board pide"] + [f"- {e}" for e in c.evidence_requests]
        if c.next_steps:
            lines += ["", "## Próximos pasos"] + [f"- {n}" for n in c.next_steps]
        lines += ["", "La decisión es del cliente: esto es una recomendación del Board (Patrón A)."]
        return "\n".join(lines)

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
            messages = [
                LLMMessage(role="system", content=agent_config["system"]),
                LLMMessage(role="user", content=prompt),
            ]
            if isinstance(self.llm, LLMAdapter):
                response = await self.llm.chat_json(messages, VOTE_SCHEMA, temperature=0.6, max_tokens=1500)
            else:
                response = await self.llm.chat(messages=messages, temperature=0.6, max_tokens=1500)
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
            raw_data = getattr(response, "parsed", None)
            if not isinstance(raw_data, dict):
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
