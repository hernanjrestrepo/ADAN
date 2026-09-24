"""
Learning Engine — Aprendizaje organizacional.

Guarda decisiones, resultados, éxito/fracaso y genera mejoras.
"""

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class LearningRecord:
    """Registro de aprendizaje."""
    id: str
    timestamp: datetime
    context: str
    decision: str
    outcome: str                         # success, failure, partial
    quality_score: float
    lesson_learned: str
    recommendation: str
    metadata: dict = field(default_factory=dict)


class LearningEngine:
    """
    Motor de aprendizaje que:
    - Registra decisiones y resultados
    - Detecta patrones de éxito/fracaso
    - Genera recomendaciones
    - Alimenta la memoria organizacional
    """

    def __init__(self):
        self._records: list[LearningRecord] = []

    def record_decision(
        self,
        context: str,
        decision: str,
        outcome: str,
        quality_score: float,
        lesson: str = "",
        recommendation: str = "",
        metadata: dict | None = None,
    ) -> LearningRecord:
        """Registra una decisión y su resultado."""
        record = LearningRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            context=context,
            decision=decision,
            outcome=outcome,
            quality_score=quality_score,
            lesson_learned=lesson,
            recommendation=recommendation,
            metadata=metadata or {},
        )
        self._records.append(record)
        return record

    def get_patterns(self) -> dict:
        """Detecta patrones de éxito y fracaso."""
        if not self._records:
            return {"success_rate": 0, "total": 0, "patterns": []}

        total = len(self._records)
        successes = sum(1 for r in self._records if r.outcome == "success")
        failures = sum(1 for r in self._records if r.outcome == "failure")

        # Detectar patrones por contexto
        context_patterns = {}
        for record in self._records:
            ctx = record.context[:50]
            if ctx not in context_patterns:
                context_patterns[ctx] = {"success": 0, "failure": 0}
            if record.outcome == "success":
                context_patterns[ctx]["success"] += 1
            else:
                context_patterns[ctx]["failure"] += 1

        return {
            "success_rate": round(successes / total * 100, 1) if total > 0 else 0,
            "total": total,
            "successes": successes,
            "failures": failures,
            "avg_quality": round(sum(r.quality_score for r in self._records) / total, 2) if total > 0 else 0,
            "context_patterns": context_patterns,
        }

    def get_recommendations(self) -> list[str]:
        """Genera recomendaciones basadas en el historial."""
        recommendations = []

        patterns = self.get_patterns()
        if patterns["success_rate"] < 50:
            recommendations.append("Tasa de éxito baja. Revisar proceso de toma de decisiones.")

        if patterns["failures"] > patterns["successes"]:
            recommendations.append("Más fracasos que éxitos. Considerar cambiar estrategia.")

        # Recomendaciones de lessons
        for record in self._records:
            if record.outcome == "failure" and record.lesson_learned:
                recommendations.append(f"Aprender de: {record.lesson_learned[:100]}")

        return list(set(recommendations))[:10]

    def get_all(self) -> list[dict]:
        """Retorna todos los registros."""
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp.isoformat(),
                "context": r.context,
                "decision": r.decision,
                "outcome": r.outcome,
                "quality_score": r.quality_score,
                "lesson_learned": r.lesson_learned,
                "recommendation": r.recommendation,
            }
            for r in self._records
        ]
