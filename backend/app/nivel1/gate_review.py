"""Gate Review Engine — DETERMINISTIC evaluation with 80/100 minimum threshold.

The scoring is rule-based, NOT LLM-dependent.
The LLM can provide observations, but the calculation is deterministic.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class GateReviewResult:
    approved: bool
    overall_score: float  # 0-100
    criteria_scores: dict  # criterion -> score (0-100)
    observations: list[str]
    blocking_issues: list[str]
    recommendations: list[str]
    message: str


# Evaluation criteria with weights
CRITERIA = {
    "problem_clarity": {
        "name": "Claridad del Problema",
        "weight": 0.20,
    },
    "evidence_quality": {
        "name": "Calidad de la Evidencia",
        "weight": 0.20,
    },
    "market_validation": {
        "name": "Validación de Mercado",
        "weight": 0.15,
    },
    "solution_viability": {
        "name": "Viabilidad de la Solución",
        "weight": 0.15,
    },
    "financial_feasibility": {
        "name": "Factibilidad Financiera",
        "weight": 0.10,
    },
    "board_alignment": {
        "name": "Alineación del Board Room",
        "weight": 0.10,
    },
    "deliverable_completeness": {
        "name": "Completitud del Entregable",
        "weight": 0.10,
    },
}

MINIMUM_PASSING_SCORE = 80


class GateReviewEngine:
    """Deterministic Gate Review — rules, not LLM, for scoring."""

    def evaluate(
        self,
        diagnosis: str,
        board_votes: list[dict],
        scores: list[dict],
        deliverables: list[str],
        conversation_messages: list[dict],
    ) -> GateReviewResult:
        """Run deterministic Gate Review evaluation."""

        criteria_scores = {}
        observations = []
        blocking_issues = []
        recommendations = []

        # --- Criterion 1: Problem Clarity (0-100) ---
        clarity_score, clarity_obs = self._evaluate_problem_clarity(diagnosis, conversation_messages)
        criteria_scores["problem_clarity"] = clarity_score
        observations.extend(clarity_obs)
        if clarity_score < 50:
            blocking_issues.append("Problema no está claramente definido")
            recommendations.append("Profundizar en la descripción del problema")

        # --- Criterion 2: Evidence Quality (0-100) ---
        evidence_score, evidence_obs = self._evaluate_evidence_quality(diagnosis, conversation_messages)
        criteria_scores["evidence_quality"] = evidence_score
        observations.extend(evidence_obs)
        if evidence_score < 40:
            blocking_issues.append("Evidencia insuficiente para respaldar el problema")
            recommendations.append("Agregar datos concretos: cifras, fuentes, casos de uso")

        # --- Criterion 3: Market Validation (0-100) ---
        market_score, market_obs = self._evaluate_market_validation(diagnosis, conversation_messages)
        criteria_scores["market_validation"] = market_score
        observations.extend(market_obs)
        if market_score < 40:
            recommendations.append("Validar con clientes potenciales reales")

        # --- Criterion 4: Solution Viability (0-100) ---
        solution_score, solution_obs = self._evaluate_solution_viability(diagnosis, board_votes)
        criteria_scores["solution_viability"] = solution_score
        observations.extend(solution_obs)
        if solution_score < 40:
            blocking_issues.append("Solución no técnicamente viable")
            recommendations.append("Revisar viabilidad técnica con expertos")

        # --- Criterion 5: Financial Feasibility (0-100) ---
        financial_score, financial_obs = self._evaluate_financial_feasibility(diagnosis, conversation_messages)
        criteria_scores["financial_feasibility"] = financial_score
        observations.extend(financial_obs)
        if financial_score < 40:
            recommendations.append("Desarrollar modelo financiero detallado")

        # --- Criterion 6: Board Alignment (0-100) ---
        board_score, board_obs = self._evaluate_board_alignment(board_votes)
        criteria_scores["board_alignment"] = board_score
        observations.extend(board_obs)
        if board_score < 50:
            blocking_issues.append("Board Room sin consenso mayoritario")
            recommendations.append("Abordar las preocupaciones de los agentes disidentes")

        # --- Criterion 7: Deliverable Completeness (0-100) ---
        deliverable_score, deliverable_obs = self._evaluate_deliverables(diagnosis, deliverables, scores)
        criteria_scores["deliverable_completeness"] = deliverable_score
        observations.extend(deliverable_obs)
        if deliverable_score < 50:
            blocking_issues.append("Entregables incompletos")
            recommendations.append("Completar todos los entregables requeridos")

        # --- Calculate weighted overall score ---
        overall_score = 0.0
        for criterion, config in CRITERIA.items():
            overall_score += criteria_scores.get(criterion, 0) * config["weight"]

        # --- Determine approval ---
        approved = overall_score >= MINIMUM_PASSING_SCORE and len(blocking_issues) == 0

        # --- Build message ---
        if approved:
            message = (
                f"Gate Review APROBADO. Score: {overall_score:.0f}/100 "
                f"(mínimo: {MINIMUM_PASSING_SCORE}/100). "
                f"Nivel 1 completado exitosamente."
            )
        else:
            issues_text = "; ".join(blocking_issues) if blocking_issues else "Score insuficiente"
            message = (
                f"Gate Review NO APROBADO. Score: {overall_score:.0f}/100 "
                f"(mínimo: {MINIMUM_PASSING_SCORE}/100). "
                f"Problemas: {issues_text}"
            )

        return GateReviewResult(
            approved=approved,
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            observations=observations,
            blocking_issues=blocking_issues,
            recommendations=recommendations,
            message=message,
        )

    def _evaluate_problem_clarity(self, diagnosis: str, messages: list[dict]) -> tuple[float, list[str]]:
        """Evaluate how clearly the problem is defined."""
        score = 0
        obs = []

        # Check diagnosis length (longer = more detailed)
        if len(diagnosis) > 3000:
            score += 30
            obs.append("Diagnóstico detallado (3000+ caracteres)")
        elif len(diagnosis) > 1000:
            score += 20
            obs.append("Diagnóstico con tamaño adecuado")
        else:
            score += 5
            obs.append("Diagnóstico demasiado corto")

        # Check for key problem indicators in diagnosis
        problem_indicators = ["problema", "dolor", "necesidad", "solución", "mercado", "cliente"]
        found = sum(1 for ind in problem_indicators if ind.lower() in diagnosis.lower())
        score += min(found * 10, 40)
        obs.append(f"Indicadores de problema encontrados: {found}/{len(problem_indicators)}")

        # Check conversation depth
        user_msgs = [m for m in messages if m.get("role") == "user"]
        if len(user_msgs) >= 3:
            score += 30
            obs.append(f"Conversación profunda ({len(user_msgs)} mensajes del usuario)")
        elif len(user_msgs) >= 1:
            score += 15
            obs.append(f"Conversación básica ({len(user_msgs)} mensajes)")
        else:
            obs.append("Sin mensajes del usuario")

        return min(score, 100), obs

    def _evaluate_evidence_quality(self, diagnosis: str, messages: list[dict]) -> tuple[float, list[str]]:
        """Evaluate the quality of evidence presented."""
        score = 0
        obs = []

        # Check for quantitative evidence
        numbers = re.findall(r'\d+[\.,]?\d*\s*(USD|dólares|\$|empresas|clientes|mes|año|%)', diagnosis)
        if len(numbers) >= 3:
            score += 40
            obs.append(f"Evidencia cuantitativa fuerte ({len(numbers)} datos numéricos)")
        elif len(numbers) >= 1:
            score += 20
            obs.append(f"Evidencia cuantitativa limitada ({len(numbers)} datos)")
        else:
            obs.append("Sin evidencia cuantitativa en el diagnóstico")

        # Check for specific market data
        market_terms = ["mercado", "competidor", "cliente", "demanda", "sector", "industria"]
        found = sum(1 for term in market_terms if term.lower() in diagnosis.lower())
        score += min(found * 10, 30)

        # Check conversation has substance
        user_msgs = [m for m in messages if m.get("role") == "user"]
        total_chars = sum(len(m.get("content", "")) for m in user_msgs)
        if total_chars > 500:
            score += 30
            obs.append(f"Conversación sustancial ({total_chars} caracteres del usuario)")
        elif total_chars > 100:
            score += 15
        else:
            obs.append("Conversación escasa")

        return min(score, 100), obs

    def _evaluate_market_validation(self, diagnosis: str, messages: list[dict]) -> tuple[float, list[str]]:
        """Evaluate market validation evidence."""
        score = 0
        obs = []

        # Check for market size mentions
        market_indicators = ["mercado", "empresas", "clientes", "demanda", "necesitan", "problema"]
        found = sum(1 for ind in market_indicators if ind.lower() in diagnosis.lower())
        score += min(found * 12, 50)

        # Check for competition awareness
        competition_terms = ["competidor", "competencia", "alternativa", "diferente", "único"]
        found_comp = sum(1 for term in competition_terms if term.lower() in diagnosis.lower())
        if found_comp > 0:
            score += 25
            obs.append("Conciencia de competencia presente")
        else:
            obs.append("Sin mención de competencia")
            score += 5

        # Check for customer validation
        customer_terms = ["cliente", "usuario", "encuesta", "entrevista", "validación"]
        found_cust = sum(1 for term in customer_terms if term.lower() in diagnosis.lower())
        score += min(found_cust * 15, 25)

        if found_comp > 0 and found_cust > 0:
            obs.append("Validación de mercado razonable")
        else:
            obs.append("Validación de mercado incompleta")

        return min(score, 100), obs

    def _evaluate_solution_viability(self, diagnosis: str, board_votes: list[dict]) -> tuple[float, list[str]]:
        """Evaluate solution viability based on board votes."""
        score = 50  # Base score
        obs = []

        if not board_votes:
            obs.append("Sin votos del Board Room")
            return 30, obs

        # Count PROCEED vs STOP vs PIVOT
        proceed = sum(1 for v in board_votes if v.get("vote") == "PROCEED")
        pivot = sum(1 for v in board_votes if v.get("vote") == "PIVOT")
        stop = sum(1 for v in board_votes if v.get("vote") == "STOP")
        total = len(board_votes)

        if proceed > total / 2:
            score = 80 + (proceed / total) * 20
            obs.append(f"Mayoría PROCEED ({proceed}/{total})")
        elif stop > total / 2:
            score = 20 + (1 - stop / total) * 30
            obs.append(f"Mayoría STOP ({stop}/{total}) — riesgo alto")
        elif pivot > 0:
            score = 50 + pivot * 10
            obs.append(f"Votos mixtos con PIVOT ({pivot}/{total})")
        else:
            score = 50
            obs.append("Votos sin mayoría clara")

        # Check average confidence
        confidences = [v.get("confidence", 50) for v in board_votes]
        avg_conf = sum(confidences) / len(confidences) if confidences else 50
        if avg_conf > 80:
            score = min(score + 10, 100)
            obs.append(f"Alta confianza promedio ({avg_conf:.0f}%)")
        elif avg_conf < 50:
            score = max(score - 10, 0)
            obs.append(f"Baja confianza promedio ({avg_conf:.0f}%)")

        return min(score, 100), obs

    def _evaluate_financial_feasibility(self, diagnosis: str, messages: list[dict]) -> tuple[float, list[str]]:
        """Evaluate financial feasibility."""
        score = 30  # Base — not enough info
        obs = []

        # Check for financial indicators
        financial_terms = ["precio", "costo", "ingreso", "ganancia", "inversión", "ROI", "USD", "dólares", "mensual"]
        found = sum(1 for term in financial_terms if term.lower() in diagnosis.lower())
        score += min(found * 10, 40)

        # Check for pricing model
        pricing_terms = ["USD/mes", "suscripción", "precio", "plan", "tier"]
        found_price = sum(1 for term in pricing_terms if term.lower() in diagnosis.lower())
        if found_price > 0:
            score += 20
            obs.append("Modelo de precios mencionado")
        else:
            obs.append("Sin modelo de precios definido")

        # Check for numbers in conversation
        user_msgs = [m for m in messages if m.get("role") == "user"]
        all_text = " ".join(m.get("content", "") for m in user_msgs)
        price_mentions = re.findall(r'\d+\s*(USD|dólares|\$)', all_text)
        if price_mentions:
            score += 10

        return min(score, 100), obs

    def _evaluate_board_alignment(self, board_votes: list[dict]) -> tuple[float, list[str]]:
        """Evaluate Board Room alignment."""
        if not board_votes:
            return 0, ["Sin votos del Board Room"]

        proceed = sum(1 for v in board_votes if v.get("vote") == "PROCEED")
        total = len(board_votes)
        ratio = proceed / total

        obs = []
        if ratio >= 0.75:
            score = 90
            obs.append(f"Mayoría fuerte PROCEED ({proceed}/{total})")
        elif ratio >= 0.5:
            score = 70
            obs.append(f"Mayoría PROCEED ({proceed}/{total})")
        elif ratio >= 0.25:
            score = 40
            obs.append(f"Votos divididos ({proceed}/{total} PROCEED)")
        else:
            score = 15
            obs.append(f"Mayoría STOP ({total - proceed}/{total})")

        return min(score, 100), obs

    def _evaluate_deliverables(self, diagnosis: str, deliverables: list[str], scores: list[dict]) -> tuple[float, list[str]]:
        """Evaluate deliverable completeness."""
        score = 0
        obs = []

        # Check diagnosis exists and has content
        if diagnosis and len(diagnosis) > 500:
            score += 30
            obs.append("Diagnóstico presente y sustancial")
        elif diagnosis:
            score += 15
            obs.append("Diagnóstico presente pero corto")
        else:
            obs.append("Sin diagnóstico")

        # Check scores exist
        if scores:
            score += 25
            obs.append(f"{len(scores)} scores calculados")
        else:
            obs.append("Sin scores calculados")

        # Check documents exist
        if deliverables:
            score += 25
            obs.append(f"{len(deliverables)} documentos generados")
        else:
            obs.append("Sin documentos generados")

        # Check conversation happened
        if any("conversación" in d.lower() or "chat" in d.lower() for d in deliverables):
            score += 20
        elif len(deliverables) > 0:
            score += 10

        return min(score, 100), obs
