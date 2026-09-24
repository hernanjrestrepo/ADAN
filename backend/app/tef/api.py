"""
TEF API — Endpoints para el Tool Execution Framework.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, Company
from app.tef.interfaces import ToolContext
from app.tef.registry import ToolRegistry
from app.tef.executor import ToolExecutor
from app.tef.tools import CalculatorTool, HttpRequestTool, EmailSenderTool

router = APIRouter(prefix="/tef", tags=["tef"])


# ============================================================
# Schemas
# ============================================================

class ExecuteRequest(BaseModel):
    tool_id: str
    params: dict
    company_id: str
    dry_run: bool = False


class ExecuteResponse(BaseModel):
    tool_id: str
    status: str
    output: dict | None = None
    error: str | None = None
    duration_ms: int
    retries_used: int


class ToolInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    version: str
    tags: list[str]


class DiscoverRequest(BaseModel):
    query: str
    company_id: str


class AuditEntry(BaseModel):
    tool_id: str
    status: str
    error: str | None
    company_id: str
    user_id: str
    trace_id: str
    timestamp: str


# ============================================================
# Singleton: Registry y Executor
# ============================================================

_registry = ToolRegistry()
_executor = ToolExecutor(_registry)

# Registrar herramientas iniciales.
# file_reader, python_sandbox y sql_query quedan fuera hasta tener aislamiento real.
_registry.register(CalculatorTool())
_registry.register(HttpRequestTool())
_registry.register(EmailSenderTool())


def get_executor() -> ToolExecutor:
    return _executor


def require_company(db: Session, company_id: str, user: User) -> Company:
    """Verifica que la empresa pertenece al usuario."""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return company


# ============================================================
# Endpoints
# ============================================================

@router.get("/tools", response_model=list[ToolInfo])
async def list_tools():
    """Lista todas las herramientas disponibles."""
    tools = _registry.list_all()
    return [
        ToolInfo(
            id=t.id,
            name=t.name,
            description=t.description,
            category=t.category,
            version=t.version,
            tags=t.tags,
        )
        for t in tools
    ]


@router.post("/discover", response_model=list[ToolInfo])
async def discover_tools(
    request: DiscoverRequest,
    current_user: User = Depends(get_current_user),
):
    """Descubre herramientas relevantes para una query."""
    tools = _registry.discover(request.query)
    return [
        ToolInfo(
            id=t.id,
            name=t.name,
            description=t.description,
            category=t.category,
            version=t.version,
            tags=t.tags,
        )
        for t in tools
    ]


@router.post("/execute", response_model=ExecuteResponse)
async def execute_tool(
    request: ExecuteRequest,
    current_user: User = Depends(get_current_user),
    executor: ToolExecutor = Depends(get_executor),
    db: Session = Depends(get_db),
):
    """Ejecuta una herramienta."""
    require_company(db, request.company_id, current_user)

    import uuid
    context = ToolContext(
        company_id=request.company_id,
        user_id=str(current_user.id),
        trace_id=f"tef-{uuid.uuid4().hex[:12]}",
    )

    result = await executor.execute(
        tool_id=request.tool_id,
        params=request.params,
        context=context,
        dry_run=request.dry_run,
    )

    return ExecuteResponse(
        tool_id=result.tool_id,
        status=result.status,
        output=result.output if isinstance(result.output, dict) else {"result": result.output},
        error=result.error,
        duration_ms=result.duration_ms,
        retries_used=result.retries_used,
    )


@router.get("/audit/{company_id}", response_model=list[AuditEntry])
async def get_audit_log(
    company_id: str,
    current_user: User = Depends(get_current_user),
    executor: ToolExecutor = Depends(get_executor),
    db: Session = Depends(get_db),
):
    """Obtiene el log de auditoría de herramientas."""
    require_company(db, company_id, current_user)

    log = executor.get_audit_log(company_id=company_id)
    return [AuditEntry(**entry) for entry in log]


@router.get("/health")
async def tef_health():
    """Health check del TEF."""
    return {
        "status": "healthy",
        "tools_registered": _registry.count(),
        "version": "0.1.0-wo005",
    }
