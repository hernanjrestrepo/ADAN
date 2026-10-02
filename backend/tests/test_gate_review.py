"""Motor de Scoring y Gate por evidencia (WO-107, AD-CMP-05). Reemplaza al Gate por palabras clave (B5)."""
from app.scoring.engine import (
    CONTRADICTS, EXTERNAL, INFERENCE, TESTIMONY, EvidenceItem as E, evaluate_gate, responsible_score,
    score_dimension, venture_score,
)


def test_same_evidence_same_score():
    items = [E(EXTERNAL), E(TESTIMONY), E(INFERENCE, CONTRADICTS)]
    assert score_dimension("problem", items) == score_dimension("problem", items)


def test_without_evidence_the_score_is_declared_not_omitted():
    result = score_dimension("problem", [])
    assert (result.value, result.confidence) == (0.0, 0.0)
    assert "sin evidencia" in result.reasoning


def test_conversation_alone_is_never_enough():
    """Muchas inferencias de Agentes: la confianza no pasa de 40 % y el Gate no abre."""
    many = [E(INFERENCE)] * 50
    result = score_dimension("problem", many)
    assert result.confidence <= 40.0
    assert "no es evidencia suficiente" in result.reasoning
    assert not evaluate_gate(1, many).sufficient


def test_hierarchy_external_weighs_more_than_testimony_and_inference():
    external = score_dimension("problem", [E(EXTERNAL)] * 2)
    testimony = score_dimension("problem", [E(TESTIMONY)] * 2)
    inference = score_dimension("problem", [E(INFERENCE)] * 2)
    assert external.value > testimony.value > inference.value
    assert external.confidence > testimony.confidence > inference.confidence


def test_contradicting_evidence_lowers_the_score():
    base = score_dimension("problem", [E(EXTERNAL)] * 3)
    contradicted = score_dimension("problem", [E(EXTERNAL)] * 3 + [E(EXTERNAL, CONTRADICTS)] * 2)
    assert contradicted.value < base.value


def test_unclassified_claims_do_not_count():
    assert score_dimension("problem", [E("rumor")]).value == 0


def test_level_1_gate_requires_external_evidence():
    only_testimony = evaluate_gate(1, [E(TESTIMONY)] * 6)
    assert not only_testimony.sufficient
    assert any("dato verificable" in m for m in only_testimony.missing)

    enough = evaluate_gate(1, [E(EXTERNAL)] * 3 + [E(TESTIMONY)] * 2)
    assert enough.sufficient, enough.missing
    assert enough.missing == []


def test_gate_says_exactly_what_is_missing():
    evaluation = evaluate_gate(1, [E(EXTERNAL)])
    assert not evaluation.sufficient
    assert any("evidencias a favor" in m for m in evaluation.missing)
    assert any("Confianza" in m for m in evaluation.missing)


def test_responsible_score_grows_with_track_record():
    none = responsible_score(0, 0, 0, 0)
    some = responsible_score(4, 3, 1, 1)
    assert none.value == 0 and "todavía no hay decisiones" in none.reasoning
    assert some.value > 0 and some.confidence > 0


def test_venture_score_weights_by_confidence():
    result = venture_score({"problem": (80.0, 90.0), "solution": (20.0, 10.0)})
    assert 70 < result.value < 80  # domina el Score con más confianza
    assert venture_score({}).confidence == 0
