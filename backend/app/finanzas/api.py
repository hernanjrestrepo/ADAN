"""Finanzas y estrategia: organigrama híbrido, flujo de caja e informe ejecutivo."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.ai.usage import usage_scope
from app.api.v1.nivel1 import get_llm
from app.constitucion.service import company_context, markdown_to_docx
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.core.ratelimit import llm_user
from app.finanzas import modelo
from app.finanzas.service import Finanzas, report_markdown
from app.models.models import Project, User
from app.nivel1.service import Nivel1Service

router = APIRouter(prefix="/finanzas", tags=["finanzas"])


class AssumptionsBody(BaseModel):
    assumptions: dict


def _project(db: Session, company_id: str, user: User):
    company = get_owned_company(db, company_id, user)
    return company, db.query(Project).filter(Project.company_id == company_id).first()


def _context(db: Session, project: Project, company, llm) -> str:
    brief = Nivel1Service(llm, db).board_brief(project)
    return company_context(db, project, company) + (f"\n\nLo que ADAN sabe del dolor y la evidencia:\n{brief[:5000]}" if brief else "")


def _got(data, what: str):
    if data is None:
        raise HTTPException(status_code=404, detail=f"Todavía no hay {what}")
    return data


@router.post("/{company_id}/organigrama")
async def build_org(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                    llm: LLMAdapter = Depends(get_llm)):
    company, project = _project(db, company_id, user)
    with usage_scope(db, company_id, level=3):
        try:
            return await Finanzas(llm, db).build_org(project, _context(db, project, company, llm))
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc))


@router.get("/{company_id}/organigrama")
def get_org(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _project(db, company_id, user)
    return _got(Finanzas(None, db).org(project), "organigrama")


@router.post("/{company_id}/modelo")
async def build_model(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                      llm: LLMAdapter = Depends(get_llm)):
    company, project = _project(db, company_id, user)
    with usage_scope(db, company_id, level=3):
        try:
            return await Finanzas(llm, db).build_model(project, _context(db, project, company, llm))
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc))


@router.post("/{company_id}/modelo/calcular")
def recompute(company_id: str, body: AssumptionsBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """El cliente corrige un supuesto y el flujo se recalcula al instante (sin modelo de lenguaje)."""
    _, project = _project(db, company_id, user)
    return Finanzas(None, db).recompute(project, body.assumptions)


@router.get("/{company_id}/modelo")
def get_model(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _project(db, company_id, user)
    return _got(Finanzas(None, db).model(project), "modelo financiero")


@router.get("/{company_id}/modelo.xlsx")
def model_xlsx(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _project(db, company_id, user)
    model = _got(Finanzas(None, db).model(project), "modelo financiero")
    return Response(modelo.to_xlsx(model, company.name),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="flujo-de-caja.xlsx"'})


@router.post("/{company_id}/informe")
async def build_report(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                       llm: LLMAdapter = Depends(get_llm)):
    company, project = _project(db, company_id, user)
    with usage_scope(db, company_id, level=3):
        try:
            return await Finanzas(llm, db).build_report(project, _context(db, project, company, llm), company)
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc))


@router.get("/{company_id}/informe")
def get_report(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _project(db, company_id, user)
    return _got(Finanzas(None, db).report(project), "informe ejecutivo")


@router.get("/{company_id}/informe.docx")
def report_docx(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _project(db, company_id, user)
    report = _got(Finanzas(None, db).report(project), "informe ejecutivo")
    return Response(markdown_to_docx(report_markdown(report), f"Informe ejecutivo: {company.name}"),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": 'attachment; filename="informe-ejecutivo.docx"'})
