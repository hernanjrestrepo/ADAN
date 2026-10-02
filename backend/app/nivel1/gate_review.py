"""Gate Review de un Nivel sobre evidencia registrada (WO-107, cierra B5 de la auditoría).

Antes, el Gate contaba palabras clave en un diagnóstico que escribió el mismo LLM, al que se
le pedía incluir esas palabras. Ahora decide solo sobre la evidencia clasificada del Gemelo
(AD-CMP-05) con la regla del Nivel (app/scoring/engine.py, GATE_RULES):

- Evidencia suficiente → se propone cerrar el Nivel; se cierra solo si el cliente aprueba.
- Evidencia insuficiente → ADÁN dice exactamente qué falta. El cliente puede avanzar igual,
  bajo su responsabilidad: queda como decisión distinta a la recomendada, con los 6 campos
  de AD-FUNC-02 §2.5 (AD-CMP-01 §3).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GateReviewResult:
    approved: bool          # la evidencia alcanza (falta la aprobación del cliente)
    overall_score: float    # Score de la dimensión del Nivel (Problem Score en el Nivel 1)
    confidence: float
    missing: list[str] = field(default_factory=list)
    breakdown: dict = field(default_factory=dict)
    message: str = ""


def build_result(level_number: int, evaluation) -> GateReviewResult:
    s = evaluation.score
    if evaluation.sufficient:
        message = (f"La evidencia alcanza para cerrar el Nivel {level_number}: Problem Score {s.value:.0f}/100 "
                   f"con {s.confidence:.0f} % de confianza. Falta tu aprobación para cerrar el Nivel {level_number}.")
    else:
        # Lo que falta va aparte (`missing`), en una lista que el cliente puede seguir punto por punto
        message = (f"Todavía no hay evidencia suficiente para cerrar el Nivel {level_number} "
                   f"(Problem Score {s.value:.0f}/100, confianza {s.confidence:.0f} %).")
    return GateReviewResult(evaluation.sufficient, s.value, s.confidence, list(evaluation.missing),
                            s.breakdown, message)
