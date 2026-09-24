"""
Decision Engine — Consolidación de respuestas con justificación.

Evalúa la calidad de las respuestas, genera justificaciones,
y decide cuándo entregar vs cuándo revisar.
"""

from dataclasses import dataclass, field


@dataclass
class DecisionJustification:
    """Justificación de una decisión del sistema."""
    decision: str
    confidence: float  # 0-1
    reasoning: str
    supporting_facts: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    risk_assessment: str = ""


@dataclass
class QualityAssessment:
    """Evaluación de calidad de una respuesta."""
    overall_score: float  # 0-1
    dimensions: dict[str, float] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    approved: bool = True


class DecisionEngine:
    """
    Motor de decisiones que evalúa y consolida respuestas.
    """

    def evaluate_response(
        self,
        response: str,
        user_message: str,
        knowledge_context: str,
        board_consensus: dict | None = None,
    ) -> tuple[str, DecisionJustification]:
        """
        Evalúa una respuesta y genera justificación.
        
        Retorna (respuesta_final, justificación).
        """
        # Evaluar calidad
        quality = self._assess_quality(response, user_message, knowledge_context)

        # Si la calidad es baja, marcar como "respuesta con limitaciones"
        if not quality.approved:
            response = self._add_quality_disclaimer(response, quality)

        # Generar justificación
        justification = self._build_justification(
            response=response,
            user_message=user_message,
            knowledge_context=knowledge_context,
            board_consensus=board_consensus,
            quality=quality,
        )

        return response, justification

    def _assess_quality(
        self, response: str, user_message: str, knowledge_context: str
    ) -> QualityAssessment:
        """Evalúa la calidad de una respuesta."""
        dimensions = {}

        # 1. Completitud: ¿responde lo que preguntó?
        completeness = self._assess_completeness(response, user_message)
        dimensions["completeness"] = completeness

        # 2. Relevancia: ¿la información es relevante?
        relevance = self._assess_relevance(response, knowledge_context)
        dimensions["relevance"] = relevance

        # 3. Claridad: ¿la respuesta es clara?
        clarity = self._assess_clarity(response)
        dimensions["clarity"] = clarity

        # 4. Longitud: ¿es suficientemente detallada?
        length_score = min(len(response) / 200, 1.0)
        dimensions["length"] = length_score

        # Score general
        overall = (
            0.35 * completeness +
            0.30 * relevance +
            0.20 * clarity +
            0.15 * length_score
        )

        issues = []
        if completeness < 0.5:
            issues.append("La respuesta puede no cubrir todos los aspectos solicitados")
        if relevance < 0.5:
            issues.append("La respuesta puede incluir información no relevante")
        if clarity < 0.5:
            issues.append("La respuesta podría ser más clara")

        return QualityAssessment(
            overall_score=overall,
            dimensions=dimensions,
            issues=issues,
            approved=overall >= 0.4,
        )

    def _assess_completeness(self, response: str, user_message: str) -> float:
        """Evalúa si la respuesta cubre lo solicitado."""
        # Heurística: ¿la respuesta menciona los temas del usuario?
        user_words = set(user_message.lower().split())
        response_words = set(response.lower().split())
        overlap = len(user_words & response_words)
        return min(overlap / max(len(user_words), 1), 1.0)

    def _assess_relevance(self, response: str, knowledge_context: str) -> float:
        """Evalúa si la respuesta es relevante al contexto."""
        if not knowledge_context:
            return 0.7  # Sin contexto, asumir relevancia media
        # Heurística: ¿la respuesta usa información del contexto?
        ctx_words = set(knowledge_context.lower().split())
        resp_words = set(response.lower().split())
        overlap = len(ctx_words & resp_words)
        return min(overlap / max(len(ctx_words) * 0.3, 1), 1.0)

    def _assess_clarity(self, response: str) -> float:
        """Evalúa la claridad de la respuesta."""
        # Heurísticas simples
        score = 1.0

        # Penalizar oraciones muy largas
        sentences = response.split(".")
        avg_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
        if avg_length > 30:
            score -= 0.2

        # Penalizar demasiada jerga técnica sin explicar
        tech_words = {"api", "json", "http", "db", "sql", "orm", "dto", "crud"}
        tech_count = sum(1 for w in response.lower().split() if w in tech_words)
        if tech_count > 5:
            score -= 0.1

        # Bonificar estructura (listas, viñetas)
        if any(c in response for c in ["- ", "• ", "1.", "2.", "3."]):
            score += 0.1

        return max(0.0, min(1.0, score))

    def _add_quality_disclaimer(self, response: str, quality: QualityAssessment) -> str:
        """Agrega disclaimer de calidad a respuestas con issues."""
        disclaimer_parts = ["\n\n---"]

        if quality.dimensions.get("completeness", 1) < 0.5:
            disclaimer_parts.append(
                "Nota: Esta respuesta puede no cubrir todos los aspectos de tu pregunta. "
                "¿Hay algo específico que quieras que profundice?"
            )

        if quality.dimensions.get("relevance", 1) < 0.5:
            disclaimer_parts.append(
                "Nota: La información disponible es limitada. "
                "Para un análisis más completo, necesitaría más contexto."
            )

        return response + "\n".join(disclaimer_parts)

    def _build_justification(
        self,
        response: str,
        user_message: str,
        knowledge_context: str,
        board_consensus: dict | None,
        quality: QualityAssessment,
    ) -> DecisionJustification:
        """Construye la justificación de la respuesta."""
        supporting = []
        alternatives = []

        # Hechos de soporte
        if knowledge_context:
            for line in knowledge_context.split("\n"):
                if line.strip() and ":" in line:
                    supporting.append(line.strip())

        # Alternativas consideradas
        if board_consensus:
            if board_consensus.get("consensus") == "PROCEED":
                alternatives.append("Board Room recomienda PROCEED")
            elif board_consensus.get("consensus") == "PIVOT":
                alternatives.append("Board Room recomienda cambios en el enfoque")
            elif board_consensus.get("consensus") == "STOP":
                alternatives.append("Board Room recomienda pausar y reevaluar")
        else:
            alternatives.append("Análisis directo sin Board Room (solicitud simple)")

        # Confianza basada en calidad
        confidence = quality.overall_score

        return DecisionJustification(
            decision="Entregar respuesta generada",
            confidence=confidence,
            reasoning=f"Respuesta generada con score de calidad {quality.overall_score:.2f}. "
                      f"Dimensiones: completitud={quality.dimensions.get('completeness', 0):.2f}, "
                      f"relevancia={quality.dimensions.get('relevance', 0):.2f}, "
                      f"claridad={quality.dimensions.get('clarity', 0):.2f}",
            supporting_facts=supporting[:5],
            alternatives=alternatives,
            risk_assessment=f"Issues detectados: {len(quality.issues)}. "
                           f"{'Respuesta aprobada.' if quality.approved else 'Respuesta con limitaciones.'}",
        )
