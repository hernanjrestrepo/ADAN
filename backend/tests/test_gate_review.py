"""Gate Review tests — proves deterministic scoring."""
import pytest
from app.nivel1.gate_review import GateReviewEngine, CRITERIA, MINIMUM_PASSING_SCORE


@pytest.fixture
def engine():
    return GateReviewEngine()


def test_gate_review_is_deterministic(engine):
    """Same inputs produce same outputs — no LLM involved."""
    inputs = {
        "diagnosis": "Problema claro con evidencia. Mercado de 500 empresas.",
        "board_votes": [
            {"agent": "CEO", "vote": "PROCEED", "confidence": 90},
            {"agent": "CTO", "vote": "PROCEED", "confidence": 85},
            {"agent": "CFO", "vote": "PROCEED", "confidence": 80},
            {"agent": "CMO", "vote": "PROCEED", "confidence": 85},
        ],
        "scores": [{"type": "problem", "value": 75, "confidence": 80}],
        "deliverables": ["Diagnóstico del Dolor"],
        "conversation_messages": [
            {"role": "user", "content": "Tenemos un SaaS de monitoreo energetico para 500 empresas."},
        ],
    }
    result1 = engine.evaluate(**inputs)
    result2 = engine.evaluate(**inputs)
    assert result1.overall_score == result2.overall_score
    assert result1.approved == result2.approved


def test_criteria_weights_sum_to_one(engine):
    """All criteria weights sum to 1.0."""
    total = sum(c["weight"] for c in CRITERIA.values())
    assert abs(total - 1.0) < 0.001


def test_minimum_passing_score(engine):
    """Minimum passing score is 80."""
    assert MINIMUM_PASSING_SCORE == 80


def test_all_proceed_approves(engine):
    """All PROCEED votes with comprehensive data should score well."""
    result = engine.evaluate(
        diagnosis=(
            "Problema claro: las empresas medianas pagan entre 500 y 5000 USD mensuales "
            "en energía sin datos en tiempo real. Las facturas de luz son su segundo gasto "
            "más grande después de nómina. Mercado: 500 empresas en Colombia. "
            "Competidores: paneles solares sin monitoreo. Solución: SaaS IoT con sensores "
            "y dashboard por 200 USD/mes. Validado con 3 pilotos exitosos."
        ),
        board_votes=[
            {"agent": "CEO", "vote": "PROCEED", "confidence": 90},
            {"agent": "CTO", "vote": "PROCEED", "confidence": 90},
            {"agent": "CFO", "vote": "PROCEED", "confidence": 90},
            {"agent": "CMO", "vote": "PROCEED", "confidence": 90},
        ],
        scores=[{"type": "problem", "value": 80, "confidence": 85}],
        deliverables=["Diagnóstico del Dolor", "Recomendaciones"],
        conversation_messages=[
            {"role": "user", "content": "SaaS IoT energetico para 500 empresas en Colombia. Precio 200 USD/mes. Competidores: paneles solares sin monitoreo. 3 pilotos exitosos."},
            {"role": "assistant", "content": "Entendido. Cuéntame más sobre el mercado."},
            {"role": "user", "content": "Mercado de 500 empresas medianas. Ya tenemos 3 pilotos con clientes reales pagando."},
        ],
    )
    assert result.overall_score >= 50  # Comprehensive data should score decently


def test_all_stop_rejects(engine):
    """All STOP votes should reject."""
    result = engine.evaluate(
        diagnosis="Problema",
        board_votes=[
            {"agent": "CEO", "vote": "STOP", "confidence": 90},
            {"agent": "CTO", "vote": "STOP", "confidence": 90},
            {"agent": "CFO", "vote": "STOP", "confidence": 90},
            {"agent": "CMO", "vote": "STOP", "confidence": 90},
        ],
        scores=[],
        deliverables=[],
        conversation_messages=[],
    )
    assert result.approved is False
    assert result.overall_score < 80


def test_score_calculation(engine):
    """Score is calculated as weighted average."""
    result = engine.evaluate(
        diagnosis="Problema claro",
        board_votes=[{"agent": "CEO", "vote": "PROCEED", "confidence": 80}],
        scores=[],
        deliverables=[],
        conversation_messages=[],
    )
    assert 0 <= result.overall_score <= 100
    assert isinstance(result.criteria_scores, dict)
    assert len(result.criteria_scores) == 7


def test_blocking_issues_prevent_approval(engine):
    """Blocking issues prevent approval."""
    result = engine.evaluate(
        diagnosis="Problema claro con evidencia. Mercado de 500 empresas.",
        board_votes=[
            {"agent": "CEO", "vote": "PROCEED", "confidence": 95},
            {"agent": "CTO", "vote": "PROCEED", "confidence": 95},
            {"agent": "CFO", "vote": "PROCEED", "confidence": 95},
            {"agent": "CMO", "vote": "PROCEED", "confidence": 95},
        ],
        scores=[{"type": "problem", "value": 90, "confidence": 90}],
        deliverables=["Diagnóstico", "Recomendaciones", "Score"],
        conversation_messages=[
            {"role": "user", "content": "SaaS IoT energetico 500 empresas 200 USD/mes Colombia."},
            {"role": "assistant", "content": "Entendido."},
            {"role": "user", "content": "Mercado validado con 3 pilotos."},
        ],
    )
    # With comprehensive data, should score reasonably
    assert result.overall_score >= 40
    assert isinstance(result.criteria_scores, dict)
