"""
Agent API — Endpoints para agentes ejecutivos.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, Company
from app.ai.factory import get_llm_adapter
from app.ems.memory import EnterpriseMemorySystem
from app.ems.providers import LocalEmbeddingProvider, LocalVectorStoreProvider
from app.tef.executor import ToolExecutor
from app.tef.registry import ToolRegistry
from app.tef.tools import CalculatorTool, HttpRequestTool, EmailSenderTool
from app.agents.ceo import CEOAgent
from app.agents.base import AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])


# ============================================================
# Schemas
# ============================================================

class AgentRequest(BaseModel):
    message: str
    company_id: str


class AgentPlanStep(BaseModel):
    action: str
    reasoning: str


class AgentPlanResponse(BaseModel):
    goal: str
    steps: list[AgentPlanStep]
    reasoning: str


class AgentResponseSchema(BaseModel):
    agent: str
    response: str
    plan: AgentPlanResponse | None = None
    tools_used: list[str]
    memory_context: str
    justification: str
    confidence: float
    duration_ms: int


# ============================================================
# Singletons
# ============================================================

_embedding_provider = LocalEmbeddingProvider(dim=128)
_vector_store = LocalVectorStoreProvider()
_tef_registry = ToolRegistry()
_tef_executor = ToolExecutor(_tef_registry)

# Registrar herramientas.
# file_reader, python_sandbox y sql_query quedan fuera hasta tener aislamiento real.
_tef_registry.register(CalculatorTool())
_tef_registry.register(HttpRequestTool())
_tef_registry.register(EmailSenderTool())


# ============================================================
# Endpoints
# ============================================================

@router.post("/ceo", response_model=AgentResponseSchema)
async def ceo_analyze(
    request: AgentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    CEO Agent — Analiza una empresa y produce decisiones ejecutivas.
    
    Flujo:
    1. Recuperar memoria empresarial
    2. Analizar solicitud
    3. Ejecutar herramientas si es necesario
    4. Generar análisis y recomendaciones
    5. Justificar cada decisión
    """
    # Verificar que la empresa pertenece al usuario
    company = db.query(Company).filter(
        Company.id == request.company_id,
        Company.primary_user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Crear componentes
    llm = get_llm_adapter()
    ems = EnterpriseMemorySystem(db, _embedding_provider, _vector_store)

    # Crear agente CEO
    ceo = CEOAgent(llm, ems, _tef_executor)

    # Ejecutar
    result: AgentResponse = await ceo.process(
        message=request.message,
        company_id=request.company_id,
        user_id=str(current_user.id),
    )

    # Construir respuesta
    plan_response = None
    if result.plan:
        plan_response = AgentPlanResponse(
            goal=result.plan.goal,
            steps=[
                AgentPlanStep(action=s.get("action", ""), reasoning=s.get("reasoning", ""))
                for s in result.plan.steps
            ],
            reasoning=result.plan.reasoning,
        )

    return AgentResponseSchema(
        agent=result.agent,
        response=result.response,
        plan=plan_response,
        tools_used=result.tools_used,
        memory_context=result.memory_context,
        justification=result.justification,
        confidence=result.confidence,
        duration_ms=result.duration_ms,
    )


@router.get("/health")
async def agents_health():
    """Health check del sistema de agentes."""
    return {
        "status": "healthy",
        "agents": ["ceo"],
        "version": "0.1.0-wo006",
    }
