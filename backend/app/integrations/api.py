"""
Integration Hub API — Endpoints para integraciones externas.
"""

from fastapi import APIRouter, Depends
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


# Un gestor por usuario: las credenciales y conexiones de un usuario nunca
# son visibles ni utilizables por otro (antes era un singleton global).
# Nota: viven en memoria del proceso; con varios workers cada uno tiene las suyas.
_managers: dict[str, ConnectorManager] = {}


def _new_manager() -> ConnectorManager:
    manager = ConnectorManager()
    manager.register(GmailConnector())
    manager.register(OutlookConnector())
    manager.register(GoogleCalendarConnector())
    manager.register(SlackConnector())
    manager.register(RESTAPIConnector())
    return manager


def get_manager(current_user: User = Depends(get_current_user)) -> ConnectorManager:
    manager = _managers.get(current_user.id)
    if manager is None:
        manager = _managers[current_user.id] = _new_manager()
    return manager


# Catálogo (sin estado de usuario) para listados y health
_catalog = _new_manager()


@router.get("/connectors")
async def list_connectors(current_user: User = Depends(get_current_user)):
    """Lista conectores disponibles."""
    connectors = _catalog.list_all()
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
    manager: ConnectorManager = Depends(get_manager),
):
    """Conecta a un servicio externo."""
    result = await manager.connect(request.connector_id, request.credentials)
    return {"connector_id": request.connector_id, "connected": result}


@router.post("/disconnect")
async def disconnect_service(
    connector_id: str,
    manager: ConnectorManager = Depends(get_manager),
):
    """Desconecta de un servicio."""
    result = await manager.disconnect(connector_id)
    return {"connector_id": connector_id, "disconnected": result}


@router.get("/health/{connector_id}")
async def connector_health(
    connector_id: str,
    manager: ConnectorManager = Depends(get_manager),
):
    """Verifica salud de un conector."""
    return await manager.health(connector_id)


@router.post("/execute")
async def execute_connector(
    request: ExecuteRequest,
    manager: ConnectorManager = Depends(get_manager),
):
    """Ejecuta una acción en un conector."""
    result = await manager.execute(
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
        "connectors": _catalog.count(),
        "version": "0.1.0-wo010",
    }
