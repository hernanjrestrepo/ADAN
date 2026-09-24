"""
API Endpoint para el Sistema Cognitivo de ADÁN.

Endpoint principal del vertical slice de WO-003.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, Company, Card, Conversation, Project
from app.ai.factory import get_llm_adapter
from app.core.disclaimer import AI_DISCLAIMER

from app.cognitive.orchestrator import CognitiveOrchestrator, CognitiveResponse

router = APIRouter(prefix="/cognitive", tags=["cognitive"])


class CognitiveRequest(BaseModel):
    message: str
    company_id: str
    conversation_id: str | None = None


class CognitiveStepResponse(BaseModel):
    component: str
    description: str
    duration_ms: int
    status: str


class CognitiveJustificationResponse(BaseModel):
    decision: str
    confidence: float
    reasoning: str
    supporting_facts: list[str]
    alternatives: list[str]
    risk_assessment: str


class CognitiveResponseSchema(BaseModel):
    response: str
    trace_id: str
    duration_ms: int
    events_published: int
    components_used: list[str]
    quality_score: float
    justification: CognitiveJustificationResponse | None = None
    plan_steps: int
    knowledge_units: int
    disclaimer: str = AI_DISCLAIMER


@router.post("/think", response_model=CognitiveResponseSchema)
async def cognitive_think(
    request: CognitiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint principal del cerebro cognitivo de ADÁN.
    
    Procesa una solicitud del usuario a través de todo el pipeline:
    Memoria → Conocimiento → Planificación → Ejecución → Evaluación → Respuesta
    
    Retorna la respuesta con trazabilidad completa.
    """
    # Verificar que la empresa pertenece al usuario
    company = db.query(Company).filter(
        Company.id == request.company_id,
        Company.primary_user_id == current_user.id,
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Verificar que la conversación pertenece a la empresa
    if request.conversation_id:
        conversation = (
            db.query(Conversation)
            .join(Card, Conversation.card_id == Card.id)
            .join(Project, Card.project_id == Project.id)
            .filter(Conversation.id == request.conversation_id, Project.company_id == company.id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # Crear orquestador cognitivo
    llm = get_llm_adapter()
    orchestrator = CognitiveOrchestrator(llm=llm, db=db)

    # Procesar
    result: CognitiveResponse = await orchestrator.process(
        user_message=request.message,
        company_id=request.company_id,
        user_id=str(current_user.id),
        conversation_id=request.conversation_id,
    )
    # El orquestador solo hace flush: sin commit se perdían eventos y mensajes
    db.commit()

    # Construir respuesta
    justification_data = None
    if result.justification:
        justification_data = CognitiveJustificationResponse(
            decision=result.justification.decision,
            confidence=result.justification.confidence,
            reasoning=result.justification.reasoning,
            supporting_facts=result.justification.supporting_facts,
            alternatives=result.justification.alternatives,
            risk_assessment=result.justification.risk_assessment,
        )

    return CognitiveResponseSchema(
        response=result.response,
        trace_id=result.trace_id,
        duration_ms=result.duration_ms,
        events_published=result.events_published,
        components_used=result.components_used,
        quality_score=result.metrics.get("quality_score", 0),
        justification=justification_data,
        plan_steps=result.metrics.get("plan_steps", 0),
        knowledge_units=result.metrics.get("knowledge_units", 0),
    )


@router.get("/health")
async def cognitive_health():
    """Health check del sistema cognitivo."""
    return {
        "status": "healthy",
        "components": [
            "event_bus",
            "memory_engine",
            "knowledge_engine",
            "planner",
            "tool_manager",
            "decision_engine",
            "orchestrator",
        ],
        "version": "0.1.0-wo003",
    }
