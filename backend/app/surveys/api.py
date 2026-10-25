"""Encuestas: el fundador las crea y ve resultados; quien responde entra sin cuenta por el enlace público."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.ai.usage import usage_scope
from app.api.v1.nivel1 import get_llm
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.core.ratelimit import llm_user
from app.models.models import Project, User
from app.nivel1.service import Nivel1Service
from app.surveys.service import Surveys

router = APIRouter(tags=["encuestas"])


class CreateBody(BaseModel):
    objective: str = Field("", max_length=1000)


class AnswerBody(BaseModel):
    answers: dict[str, str | int | float | list[str]] = Field(default_factory=dict)
    consent: bool = False


class OpenBody(BaseModel):
    open: bool


def _project(db: Session, company_id: str, user: User):
    company = get_owned_company(db, company_id, user)
    return company, db.query(Project).filter(Project.company_id == company_id).first()


@router.post("/nivel1/{company_id}/surveys")
async def create_survey(company_id: str, body: CreateBody | None = None, db: Session = Depends(get_db),
                        user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    company, project = _project(db, company_id, user)
    brief = Nivel1Service(llm, db).board_brief(project)
    with usage_scope(db, company_id, level=1):
        try:
            return await Surveys(llm, db).create(project, company, brief, body.objective.strip() if body else "")
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc))


@router.get("/nivel1/{company_id}/surveys")
def list_surveys(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _project(db, company_id, user)
    return Surveys(None, db).list(project)


@router.get("/nivel1/{company_id}/surveys/{token}/results")
def survey_results(company_id: str, token: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _project(db, company_id, user)
    survey = Surveys(None, db).get(token, project)
    if not survey:
        raise HTTPException(status_code=404, detail="La encuesta no existe")
    return Surveys.results(survey)


@router.post("/nivel1/{company_id}/surveys/{token}/open")
def set_open(company_id: str, token: str, body: OpenBody, db: Session = Depends(get_db),
             user: User = Depends(get_current_user)):
    _, project = _project(db, company_id, user)
    try:
        return Surveys.results(Surveys(None, db).close(project, token, body.open))
    except LookupError:
        raise HTTPException(status_code=404, detail="La encuesta no existe")


@router.post("/nivel1/{company_id}/surveys/{token}/simular")
async def simulate_survey(company_id: str, token: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                          llm: LLMAdapter = Depends(get_llm)):
    """Encuesta simulada con el Simulador de Mercado: se avanza ya y se contrasta cuando lleguen las respuestas reales."""
    _, project = _project(db, company_id, user)
    surveys = Surveys(llm, db)
    survey = surveys.get(token, project)
    if not survey:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    with usage_scope(db, company_id, level=1):
        return await surveys.simulate(project, survey, Nivel1Service(llm, db).board_brief(project))


@router.post("/nivel1/{company_id}/surveys/{token}/insights")
async def survey_insights(company_id: str, token: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                          llm: LLMAdapter = Depends(get_llm)):
    _, project = _project(db, company_id, user)
    surveys = Surveys(llm, db)
    survey = surveys.get(token, project)
    if not survey:
        raise HTTPException(status_code=404, detail="La encuesta no existe")
    with usage_scope(db, company_id, level=1):
        try:
            return await surveys.insights(survey)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))


# --- Público: quien recibe el enlace responde sin cuenta ---

@router.get("/encuestas/{token}")
def public_survey(token: str, db: Session = Depends(get_db)):
    survey = Surveys(None, db).get(token)
    if not survey:
        raise HTTPException(status_code=404, detail="La encuesta no existe o ya no está disponible")
    return Surveys.public(survey)


@router.post("/encuestas/{token}", status_code=201)
def answer_survey(token: str, body: AnswerBody, db: Session = Depends(get_db)):
    try:
        Surveys(None, db).answer(token, {k: v for k, v in body.answers.items()}, body.consent)
    except LookupError:
        raise HTTPException(status_code=404, detail="La encuesta no existe")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"ok": True, "message": "¡Gracias! Tus respuestas quedaron registradas de forma anónima."}
