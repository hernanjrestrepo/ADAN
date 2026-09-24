"""
Tests consolidados para WO-011 a WO-020.
"""

import pytest
from datetime import datetime, timezone

# WO-011: Voice
from app.voice.adapter import ClaroVoiceAdapter, VoiceResult
from app.voice.tools import STTTool, TTSTool

# WO-012: Omnichannel
from app.omnichannel.channels import (
    ChannelManager, WebChatChannel, WhatsAppChannel,
    TelegramChannel, EmailChannel, ChannelMessage,
)

# WO-016: Knowledge Quality
from app.quality.engine import KnowledgeQualityEngine, KnowledgeQualityReport

# WO-017: Learning
from app.learning.engine import LearningEngine, LearningRecord

# WO-018: Agent Factory
from app.agent_factory.factory import AgentFactory, AgentConfig, ConfigurableAgent
from unittest.mock import AsyncMock, MagicMock

# WO-019: Plugin Marketplace
from app.plugins.marketplace import PluginMarketplace, PluginManifest

# WO-020: Autonomous Organization
from app.autonomous.engine import AutonomousEngine, AutonomousCycle


# ============================================================
# WO-011: Voice Tests
# ============================================================

class TestVoice:
    @pytest.mark.asyncio
    async def test_stt(self):
        adapter = ClaroVoiceAdapter()
        result = await adapter.stt(b"audio_data")
        assert result.status == "success"
        assert "text" in result.output

    @pytest.mark.asyncio
    async def test_tts(self):
        adapter = ClaroVoiceAdapter()
        result = await adapter.tts("Hola mundo")
        assert result.status == "success"
        assert "audio_url" in result.output

    @pytest.mark.asyncio
    async def test_health(self):
        adapter = ClaroVoiceAdapter()
        health = await adapter.health()
        assert health["status"] == "healthy"


# ============================================================
# WO-012: Omnichannel Tests
# ============================================================

class TestOmnichannel:
    def test_channel_manager(self):
        mgr = ChannelManager()
        mgr.register(WebChatChannel())
        mgr.register(WhatsAppChannel())
        assert len(mgr.list_channels()) == 2

    @pytest.mark.asyncio
    async def test_receive_web(self):
        mgr = ChannelManager()
        mgr.register(WebChatChannel())
        msg = await mgr.receive("web", {"user_id": "u1", "message": "Hola"})
        assert msg.channel == "web"
        assert msg.content == "Hola"

    @pytest.mark.asyncio
    async def test_respond(self):
        mgr = ChannelManager()
        mgr.register(WebChatChannel())
        from app.omnichannel.channels import ChannelResponse
        result = await mgr.respond("web", ChannelResponse(
            channel="web", recipient_id="u1", content="Respuesta"
        ))
        assert result is True


# ============================================================
# WO-016: Knowledge Quality Tests
# ============================================================

class TestKnowledgeQuality:
    def test_evaluate_good_content(self):
        engine = KnowledgeQualityEngine()
        report = engine.evaluate(
            content="Empresa de tecnología SaaS con 50 clientes en LATAM. Facturación anual de $120K.",
            source_url="https://example.com",
        )
        assert report.overall_score > 40
        assert report.passed is True

    def test_evaluate_bad_content(self):
        engine = KnowledgeQualityEngine()
        report = engine.evaluate(
            content="X",
            source_url="",
        )
        assert report.overall_score < 50

    def test_dimensions(self):
        engine = KnowledgeQualityEngine()
        report = engine.evaluate(content="Test content here")
        assert len(report.dimensions) == 6
        total_weight = sum(d.weight for d in report.dimensions)
        assert abs(total_weight - 1.0) < 0.01


# ============================================================
# WO-017: Learning Tests
# ============================================================

class TestLearning:
    def test_record_decision(self):
        engine = LearningEngine()
        record = engine.record_decision(
            context="Expandir mercado",
            decision="PROCEED",
            outcome="success",
            quality_score=0.85,
            lesson="Mercado favorable",
        )
        assert record.id is not None
        assert record.outcome == "success"

    def test_patterns(self):
        engine = LearningEngine()
        engine.record_decision("ctx1", "d1", "success", 0.9)
        engine.record_decision("ctx1", "d2", "failure", 0.4)
        engine.record_decision("ctx2", "d3", "success", 0.8)

        patterns = engine.get_patterns()
        assert patterns["total"] == 3
        assert patterns["success_rate"] > 0

    def test_recommendations(self):
        engine = LearningEngine()
        engine.record_decision("ctx", "d", "failure", 0.3, lesson="No hacer X")
        recs = engine.get_recommendations()
        assert len(recs) > 0


# ============================================================
# WO-018: Agent Factory Tests
# ============================================================

class TestAgentFactory:
    def test_create_agent(self):
        llm = AsyncMock()
        llm.chat = AsyncMock(return_value=MagicMock(content="Respuesta", model="test", prompt_tokens=10, completion_tokens=10, duration_s=0.1))
        ems = AsyncMock()
        ems.retrieve_for_llm = AsyncMock(return_value="Contexto")
        executor = MagicMock()

        factory = AgentFactory(llm, ems, executor)
        agent = factory.create(AgentConfig(
            name="Finance Director",
            role="CFO",
            personality="Analítico",
            system_prompt="Eres el CFO",
            tools=["sql_query"],
            goals=["Optimizar costos"],
        ))

        assert agent.config.name == "Finance Director"
        assert len(factory.list_all()) == 1

    @pytest.mark.asyncio
    async def test_agent_process(self):
        llm = AsyncMock()
        llm.chat = AsyncMock(return_value=MagicMock(content='{"analysis": "test", "vote": "PROCEED", "confidence": 0.8}', model="test", prompt_tokens=10, completion_tokens=10, duration_s=0.1))
        ems = AsyncMock()
        ems.retrieve_for_llm = AsyncMock(return_value="Contexto")
        executor = MagicMock()

        factory = AgentFactory(llm, ems, executor)
        agent = factory.create(AgentConfig(
            name="Test Agent",
            role="Tester",
            personality="Test",
            system_prompt="Eres un tester",
        ))

        result = await agent.process("Test", "company-1", "user-1")
        assert result.response is not None
        assert result.agent == "test_agent"


# ============================================================
# WO-019: Plugin Marketplace Tests
# ============================================================

class TestPluginMarketplace:
    def test_register_plugin(self):
        mp = PluginMarketplace()
        mp.register_plugin(PluginManifest(
            id="crm-plugin",
            name="CRM Plugin",
            description="Integración con CRM",
            version="1.0.0",
            author="Paradixe",
            category="crm",
        ))
        assert len(mp.list_available()) == 1

    def test_install_plugin(self):
        mp = PluginMarketplace()
        mp.register_plugin(PluginManifest(
            id="crm-plugin", name="CRM", description="CRM",
            version="1.0.0", author="Paradixe", category="crm",
        ))
        plugin = mp.install("crm-plugin")
        assert plugin.manifest.id == "crm-plugin"
        assert plugin.status == "active"

    def test_uninstall_plugin(self):
        mp = PluginMarketplace()
        mp.register_plugin(PluginManifest(
            id="crm-plugin", name="CRM", description="CRM",
            version="1.0.0", author="Paradixe", category="crm",
        ))
        mp.install("crm-plugin")
        assert mp.uninstall("crm-plugin") is True
        assert len(mp.list_installed()) == 0

    def test_count(self):
        mp = PluginMarketplace()
        mp.register_plugin(PluginManifest(
            id="p1", name="P1", description="P1", version="1.0.0",
            author="A", category="c",
        ))
        mp.install("p1")
        count = mp.count()
        assert count["available"] == 1
        assert count["installed"] == 1


# ============================================================
# WO-020: Autonomous Organization Tests
# ============================================================

class TestAutonomousOrganization:
    def test_start_cycle(self):
        engine = AutonomousEngine()
        cycle = engine.start_cycle("org-1")
        assert cycle.id is not None
        assert cycle.status == "running"

    def test_complete_cycle(self):
        engine = AutonomousEngine()
        cycle = engine.start_cycle("org-1")
        completed = engine.complete_cycle(cycle.id)
        assert completed.status == "completed"
        assert completed.completed_at is not None

    def test_get_status(self):
        engine = AutonomousEngine()
        engine.start_cycle("org-1")
        engine.start_cycle("org-1")
        status = engine.get_status("org-1")
        assert status["total_cycles"] == 2
        assert status["active_cycles"] == 2
