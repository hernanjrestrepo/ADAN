"""
Board API — Endpoint para el Executive Board con deliberación real.
"""

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.schemas.schemas import MAX_MESSAGE_CHARS
from app.core.authz import get_owned_company
from app.core.ratelimit import llm_user
from app.models.models import User
from app.ai.factory import get_llm_adapter
from app.core.disclaimer import AI_DISCLAIMER
from app.ems.memory import EnterpriseMemorySystem
from app.ems.store import embedding_provider, get_vector_store
from app.tef.executor import ToolExecutor
from app.tef.registry import ToolRegistry
from app.tef.tools import CalculatorTool
from app.agents.board import ExecutiveBoard, BOARD_AGENTS

router = APIRouter(prefix="/board", tags=["board"])


# ============================================================
# Schemas
# ============================================================

class BoardRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    company_id: str


class DebateRoundSchema(BaseModel):
    agent: str
    role: str
    round_number: int
    analysis: str
    response_to_previous: str
    vote: str
    confidence: float
    objections: list[str]
    key_points: list[str]
    question_for_board: str
    duration_ms: int


class DecisionRecordSchema(BaseModel):
    id: str
    topic: str
    final_decision: str
    final_score: float
    final_confidence: float
    votes: dict[str, str]
    key_objections: list[str]
    actions: list[dict]
    follow_up: list[dict]
    dissent_details: str


class BoardResponseSchema(BaseModel):
    deliberation_rounds: list[DebateRoundSchema]
    final_decision: str
    final_score: float
    final_confidence: float
    dissent_rounds: list[int]
    decision_record: DecisionRecordSchema
    agents_count: int
    duration_ms: int
    disclaimer: str = AI_DISCLAIMER


# ============================================================
# Singletons
# ============================================================

_tef_registry = ToolRegistry()
_tef_executor = ToolExecutor(_tef_registry)
_tef_registry.register(CalculatorTool())


def get_board(db: Session = Depends(get_db)) -> ExecutiveBoard:
    llm = get_llm_adapter()
    ems = EnterpriseMemorySystem(db, embedding_provider, get_vector_store(db))
    return ExecutiveBoard(llm, ems, _tef_executor)


# ============================================================
# Endpoints
# ============================================================

@router.post("/run", response_model=BoardResponseSchema)
async def run_board(
    request: BoardRequest,
    current_user: User = Depends(llm_user),
    db: Session = Depends(get_db),
):
    """Board ejecutivo (operación continua): el mismo Board Room de 7 roles de los Niveles.

    El CEO preside; CTO, CFO, CMO, Legal, Producto y Operaciones votan con la memoria de la
    empresa y sus decisiones pasadas como contexto. Se produce un Decision Record persistente.
    """
    # Verificar que la empresa pertenece al usuario
    get_owned_company(db, request.company_id, current_user)

    board = get_board(db)

    result = await board.run(
        message=request.message,
        company_id=request.company_id,
        user_id=str(current_user.id),
    )

    delib = result.deliberation
    record = result.decision_record

    return BoardResponseSchema(
        deliberation_rounds=[
            DebateRoundSchema(
                agent=r.agent,
                role=r.role,
                round_number=r.round_number,
                analysis=r.analysis,
                response_to_previous=r.response_to_previous,
                vote=r.vote,
                confidence=r.confidence,
                objections=r.objections,
                key_points=r.key_points,
                question_for_board=r.question_for_board,
                duration_ms=r.duration_ms,
            )
            for r in delib.rounds
        ],
        final_decision=record.final_decision,
        final_score=record.final_score,
        final_confidence=record.final_confidence,
        dissent_rounds=delib.dissent_rounds,
        decision_record=DecisionRecordSchema(
            id=record.id,
            topic=record.topic,
            final_decision=record.final_decision,
            final_score=record.final_score,
            final_confidence=record.final_confidence,
            votes=record.votes,
            key_objections=record.key_objections,
            actions=record.actions,
            follow_up=record.follow_up,
            dissent_details=record.dissent_details,
        ),
        agents_count=len(delib.rounds),
        duration_ms=result.duration_ms,
    )


@router.get("/health")
async def board_health():
    """Health check del Board."""
    return {
        "status": "healthy",
        "agents": list(BOARD_AGENTS.keys()),
        "version": "wo099-board-unico",
    }
