"""
Integration Hub API — Endpoints para integraciones externas.

WO-097 (S13): cada empresa tiene sus propias conexiones. Antes había un objeto global de
conectores compartido por todos los usuarios: lo que uno conectaba lo usaba cualquiera.
Ahora cada petición crea su propio conector y lo conecta con las credenciales de *esa*
empresa, que se guardan cifradas (`integration_connections`) y nunca se devuelven.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.crypto import decrypt_json, encrypt_json
from app.core.database import get_db
from app.integrations.connectors import (
    BaseConnector, GmailConnector, GoogleCalendarConnector, OutlookConnector, RESTAPIConnector,
    SlackConnector,
)
from app.integrations.models import IntegrationConnection
from app.models.models import User

router = APIRouter(prefix="/integrations", tags=["integrations"])

# Solo el conector REST hace llamadas reales; los demás son simulados hasta WO-119
REAL_CONNECTORS = {"rest_api"}

CONNECTORS: dict[str, type[BaseConnector]] = {
    cls().metadata().id: cls
    for cls in (GmailConnector, OutlookConnector, GoogleCalendarConnector, SlackConnector, RESTAPIConnector)
}


class ConnectRequest(BaseModel):
    company_id: str
    connector_id: str
    credentials: dict = Field(default_factory=dict)


class DisconnectRequest(BaseModel):
    company_id: str
    connector_id: str


class ExecuteRequest(BaseModel):
    company_id: str
    connector_id: str
    action: str = Field(max_length=100)
    params: dict = Field(default_factory=dict)


def _connector_class(connector_id: str) -> type[BaseConnector]:
    cls = CONNECTORS.get(connector_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Conector no encontrado")
    return cls


def _connection(db: Session, company_id: str, connector_id: str) -> IntegrationConnection | None:
    return db.query(IntegrationConnection).filter_by(company_id=company_id, connector_id=connector_id).first()


async def _company_connector(db: Session, company_id: str, connector_id: str) -> tuple[BaseConnector, bool]:
    """Un conector nuevo, conectado con las credenciales de la empresa si las tiene."""
    connector = _connector_class(connector_id)()
    connection = _connection(db, company_id, connector_id)
    if connection is None or connection.status != "connected":
        return connector, False
    try:
        credentials = decrypt_json(connection.credentials_encrypted)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=f"{exc}. Vuelve a conectar {connector_id}.")
    return connector, await connector.connect(credentials)


@router.get("/connectors")
async def list_connectors(current_user: User = Depends(get_current_user)):
    """Lista conectores disponibles."""
    return [
        {
            "id": meta.id,
            "name": meta.name,
            "description": meta.description,
            "category": meta.category,
            "auth_type": meta.auth_type,
            "capabilities": meta.capabilities,
            "version": meta.version,
            "mock": meta.id not in REAL_CONNECTORS,
        }
        for meta in (cls().metadata() for cls in CONNECTORS.values())
    ]


@router.get("/connections/{company_id}")
def list_connections(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Conexiones de la empresa. Nunca incluye credenciales."""
    get_owned_company(db, company_id, current_user)
    connections = db.query(IntegrationConnection).filter_by(company_id=company_id).all()
    return [
        {"connector_id": c.connector_id, "status": c.status, "updated_at": c.updated_at.isoformat()}
        for c in connections
    ]


@router.post("/connect")
async def connect_service(
    request: ConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Conecta un servicio para la empresa y guarda sus credenciales cifradas."""
    get_owned_company(db, request.company_id, current_user)
    connector = _connector_class(request.connector_id)()
    connected = await connector.connect(request.credentials)
    if connected:
        connection = _connection(db, request.company_id, request.connector_id)
        if connection is None:
            connection = IntegrationConnection(
                company_id=request.company_id, connector_id=request.connector_id, created_by=current_user.id,
            )
            db.add(connection)
        connection.credentials_encrypted = encrypt_json(request.credentials)
        connection.status = "connected"
        db.commit()
    return {"connector_id": request.connector_id, "connected": connected,
            "mock": request.connector_id not in REAL_CONNECTORS}


@router.post("/disconnect")
async def disconnect_service(
    request: DisconnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Desconecta el servicio y borra sus credenciales (la fila queda como registro)."""
    get_owned_company(db, request.company_id, current_user)
    _connector_class(request.connector_id)
    connection = _connection(db, request.company_id, request.connector_id)
    if connection is None:
        raise HTTPException(status_code=404, detail="La empresa no tiene ese servicio conectado")
    connection.credentials_encrypted = encrypt_json({})
    connection.status = "disconnected"
    db.commit()
    return {"connector_id": request.connector_id, "disconnected": True}


@router.get("/health/{company_id}/{connector_id}")
async def connector_health(
    company_id: str,
    connector_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Salud del conector con las credenciales de la empresa."""
    get_owned_company(db, company_id, current_user)
    connector, _ = await _company_connector(db, company_id, connector_id)
    return await connector.health()


@router.post("/execute")
async def execute_connector(
    request: ExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ejecuta una acción del conector con las credenciales de la empresa."""
    get_owned_company(db, request.company_id, current_user)
    connector, _ = await _company_connector(db, request.company_id, request.connector_id)
    result = await connector.execute(request.action, request.params)
    return {
        "connector_id": result.connector_id,
        "status": result.status,
        "output": result.output,
        "error": result.error,
        "duration_ms": result.duration_ms,
        "mock": result.connector_id not in REAL_CONNECTORS,
    }


@router.get("/health")
async def integrations_health():
    return {
        "status": "healthy",
        "connectors": len(CONNECTORS),
        "version": "0.2.0-wo097",
    }
