"""
Tests para el Sistema Cognitivo de ADÁN — WO-003.

Verifica el vertical slice completo:
Event Bus → Memory → Knowledge → Planner → Tools → Board Room → Decision Engine
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.models import User, Company, Project, Level, Card, Conversation, Message
from app.cognitive.event_bus import EventBus, CognitiveEvent, create_trace_id
from app.cognitive.memory_engine import MemoryEngine, WorkingMemory, ShortTermMemory, LongTermMemory
from app.cognitive.knowledge_engine import KnowledgeEngine, KnowledgeContext
from app.cognitive.planner import Planner, Plan
from app.cognitive.tool_manager import ToolManager, ToolDef, ToolResult
from app.cognitive.decision_engine import DecisionEngine


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from app.core.auth import hash_password
    user = User(
        email="test@cognitive.com",
        name="Test User",
        hashed_password=hash_password("test123"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_company(db_session, test_user):
    """Create a test company with full setup."""
    company = Company(
        name="Cognitive Test Corp",
        description="Empresa de prueba para cognitivo",
        industry="technology",
        country="Argentina",
        maturity=0.3,
        primary_user_id=test_user.id,
        created_by=test_user.id,
    )
    db_session.add(company)
    db_session.commit()

    project = Project(company_id=company.id, name="Cognitive Test Project")
    db_session.add(project)
    db_session.commit()

    level = Level(
        project_id=project.id,
        number=1,
        name="El Dolor",
        status="active",
    )
    db_session.add(level)
    db_session.commit()

    card = Card(
        project_id=project.id,
        level_id=level.id,
        title="Pain Discovery",
        description="Descubrir el dolor principal",
        card_type="pain_discovery",
        status="active",
    )
    db_session.add(card)
    db_session.commit()

    conversation = Conversation(
        card_id=card.id,
        title="Test Conversation",
    )
    db_session.add(conversation)
    db_session.commit()

    return company, project, level, card, conversation


# ============================================================
# Tests: Event Bus (unit tests — no DB persistence)
# ============================================================

class TestEventBus:
    def test_create_trace_id(self):
        trace_id = create_trace_id()
        assert trace_id.startswith("trace-")
        assert len(trace_id) == 18

    def test_event_creation(self):
        event = CognitiveEvent(
            type="test_event",
            source="test",
            trace_id="trace-test123",
            payload={"key": "value"},
        )
        assert event.type == "test_event"
        assert event.trace_id == "trace-test123"
        assert event.payload == {"key": "value"}

    def test_event_bus_metrics(self):
        bus = EventBus.__new__(EventBus)
        bus._subscribers = {}
        bus._metrics = {}
        bus.db = None

        # Publish without persistence (for unit test)
        event = CognitiveEvent(type="test_event", source="test", trace_id="trace-123")
        bus._metrics[f"events_{event.type}"] = bus._metrics.get(f"events_{event.type}", 0) + 1
        assert bus._metrics.get("events_test_event") == 1

    def test_subscribe_and_route(self):
        bus = EventBus.__new__(EventBus)
        bus._subscribers = {}
        bus._metrics = {}
        bus.db = None

        received = []
        bus.subscribe("test_event", lambda e: received.append(e))

        event = CognitiveEvent(type="test_event", source="test", trace_id="trace-123")
        bus._route(event)

        assert len(received) == 1
        assert received[0].type == "test_event"


# ============================================================
# Tests: Memory Engine
# ============================================================

class TestMemoryEngine:
    def test_working_memory_creation(self):
        wm = WorkingMemory(conversation_id="test-conv")
        assert wm.conversation_id == "test-conv"
        assert wm.messages == []
        assert wm.turn_count == 0

    def test_working_memory_update(self):
        wm = WorkingMemory(conversation_id="test-conv")
        wm.messages.append({"role": "user", "content": "Hola", "agent_name": None, "timestamp": "2026-01-01"})
        wm.turn_count += 1
        assert len(wm.messages) == 1
        assert wm.messages[0]["role"] == "user"
        assert wm.turn_count == 1

    def test_short_term_memory_creation(self):
        stm = ShortTermMemory(session_id="s1", user_id="u1", company_id="c1")
        assert stm.session_id == "s1"
        assert stm.turns == []

    def test_long_term_memory_creation(self):
        ltm = LongTermMemory(company_id="c1")
        assert ltm.company_id == "c1"
        assert ltm.lessons == []

    def test_memory_engine_loads_working_memory(self, db_session, test_company):
        company, project, level, card, conversation = test_company
        engine = MemoryEngine(db_session)
        wm = engine.get_working_memory(str(conversation.id))
        assert wm.conversation_id == str(conversation.id)

    def test_memory_engine_empty_conversation(self):
        engine = MemoryEngine(MagicMock())
        wm = engine.get_working_memory("nonexistent-id")
        assert wm.conversation_id == "nonexistent-id"
        assert wm.messages == []


# ============================================================
# Tests: Knowledge Engine
# ============================================================

class TestKnowledgeEngine:
    def test_knowledge_context_creation(self):
        ctx = KnowledgeContext()
        assert ctx.company_info == {}
        assert ctx.units == []

    def test_knowledge_engine_loads_company(self, db_session, test_company):
        company, _, _, _, _ = test_company
        engine = KnowledgeEngine(db_session)
        ctx = engine.get_knowledge_context(str(company.id))
        assert ctx.company_info["name"] == "Cognitive Test Corp"
        assert ctx.company_info["industry"] == "technology"
        assert len(ctx.units) > 0

    def test_knowledge_engine_loads_level(self, db_session, test_company):
        company, _, _, _, _ = test_company
        engine = KnowledgeEngine(db_session)
        ctx = engine.get_knowledge_context(str(company.id))
        assert ctx.current_level["name"] == "El Dolor"

    def test_knowledge_prompt_building(self, db_session, test_company):
        company, _, _, _, _ = test_company
        engine = KnowledgeEngine(db_session)
        ctx = engine.get_knowledge_context(str(company.id))
        prompt = engine.build_knowledge_prompt(ctx)
        assert "Cognitive Test Corp" in prompt
        assert "technology" in prompt

    def test_knowledge_empty_company(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        engine = KnowledgeEngine(mock_db)
        ctx = engine.get_knowledge_context("nonexistent")
        assert ctx.company_info == {}


# ============================================================
# Tests: Planner
# ============================================================

class TestPlanner:
    def test_simple_query_detection(self):
        planner = Planner(MagicMock())
        assert planner._is_simple_query("Qué sabes de mi empresa?")
        assert planner._is_simple_query("Cuéntame el estado")
        assert not planner._is_simple_query("Analiza los tres problemas más importantes")

    def test_simple_plan_creation(self):
        planner = Planner(MagicMock())
        plan = planner._create_simple_plan("Qué sabes de mi empresa?")
        assert len(plan.steps) == 2
        assert plan.steps[0].component == "knowledge_engine"
        assert plan.steps[1].component == "llm"

    def test_analysis_plan_creation(self):
        planner = Planner(MagicMock())
        plan = planner._create_analysis_plan("Analiza mi empresa")
        assert len(plan.steps) == 3
        assert plan.steps[0].component == "knowledge_engine"
        assert plan.steps[1].component == "board_room"
        assert plan.steps[2].component == "llm"

    def test_plan_json_parsing(self):
        planner = Planner(MagicMock())
        json_str = '{"goal": "test", "steps": [{"order": 1, "description": "step1", "component": "llm"}], "reasoning": "test"}'
        result = planner._parse_plan_response(json_str)
        assert result["goal"] == "test"
        assert len(result["steps"]) == 1

    def test_plan_json_with_code_fences(self):
        planner = Planner(MagicMock())
        json_str = '```json\n{"goal": "test", "steps": [], "reasoning": "test"}\n```'
        result = planner._parse_plan_response(json_str)
        assert result["goal"] == "test"

    def test_plan_json_invalid_fallback(self):
        planner = Planner(MagicMock())
        result = planner._parse_plan_response("not json at all")
        assert "goal" in result
        assert "steps" in result


# ============================================================
# Tests: Tool Manager
# ============================================================

class TestToolManager:
    def test_register_tool(self):
        tm = ToolManager()
        tool = ToolDef(
            id="test_tool",
            name="Test Tool",
            description="A test tool",
            category="test",
            tags=["test", "example"],
            handler=AsyncMock(return_value="result"),
        )
        tm.register(tool)
        assert tm.get("test_tool") is not None
        assert len(tm.list_all()) == 1

    def test_discover_tools(self):
        tm = ToolManager()
        tm.register(ToolDef(
            id="web_search",
            name="Búsqueda Web",
            description="Busca en internet",
            category="search",
            tags=["web", "search", "internet"],
            handler=AsyncMock(),
        ))
        tm.register(ToolDef(
            id="calculator",
            name="Calculadora",
            description="Calcula operaciones",
            category="computation",
            tags=["math", "calculate"],
            handler=AsyncMock(),
        ))

        results = tm.discover("necesito buscar en internet")
        assert len(results) > 0
        assert results[0].id == "web_search"

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        tm = ToolManager()
        tm.register(ToolDef(
            id="echo",
            name="Echo",
            description="Echo tool",
            category="test",
            tags=["echo"],
            handler=AsyncMock(return_value="hello"),
        ))

        result = await tm.execute("echo")
        assert result.status == "success"
        assert result.output == "hello"

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self):
        tm = ToolManager()
        result = await tm.execute("nonexistent")
        assert result.status == "failed"
        assert "no encontrada" in result.error

    @pytest.mark.asyncio
    async def test_execute_tool_exception(self):
        tm = ToolManager()
        tm.register(ToolDef(
            id="fail_tool",
            name="Fail",
            description="Always fails",
            category="test",
            tags=["fail"],
            handler=AsyncMock(side_effect=ValueError("boom")),
        ))

        result = await tm.execute("fail_tool")
        assert result.status == "failed"
        assert "boom" in result.error


# ============================================================
# Tests: Decision Engine
# ============================================================

class TestDecisionEngine:
    def test_evaluate_response(self):
        de = DecisionEngine()
        response, justification = de.evaluate_response(
            response="Los tres problemas principales son: 1) Falta de mercado, 2) Costos altos, 3) Competencia fuerte",
            user_message="Cuáles son los tres problemas más importantes",
            knowledge_context="Empresa: TechCorp, industria: technology",
        )
        assert response is not None
        assert justification is not None
        assert 0 <= justification.confidence <= 1
        assert justification.decision == "Entregar respuesta generada"

    def test_quality_assessment(self):
        de = DecisionEngine()
        quality = de._assess_quality(
            response="El problema principal es la falta de mercado",
            user_message="Analiza los problemas de mi empresa",
            knowledge_context="Empresa: TechCorp",
        )
        assert quality.overall_score > 0
        assert "completeness" in quality.dimensions
        assert "relevance" in quality.dimensions
        assert "clarity" in quality.dimensions

    def test_completeness_assessment(self):
        de = DecisionEngine()
        # High completeness - response contains user's words
        score = de._assess_completeness(
            response="Los problemas de mi empresa son many things",
            user_message="problemas de mi empresa"
        )
        assert score > 0.5

    def test_clarity_assessment(self):
        de = DecisionEngine()
        # Clear response with lists
        score = de._assess_clarity(
            response="Los puntos son:\n- Punto 1\n- Punto 2\n- Punto 3"
        )
        assert score > 0.8

    def test_justification_has_supporting_facts(self):
        de = DecisionEngine()
        _, justification = de.evaluate_response(
            response="Análisis completo",
            user_message="Analiza mi empresa",
            knowledge_context="Empresa: TechCorp, industria: technology, país: Argentina",
        )
        assert len(justification.supporting_facts) > 0

    def test_justification_has_alternatives(self):
        de = DecisionEngine()
        _, justification = de.evaluate_response(
            response="Respuesta",
            user_message="Pregunta",
            knowledge_context="Contexto",
        )
        assert len(justification.alternatives) > 0


# ============================================================
# Tests: Integración (requiere mock de LLM)
# ============================================================

class TestCognitiveIntegration:
    @pytest.mark.asyncio
    async def test_orchestrator_flow(self, db_session, test_company):
        """Test del flujo completo del orquestador cognitivo."""
        company, project, level, card, conversation = test_company

        # Mock del LLM
        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value=MagicMock(
            content="Los tres problemas principales son:\n1. Falta de validación de mercado\n2. Modelo de negocio no definido\n3. Equipo incompleto",
            model="qwen2.5:0.5b",
            prompt_tokens=100,
            completion_tokens=50,
            duration_s=2.0,
            done=True,
            metadata={},
        ))

        from app.cognitive.orchestrator import CognitiveOrchestrator
        orchestrator = CognitiveOrchestrator(llm=mock_llm, db=db_session)

        result = await orchestrator.process(
            user_message="Analiza mi empresa y dime cuáles son los tres problemas más importantes",
            company_id=str(company.id),
            user_id=str(company.primary_user_id),
        )

        assert result.response is not None
        assert result.trace_id.startswith("trace-")
        assert result.duration_ms > 0
        assert len(result.components_used) > 0
        assert result.justification is not None
        assert result.justification.confidence > 0

    @pytest.mark.asyncio
    async def test_orchestrator_returns_plan(self, db_session, test_company):
        """Verifica que el orquestador retorna un plan."""
        company, _, _, _, _ = test_company

        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value=MagicMock(
            content="Respuesta de prueba",
            model="test",
            prompt_tokens=10,
            completion_tokens=10,
            duration_s=0.5,
            done=True,
            metadata={},
        ))

        from app.cognitive.orchestrator import CognitiveOrchestrator
        orchestrator = CognitiveOrchestrator(llm=mock_llm, db=db_session)

        result = await orchestrator.process(
            user_message="Test simple",
            company_id=str(company.id),
            user_id=str(company.primary_user_id),
        )

        assert result.plan is not None
        assert len(result.plan.steps) > 0

    @pytest.mark.asyncio
    async def test_orchestrator_persists_messages(self, db_session, test_company):
        """Verifica que el orquestador persiste mensajes."""
        company, _, _, _, _ = test_company

        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value=MagicMock(
            content="Respuesta persistida",
            model="test",
            prompt_tokens=10,
            completion_tokens=10,
            duration_s=0.5,
            done=True,
            metadata={},
        ))

        from app.cognitive.orchestrator import CognitiveOrchestrator
        orchestrator = CognitiveOrchestrator(llm=mock_llm, db=db_session)

        await orchestrator.process(
            user_message="Mensaje de prueba",
            company_id=str(company.id),
            user_id=str(company.primary_user_id),
        )

        # Verificar que se guardaron mensajes
        messages = db_session.query(Message).all()
        assert len(messages) >= 2  # user + assistant

    @pytest.mark.asyncio
    async def test_orchestrator_metrics(self, db_session, test_company):
        """Verifica que el orquestador retorna métricas."""
        company, _, _, _, _ = test_company

        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value=MagicMock(
            content="Respuesta",
            model="test",
            prompt_tokens=10,
            completion_tokens=10,
            duration_s=0.5,
            done=True,
            metadata={},
        ))

        from app.cognitive.orchestrator import CognitiveOrchestrator
        orchestrator = CognitiveOrchestrator(llm=mock_llm, db=db_session)

        result = await orchestrator.process(
            user_message="Test",
            company_id=str(company.id),
            user_id=str(company.primary_user_id),
        )

        assert "working_memory_size" in result.metrics
        assert "knowledge_units" in result.metrics
        assert "plan_steps" in result.metrics
        assert "quality_score" in result.metrics
