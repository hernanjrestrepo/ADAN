"""
Integration Hub API — Endpoints para integraciones externas.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.models import User
from app.integrations.connectors import (
    ConnectorManager, GmailConnector, OutlookConnector,
    GoogleCalendarConnector, SlackConnector, RESTAPIConnector,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


class ConnectRequest(BaseModel):
    connector_id: str
    credentials: dict = {}


class ExecuteRequest(BaseModel):
    connector_id: str
    action: str
    params: dict = {}


# Singleton
_manager = ConnectorManager()
_manager.register(GmailConnector())
_manager.register(OutlookConnector())
_manager.register(GoogleCalendarConnector())
_manager.register(SlackConnector())
_manager.register(RESTAPIConnector())


@router.get("/connectors")
async def list_connectors(current_user: User = Depends(get_current_user)):
    """Lista conectores disponibles."""
    connectors = _manager.list_all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "category": c.category,
            "auth_type": c.auth_type,
            "capabilities": c.capabilities,
            "version": c.version,
        }
        for c in connectors
    ]


@router.post("/connect")
async def connect_service(
    request: ConnectRequest,
    current_user: User = Depends(get_current_user),
):
    """Conecta a un servicio externo."""
    result = await _manager.connect(request.connector_id, request.credentials)
    return {"connector_id": request.connector_id, "connected": result}


@router.post("/disconnect")
async def disconnect_service(
    connector_id: str,
    current_user: User = Depends(get_current_user),
):
    """Desconecta de un servicio."""
    result = await _manager.disconnect(connector_id)
    return {"connector_id": connector_id, "disconnected": result}


@router.get("/health/{connector_id}")
async def connector_health(
    connector_id: str,
    current_user: User = Depends(get_current_user),
):
    """Verifica salud de un conector."""
    return await _manager.health(connector_id)


@router.post("/execute")
async def execute_connector(
    request: ExecuteRequest,
    current_user: User = Depends(get_current_user),
):
    """Ejecuta una acción en un conector."""
    result = await _manager.execute(
        request.connector_id,
        request.action,
        request.params,
    )
    return {
        "connector_id": result.connector_id,
        "status": result.status,
        "output": result.output,
        "error": result.error,
        "duration_ms": result.duration_ms,
    }


@router.get("/health")
async def integrations_health():
    return {
        "status": "healthy",
        "connectors": _manager.count(),
        "version": "0.1.0-wo010",
    }
