"""
Tests para el CEO Agent — WO-006 (rebuild con razonamiento ejecutivo).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.models import User, Company, Project, Level
from app.ems.models import EMSBase
from app.agents.base import ExecutiveAgent, AgentMessage, AgentPlan, AgentResponse
from app.agents.ceo import CEOAgent, CEO_SYSTEM_PROMPT, ExecutiveReasoning, ExecutiveStep
from app.tef.interfaces import ToolContext, ToolResult
from app.tef.registry import ToolRegistry
from app.tef.executor import ToolExecutor
from app.tef.tools import CalculatorTool


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    EMSBase.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()


@pytest.fixture
def test_company(db_session):
    from app.core.auth import hash_password
    user = User(
        email="ceo@test.com",
        name="CEO Tester",
        hashed_password=hash_password("test123"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    company = Company(
        name="Paradixe",
        description="Empresa de tecnología SaaS",
        industry="technology",
        country="Argentina",
        maturity=0.5,
        primary_user_id=user.id,
        created_by=user.id,
    )
    db_session.add(company)
    db_session.commit()

    return company, user


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.chat = AsyncMock(return_value=MagicMock(
        content='{"objective": "Aumentar ventas", "sub_objectives": ["Identificar canales"], "available_information": ["Empresa tech"], "information_gaps": [], "needs_more_info": false, "missing_summary": "", "analysis": "La empresa tiene potencial de crecimiento", "priorities": [{"priority": 1, "action": "Implementar estrategia de content marketing", "owner": "CMO", "deadline": "Q1 2027", "reasoning": "Canal de bajo costo y alto ROI", "urgency": "high", "impact": "high", "kpis": ["Leads mensuales", "Tasa de conversión"]}], "risks": [{"risk": "Competencia creciente", "probability": "medium", "impact": "high", "mitigation": "Diferenciación por IA", "owner": "CEO"}], "dependencies": [{"dependency": "Presupuesto marketing", "from": "CFO", "status": "pending"}], "kpis": [{"name": "MRR", "current": "$10K", "target": "$50K", "unit": "USD"}], "follow_up": [{"action": "Revisar métricas", "when": "Semanal", "responsible": "CEO"}], "confidence": 0.75, "summary": "Plan para aumentar ventas con content marketing"}',
        model="test",
        prompt_tokens=100,
        completion_tokens=50,
        duration_s=1.0,
    ))
    return llm


@pytest.fixture
def mock_ems():
    ems = AsyncMock()
    ems.retrieve_for_llm = AsyncMock(return_value="Empresa: Paradixe, industria: technology, país: Argentina, ARR: $120K")
    return ems


@pytest.fixture
def tool_executor():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    return ToolExecutor(registry)


@pytest.fixture
def ceo_agent(mock_llm, mock_ems, tool_executor):
    return CEOAgent(mock_llm, mock_ems, tool_executor)


@pytest.fixture
def context(test_company):
    company, user = test_company
    return {
        "company_id": str(company.id),
        "user_id": str(user.id),
    }


# ============================================================
# Tests: Executive Reasoning
# ============================================================

class TestExecutiveReasoning:
    def test_reasoning_creation(self):
        r = ExecutiveReasoning(objective="Test objective")
        assert r.objective == "Test objective"
        assert r.needs_more_info is False
        assert len(r.steps) == 0

    def test_step_creation(self):
        step = ExecutiveStep(step_type="interpret", description="Interpretando")
        assert step.step_type == "interpret"
        assert step.status == "pending"


# ============================================================
# Tests: CEO Agent
# ============================================================

class TestCEOAgent:
    def test_system_prompt(self, ceo_agent):
        prompt = ceo_agent.system_prompt()
        assert "CEO" in prompt
        assert "needs_more_info" in prompt
        assert "JSON" in prompt

    @pytest.mark.asyncio
    async def test_process_basic(self, ceo_agent, context):
        result = await ceo_agent.process(
            message="Analiza mi empresa",
            company_id=context["company_id"],
            user_id=context["user_id"],
        )

        assert result.agent == "ceo"
        assert result.response is not None
        assert len(result.response) > 0
        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_process_with_memory(self, ceo_agent, context):
        result = await ceo_agent.process(
            message="¿Qué sabes de mi empresa?",
            company_id=context["company_id"],
            user_id=context["user_id"],
        )

        assert result.memory_context is not None
        assert "Paradixe" in result.memory_context

    @pytest.mark.asyncio
    async def test_process_returns_structured_plan(self, ceo_agent, context):
        result = await ceo_agent.process(
            message="¿Qué debo hacer esta semana para aumentar las ventas?",
            company_id=context["company_id"],
            user_id=context["user_id"],
        )

        assert result.response is not None
        assert result.confidence > 0
        # La respuesta debería contener elementos estructurados
        assert "priorities" in result.response or "action" in result.response.lower()

    @pytest.mark.asyncio
    async def test_process_with_information_gaps(self, mock_ems, tool_executor):
        """Test cuando el CEO detecta gaps de información."""
        # LLM que retorna needs_more_info: true
        gap_llm = AsyncMock()
        gap_llm.chat = AsyncMock(return_value=MagicMock(
            content='{"objective": "Analizar ventas", "available_information": [], "information_gaps": ["Datos de ventas Q4"], "needs_more_info": true, "missing_summary": "Necesito datos de ventas del Q4 para analizar tendencias", "analysis": "No tengo suficiente información", "priorities": [], "risks": [], "dependencies": [], "kpis": [], "follow_up": [], "confidence": 0.3, "summary": "Necesito más datos"}',
            model="test",
            prompt_tokens=50,
            completion_tokens=30,
            duration_s=0.5,
        ))

        ceo = CEOAgent(gap_llm, mock_ems, tool_executor)
        result = await ceo.process(
            message="¿Cómo van las ventas este trimestre?",
            company_id="test",
            user_id="test",
        )

        assert result.response is not None
        # El CEO debería indicar que necesita más información
        assert "needs_more_info" in result.response or "missing" in result.response.lower()

    @pytest.mark.asyncio
    async def test_process_failure_handling(self, mock_ems, tool_executor):
        failing_llm = AsyncMock()
        failing_llm.chat = AsyncMock(side_effect=Exception("LLM failed"))

        ceo = CEOAgent(failing_llm, mock_ems, tool_executor)

        with pytest.raises(Exception):
            await ceo.process(
                message="Test",
                company_id="test",
                user_id="test",
            )

    def test_parse_json_response(self, ceo_agent):
        # JSON válido
        result = ceo_agent._parse_json_response('{"key": "value"}', {})
        assert result == {"key": "value"}

        # JSON con code fences
        result = ceo_agent._parse_json_response('```json\n{"key": "value"}\n```', {})
        assert result == {"key": "value"}

        # JSON inválido → default
        result = ceo_agent._parse_json_response("not json", {"default": True})
        assert result == {"default": True}

    def test_build_executive_context(self, ceo_agent):
        reasoning = ExecutiveReasoning(
            objective="Aumentar ventas",
            available_information=["Empresa tech", "ARR $120K"],
            information_gaps=["Datos de competidores"],
            needs_more_info=False,
            memory_context="Paradixe es una empresa de tecnología",
        )
        reasoning.tool_results = [{"tool_id": "sql_query", "status": "success", "output": {"count": 42}}]

        context = ceo_agent._build_executive_context(reasoning)
        assert "Aumentar ventas" in context
        assert "Empresa tech" in context
        assert "Competidores" in context or "competidores" in context.lower()
        assert "Paradixe" in context
        assert "sql_query" in context


# ============================================================
# Tests: Integration
# ============================================================

class TestCEOIntegration:
    @pytest.mark.asyncio
    async def test_full_flow(self, ceo_agent, context):
        """Test completo del CEO Agent con razonamiento ejecutivo."""
        result = await ceo_agent.process(
            message="Analiza Paradixe y dime qué debo hacer esta semana para aumentar las ventas",
            company_id=context["company_id"],
            user_id=context["user_id"],
        )

        # Verificar components
        assert result.agent == "ceo"
        assert result.response is not None
        assert result.confidence > 0

        # Verificar que recuperó memoria
        assert result.memory_context is not None
        assert "Paradixe" in result.memory_context

        # Verificar que la respuesta tiene estructura
        assert len(result.response) > 100  # Respuesta sustancial

    @pytest.mark.asyncio
    async def test_multiple_queries(self, ceo_agent, context):
        """Test de múltiples consultas."""
        queries = [
            "¿Qué sabes de mi empresa?",
            "¿Cuáles son mis prioridades?",
            "¿Qué riesgos tengo?",
            "¿Qué debo hacer esta semana?",
        ]

        for query in queries:
            result = await ceo_agent.process(
                message=query,
                company_id=context["company_id"],
                user_id=context["user_id"],
            )
            assert result.response is not None
            assert result.agent == "ceo"
