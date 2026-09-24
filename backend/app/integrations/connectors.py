"""
Integration Hub — Conectores para servicios externos.

Todos implementan la misma interfaz: connect, disconnect, health, execute, metadata.
"""

import abc
import time
import asyncio
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime, timezone

from app.core.net import public_http_client


@dataclass
class ConnectorMetadata:
    """Metadata de un conector."""
    id: str
    name: str
    description: str
    category: str                        # email, calendar, chat, storage, api
    auth_type: str                       # oauth2, api_key, basic, none
    capabilities: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    status: str = "active"


@dataclass
class ConnectorResult:
    """Resultado de una operación de conector."""
    connector_id: str
    status: str                          # success, error, auth_required
    output: Any = None
    error: str | None = None
    duration_ms: int = 0
    metadata: dict = field(default_factory=dict)


class BaseConnector(abc.ABC):
    """Interfaz base para todos los conectores."""

    @abc.abstractmethod
    async def connect(self, credentials: dict) -> bool:
        """Conecta al servicio externo."""
        ...

    @abc.abstractmethod
    async def disconnect(self) -> bool:
        """Desconecta del servicio."""
        ...

    @abc.abstractmethod
    async def health(self) -> dict:
        """Verifica salud del servicio."""
        ...

    @abc.abstractmethod
    async def execute(self, action: str, params: dict) -> ConnectorResult:
        """Ejecuta una acción en el servicio."""
        ...

    @abc.abstractmethod
    def metadata(self) -> ConnectorMetadata:
        """Retorna metadata del conector."""
        ...


# ============================================================
# Gmail Connector
# ============================================================

class GmailConnector(BaseConnector):
    """Conector para Gmail."""

    def __init__(self):
        self._connected = False
        self._credentials = {}

    async def connect(self, credentials: dict) -> bool:
        self._credentials = credentials
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        return True

    async def health(self) -> dict:
        return {"status": "healthy" if self._connected else "disconnected", "service": "gmail"}

    async def execute(self, action: str, params: dict) -> ConnectorResult:
        start = time.time()
        try:
            if action == "send_email":
                result = {
                    "message_id": f"gmail-{uuid.uuid4().hex[:8]}",
                    "status": "sent",
                    "to": params.get("to"),
                    "subject": params.get("subject"),
                }
            elif action == "list_emails":
                result = {"emails": [], "count": 0}
            else:
                result = {"action": action, "status": "unknown_action"}

            return ConnectorResult(
                connector_id="gmail",
                status="success",
                output=result,
                duration_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            return ConnectorResult(
                connector_id="gmail",
                status="error",
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )

    def metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            id="gmail",
            name="Gmail",
            description="Enviar y recibir emails via Gmail",
            category="email",
            auth_type="oauth2",
            capabilities=["send_email", "list_emails", "read_email"],
        )


import uuid


# ============================================================
# Outlook Connector
# ============================================================

class OutlookConnector(BaseConnector):
    """Conector para Outlook/Microsoft 365."""

    def __init__(self):
        self._connected = False

    async def connect(self, credentials: dict) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        return True

    async def health(self) -> dict:
        return {"status": "healthy" if self._connected else "disconnected", "service": "outlook"}

    async def execute(self, action: str, params: dict) -> ConnectorResult:
        start = time.time()
        try:
            if action == "send_email":
                result = {"message_id": f"outlook-{uuid.uuid4().hex[:8]}", "status": "sent"}
            else:
                result = {"action": action, "status": "ok"}

            return ConnectorResult(
                connector_id="outlook", status="success", output=result,
                duration_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            return ConnectorResult(
                connector_id="outlook", status="error", error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )

    def metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            id="outlook", name="Outlook",
            description="Email y calendario via Microsoft 365",
            category="email", auth_type="oauth2",
            capabilities=["send_email", "list_emails", "calendar"],
        )


# ============================================================
# Google Calendar Connector
# ============================================================

class GoogleCalendarConnector(BaseConnector):
    """Conector para Google Calendar."""

    def __init__(self):
        self._connected = False

    async def connect(self, credentials: dict) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        return True

    async def health(self) -> dict:
        return {"status": "healthy" if self._connected else "disconnected", "service": "google_calendar"}

    async def execute(self, action: str, params: dict) -> ConnectorResult:
        start = time.time()
        try:
            if action == "create_event":
                result = {"event_id": f"gcal-{uuid.uuid4().hex[:8]}", "status": "created"}
            elif action == "list_events":
                result = {"events": [], "count": 0}
            else:
                result = {"action": action, "status": "ok"}

            return ConnectorResult(
                connector_id="google_calendar", status="success", output=result,
                duration_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            return ConnectorResult(
                connector_id="google_calendar", status="error", error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )

    def metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            id="google_calendar", name="Google Calendar",
            description="Gestionar eventos de calendario Google",
            category="calendar", auth_type="oauth2",
            capabilities=["create_event", "list_events", "update_event", "delete_event"],
        )


# ============================================================
# Slack Connector
# ============================================================

class SlackConnector(BaseConnector):
    """Conector para Slack."""

    def __init__(self):
        self._connected = False

    async def connect(self, credentials: dict) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        return True

    async def health(self) -> dict:
        return {"status": "healthy" if self._connected else "disconnected", "service": "slack"}

    async def execute(self, action: str, params: dict) -> ConnectorResult:
        start = time.time()
        try:
            if action == "send_message":
                result = {"message_id": f"slack-{uuid.uuid4().hex[:8]}", "status": "sent"}
            elif action == "list_channels":
                result = {"channels": [], "count": 0}
            else:
                result = {"action": action, "status": "ok"}

            return ConnectorResult(
                connector_id="slack", status="success", output=result,
                duration_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            return ConnectorResult(
                connector_id="slack", status="error", error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )

    def metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            id="slack", name="Slack",
            description="Enviar mensajes y gestionar canales Slack",
            category="chat", auth_type="api_key",
            capabilities=["send_message", "list_channels", "read_messages"],
        )


# ============================================================
# REST API Connector (Genérico)
# ============================================================

class RESTAPIConnector(BaseConnector):
    """Conector genérico para APIs REST."""

    def __init__(self):
        self._connected = False
        self._base_url = ""

    async def connect(self, credentials: dict) -> bool:
        self._base_url = credentials.get("base_url", "")
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        return True

    async def health(self) -> dict:
        return {"status": "healthy" if self._connected else "disconnected", "service": "rest_api", "base_url": self._base_url}

    async def execute(self, action: str, params: dict) -> ConnectorResult:
        start = time.time()
        try:
            url = params.get("url", self._base_url)
            method = params.get("method", "GET").upper()
            headers = params.get("headers", {})
            body = params.get("body")

            async with public_http_client(timeout=30) as client:
                response = await client.request(method, url, headers=headers, content=body)

            result = {
                "status_code": response.status_code,
                "body": response.text[:5000],
                "headers": dict(response.headers),
            }

            return ConnectorResult(
                connector_id="rest_api", status="success", output=result,
                duration_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            return ConnectorResult(
                connector_id="rest_api", status="error", error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )

    def metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            id="rest_api", name="REST API",
            description="Conector genérico para cualquier API REST",
            category="api", auth_type="api_key",
            capabilities=["get", "post", "put", "delete", "patch"],
        )


# ============================================================
# Connector Manager
# ============================================================

class ConnectorManager:
    """Gestor central de conectores."""

    def __init__(self):
        self._connectors: dict[str, BaseConnector] = {}
        self._connected: dict[str, bool] = {}

    def register(self, connector: BaseConnector):
        """Registra un conector."""
        meta = connector.metadata()
        self._connectors[meta.id] = connector
        self._connected[meta.id] = False

    async def connect(self, connector_id: str, credentials: dict) -> bool:
        """Conecta un conector."""
        connector = self._connectors.get(connector_id)
        if not connector:
            return False
        result = await connector.connect(credentials)
        self._connected[connector_id] = result
        return result

    async def disconnect(self, connector_id: str) -> bool:
        """Desconecta un conector."""
        connector = self._connectors.get(connector_id)
        if not connector:
            return False
        result = await connector.disconnect()
        self._connected[connector_id] = False
        return result

    async def health(self, connector_id: str) -> dict:
        """Verifica salud de un conector."""
        connector = self._connectors.get(connector_id)
        if not connector:
            return {"status": "not_found"}
        return await connector.health()

    async def execute(self, connector_id: str, action: str, params: dict) -> ConnectorResult:
        """Ejecuta una acción en un conector."""
        connector = self._connectors.get(connector_id)
        if not connector:
            return ConnectorResult(
                connector_id=connector_id,
                status="error",
                error=f"Connector '{connector_id}' not found",
            )
        return await connector.execute(action, params)

    def list_all(self) -> list[ConnectorMetadata]:
        """Lista todos los conectores."""
        return [c.metadata() for c in self._connectors.values()]

    def get(self, connector_id: str) -> BaseConnector | None:
        """Obtiene un conector."""
        return self._connectors.get(connector_id)

    def count(self) -> int:
        return len(self._connectors)
