"""Lanzar Agentes y consultar el historial de ejecuciones. BP-0007.
Enfoque asincrono: POST encola y devuelve execution_id de inmediato (no bloquea esperando
inferencia real); GET consulta el estado real en Postgres, escrito por el worker de /ai."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agent_queue import enqueue_agent_run
from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models.ejecucion_agente import EjecucionAgenteLectura
from app.models.usuario import Usuario

router = APIRouter(prefix="/agents", tags=["agents"])

# Agentes conocidos por el backend - debe coincidir con agents/registry.py de /ai
# (ver contracts/events/agent_execution.md). Duplicacion deliberada, no import cruzado.
KNOWN_AGENT_IDS = {"diagnostico-nivel-1"}


class RunAgentRequest(BaseModel):
    agent_id: str
    user_input: str
    proyecto_id: str | None = None


class RunAgentResponse(BaseModel):
    execution_id: str


class EjecucionAgenteResponse(BaseModel):
    id: str
    agent_id: str
    status: str
    user_input: str
    final_output: str | None
    error: str | None


def _to_response(ejecucion: EjecucionAgenteLectura) -> EjecucionAgenteResponse:
    return EjecucionAgenteResponse(
        id=str(ejecucion.id),
        agent_id=ejecucion.agent_id,
        status=ejecucion.status,
        user_input=ejecucion.user_input,
        final_output=ejecucion.final_output,
        error=ejecucion.error,
    )


@router.post("/run", response_model=RunAgentResponse, status_code=status.HTTP_202_ACCEPTED)
def run_agent(
    payload: RunAgentRequest,
    _user: Usuario = Depends(get_current_user),
) -> RunAgentResponse:
    if payload.agent_id not in KNOWN_AGENT_IDS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown agent_id")
    execution_id = enqueue_agent_run(payload.agent_id, payload.user_input, payload.proyecto_id)
    return RunAgentResponse(execution_id=execution_id)


@router.get("/runs", response_model=list[EjecucionAgenteResponse])
def list_runs(
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    _user: Usuario = Depends(get_current_user),
) -> list[EjecucionAgenteResponse]:
    ejecuciones = (
        db.query(EjecucionAgenteLectura)
        .order_by(EjecucionAgenteLectura.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_to_response(e) for e in ejecuciones]


@router.get("/runs/{execution_id}", response_model=EjecucionAgenteResponse)
def get_run(
    execution_id: str,
    db: Session = Depends(get_db),
    _user: Usuario = Depends(get_current_user),
) -> EjecucionAgenteResponse:
    ejecucion = (
        db.query(EjecucionAgenteLectura).filter(EjecucionAgenteLectura.id == execution_id).first()
    )
    if ejecucion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")
    return _to_response(ejecucion)
