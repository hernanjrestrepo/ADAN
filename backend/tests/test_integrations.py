"""
Tests para Integration Hub — WO-010.
"""

import pytest
from unittest.mock import AsyncMock

from app.models.models import User, Company
from app.integrations.connectors import (
    ConnectorManager, BaseConnector, ConnectorMetadata, ConnectorResult,
    GmailConnector, OutlookConnector, GoogleCalendarConnector,
    SlackConnector, RESTAPIConnector,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def manager():
    mgr = ConnectorManager()
    mgr.register(GmailConnector())
    mgr.register(OutlookConnector())
    mgr.register(GoogleCalendarConnector())
    mgr.register(SlackConnector())
    mgr.register(RESTAPIConnector())
    return mgr


# ============================================================
# Tests: Connector Manager
# ============================================================

class TestConnectorManager:
    def test_register(self, manager):
        assert manager.count() == 5

    def test_list_all(self, manager):
        connectors = manager.list_all()
        assert len(connectors) == 5
        assert all(isinstance(c, ConnectorMetadata) for c in connectors)

    def test_get_connector(self, manager):
        connector = manager.get("gmail")
        assert connector is not None
        assert connector.metadata().id == "gmail"

    def test_get_nonexistent(self, manager):
        assert manager.get("nonexistent") is None


# ============================================================
# Tests: Gmail Connector
# ============================================================

class TestGmailConnector:
    @pytest.mark.asyncio
    async def test_connect(self):
        connector = GmailConnector()
        result = await connector.connect({})
        assert result is True

    @pytest.mark.asyncio
    async def test_disconnect(self):
        connector = GmailConnector()
        await connector.connect({})
        result = await connector.disconnect()
        assert result is True

    @pytest.mark.asyncio
    async def test_health(self):
        connector = GmailConnector()
        health = await connector.health()
        assert health["status"] == "disconnected"

        await connector.connect({})
        health = await connector.health()
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_send_email(self):
        connector = GmailConnector()
        await connector.connect({})
        result = await connector.execute("send_email", {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Hello",
        })
        assert result.status == "success"
        assert "message_id" in result.output

    def test_metadata(self):
        connector = GmailConnector()
        meta = connector.metadata()
        assert meta.id == "gmail"
        assert meta.category == "email"
        assert "send_email" in meta.capabilities


# ============================================================
# Tests: Slack Connector
# ============================================================

class TestSlackConnector:
    @pytest.mark.asyncio
    async def test_send_message(self):
        connector = SlackConnector()
        await connector.connect({})
        result = await connector.execute("send_message", {
            "channel": "#general",
            "text": "Hello from ADÁN",
        })
        assert result.status == "success"


# ============================================================
# Tests: REST API Connector
# ============================================================

class TestRESTAPIConnector:
    @pytest.mark.asyncio
    async def test_execute_get(self):
        connector = RESTAPIConnector()
        await connector.connect({"base_url": "https://httpbin.org"})
        result = await connector.execute("get", {
            "url": "https://httpbin.org/get",
            "method": "GET",
        })
        assert result.status == "success"
        assert result.output["status_code"] == 200

    @pytest.mark.asyncio
    async def test_execute_invalid_url(self):
        connector = RESTAPIConnector()
        await connector.connect({})
        result = await connector.execute("get", {
            "url": "https://invalid.domain.xyz",
        })
        assert result.status == "error"


# ============================================================
# Tests: Integration
# ============================================================

class TestIntegrationHub:
    @pytest.mark.asyncio
    async def test_full_flow(self, manager):
        """Test completo: connect → execute → health → disconnect."""
        # 1. Connect
        connected = await manager.connect("gmail", {"token": "test"})
        assert connected is True

        # 2. Health
        health = await manager.health("gmail")
        assert health["status"] == "healthy"

        # 3. Execute
        result = await manager.execute("gmail", "send_email", {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Hello",
        })
        assert result.status == "success"

        # 4. Disconnect
        disconnected = await manager.disconnect("gmail")
        assert disconnected is True

        # 5. Health after disconnect
        health = await manager.health("gmail")
        assert health["status"] == "disconnected"

    @pytest.mark.asyncio
    async def test_nonexistent_connector(self, manager):
        result = await manager.execute("nonexistent", "test", {})
        assert result.status == "error"
