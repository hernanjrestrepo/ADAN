"""Motor de Scoring (AD-ARQ-10 v0, WO-107) — funciones puras, sin base de datos ni LLM.

AD-ARQ-10 no estaba escrito: esta es su primera versión, decidida por delegación de Hernán
(docs/wo/WO-107_REPORTE.md §4). Implementa el proceso de AD-CMP-05:

    afirmaciones → clasificadas por la jerarquía de validez → agregadas por dimensión
    → Score con su Confidence Level declarado

Jerarquía de validez (AD-CMP-05 §1) y su peso:

| Nivel | Tipo | Peso | Techo de confianza |
|---|---|---|---|
| 1 | Dato verificable externamente (`external`) | 1.0 | 95 % |
| 2 | Testimonio directo del cliente (`testimony`) | 0.6 | 75 % |
| 3 | Inferencia razonada de un Agente (`inference`) | 0.3 | 40 % |

- **Valor (0-100):** respaldo / (respaldo + contradicción + PRIOR). El PRIOR hace que poca
  evidencia no produzca un valor alto: una sola inferencia a favor da ~17, no 100.
- **Confianza (0-100):** crece con la cantidad de evidencia ponderada (1 - e^(-masa/2)) y
  nunca supera el techo del mejor nivel presente: si solo hay inferencias, la confianza
  queda en 40 % como máximo, por mucho que se haya conversado (AD-CMP-05 §1: "la
  inspección de una Conversación, por sí sola, nunca es evidencia suficiente").
- **Sin evidencia:** el Score se declara igual, con valor 0 y confianza 0, y lo dice
  (AD-CMP-05 §2: nunca se omite ni se rellena con un valor que aparente certeza).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

EXTERNAL, TESTIMONY, INFERENCE = "external", "testimony", "inference"
SUPPORTS, CONTRADICTS = "supports", "contradicts"

TIERS = {
    EXTERNAL: {"weight": 1.0, "ceiling": 95.0, "label": "Dato verificable externamente"},
    TESTIMONY: {"weight": 0.6, "ceiling": 75.0, "label": "Testimonio del cliente"},
    INFERENCE: {"weight": 0.3, "ceiling": 40.0, "label": "Inferencia de un Agente"},
}
PRIOR = 1.5

# Los 8 Scores de AD-FUNC-07 §2
DIAGNOSTIC = {  # Familia 1: anclados a un Nivel
    "problem": {"label": "Problem Score", "level": 1, "measures": "Qué tan real y validado está el problema"},
    "solution": {"label": "Solution Score", "level": 2,
                 "measures": "Qué tan diferenciada es la solución frente al mercado y los competidores"},
    "business": {"label": "Business Score", "level": 3,
                 "measures": "Qué tan sólidos son el capital, la estructura y el plan"},
    "product": {"label": "Product Score", "level": 4,
                "measures": "Qué tan cerca está el producto construido de la propuesta"},
    "market": {"label": "Market Score", "level": 5,
               "measures": "Qué tan bien resiste la propuesta los escenarios de mercado"},
    "execution": {"label": "Execution Score", "level": 5,
                  "measures": "Qué tan bien ejecuta el equipo bajo presión"},
}
CONTINUOUS = {  # Familia 2: continuos
    "responsible": {"label": "Score del Responsable", "level": None,
                    "measures": "Track record de decisiones y ejecución de la persona responsable"},
    "venture": {"label": "Venture Score", "level": 6,
                "measures": "Salud agregada de la Empresa como conjunto"},
}
ALL_SCORES = {**DIAGNOSTIC, **CONTINUOUS}


@dataclass(frozen=True)
class EvidenceItem:
    kind: str           # external | testimony | inference
    polarity: str = SUPPORTS
    id: str | None = None


@dataclass
class ScoreResult:
    score_type: str
    value: float
    confidence: float
    reasoning: str
    breakdown: dict = field(default_factory=dict)
    sufficient_evidence: bool = False


def _breakdown(items: list[EvidenceItem]) -> dict:
    out = {k: {SUPPORTS: 0, CONTRADICTS: 0} for k in TIERS}
    for item in items:
        if item.kind in out:
            out[item.kind][CONTRADICTS if item.polarity == CONTRADICTS else SUPPORTS] += 1
    return out


def score_dimension(score_type: str, items: list[EvidenceItem]) -> ScoreResult:
    """Score de una dimensión a partir de su evidencia clasificada (AD-CMP-05 §2)."""
    valid = [i for i in items if i.kind in TIERS]  # ninguna afirmación sin clasificar entra
    breakdown = _breakdown(valid)
    label = ALL_SCORES.get(score_type, {}).get("label", score_type)
    if not valid:
        return ScoreResult(score_type, 0.0, 0.0,
                           f"{label}: sin evidencia registrada. No se puede afirmar nada todavía.", breakdown)

    support = sum(TIERS[i.kind]["weight"] for i in valid if i.polarity != CONTRADICTS)
    against = sum(TIERS[i.kind]["weight"] for i in valid if i.polarity == CONTRADICTS)
    value = 100.0 * support / (support + against + PRIOR)

    mass = support + against
    ceiling = max(TIERS[i.kind]["ceiling"] for i in valid)
    confidence = min(ceiling, 100.0 * (1 - math.exp(-mass / 2)))

    parts = []
    for kind, counts in breakdown.items():
        n = counts[SUPPORTS] + counts[CONTRADICTS]
        if n:
            parts.append(f"{TIERS[kind]['label'].lower()}: {counts[SUPPORTS]} a favor, {counts[CONTRADICTS]} en contra")
    only_inference = all(i.kind == INFERENCE for i in valid)
    reasoning = f"{label}: " + "; ".join(parts) + "."
    if only_inference:
        reasoning += " Solo hay inferencias de Agentes: no es evidencia suficiente por sí sola."
    return ScoreResult(score_type, round(value, 1), round(confidence, 1), reasoning, breakdown)


# ------------------------------------------------------------------
# Gate de Nivel (AD-CMP-01 §1-2, AD-FUNC-01): umbral de "evidencia suficiente"
# ------------------------------------------------------------------

@dataclass(frozen=True)
class GateRule:
    score_type: str
    min_value: float
    min_confidence: float
    min_external_support: int      # datos verificables a favor
    min_client_or_external: int    # testimonio o dato externo a favor (en total)


# Nivel 1 (AD-FUNC-01): "requiere evidencia externa suficiente"
GATE_RULES = {1: GateRule("problem", min_value=60.0, min_confidence=50.0,
                          min_external_support=1, min_client_or_external=2)}


@dataclass
class GateEvaluation:
    level_number: int
    sufficient: bool
    score: ScoreResult
    missing: list[str]


def evaluate_gate(level_number: int, items: list[EvidenceItem]) -> GateEvaluation:
    rule = GATE_RULES[level_number]
    result = score_dimension(rule.score_type, items)
    b = result.breakdown
    external = b[EXTERNAL][SUPPORTS]
    strong = external + b[TESTIMONY][SUPPORTS]
    missing = []
    if external < rule.min_external_support:
        missing.append(f"Al menos {rule.min_external_support} dato verificable externamente que respalde el problema "
                       "(un estudio, una estadística, un registro público, un documento)")
    if strong < rule.min_client_or_external:
        missing.append(f"Al menos {rule.min_client_or_external} evidencias a favor entre datos externos y "
                       f"testimonios (tienes {strong})")
    if result.value < rule.min_value:
        missing.append(f"{ALL_SCORES[rule.score_type]['label']} de {rule.min_value:.0f} o más "
                       f"(hoy {result.value:.0f})")
    if result.confidence < rule.min_confidence:
        missing.append(f"Confianza de {rule.min_confidence:.0f} % o más (hoy {result.confidence:.0f} %)")
    result.sufficient_evidence = not missing
    return GateEvaluation(level_number, not missing, result, missing)


# ------------------------------------------------------------------
# Scores continuos (AD-FUNC-07 §3-4)
# ------------------------------------------------------------------

def responsible_score(decided: int, executed: int, divergent_documented: int, levels_completed: int) -> ScoreResult:
    """Score del Responsable: track record sobre Decisiones reales, nunca impresión de un Agente.

    - Cada decisión tomada es testimonio del propio responsable (peso de testimonio).
    - Cada decisión llevada a ejecución y cada Nivel cerrado con evidencia son hechos
      verificables en el Gemelo (peso de dato externo).
    - Decidir distinto a lo recomendado no resta: está documentado (AD-FUNC-02 §2.5).
    """
    items = [EvidenceItem(TESTIMONY)] * decided + [EvidenceItem(EXTERNAL)] * (executed + levels_completed)
    result = score_dimension("responsible", items)
    if decided == 0:
        result.reasoning = "Score del Responsable: todavía no hay decisiones tomadas en ADÁN."
    else:
        result.reasoning = (f"Score del Responsable: {decided} decisiones tomadas, {executed} ejecutadas, "
                            f"{levels_completed} Niveles cerrados; {divergent_documented} decisiones distintas "
                            "a lo recomendado, todas documentadas.")
    return result


def venture_score(latest: dict[str, tuple[float, float]]) -> ScoreResult:
    """Venture Score: agrega los Scores de diagnóstico más recientes, ponderados por su confianza."""
    rows = [(v, c) for t, (v, c) in latest.items() if t in DIAGNOSTIC and c > 0]
    if not rows:
        return ScoreResult("venture", 0.0, 0.0, "Venture Score: aún no hay Scores de diagnóstico con evidencia.")
    weight = sum(c for _, c in rows)
    value = sum(v * c for v, c in rows) / weight
    confidence = min(c for _, c in rows) * min(1.0, len(rows) / len(DIAGNOSTIC))
    return ScoreResult("venture", round(value, 1), round(confidence, 1),
                       f"Venture Score: agrega {len(rows)} de {len(DIAGNOSTIC)} Scores de diagnóstico.")
