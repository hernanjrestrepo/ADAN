"""Constitución de la empresa: nombre y dominios, ruta legal del país y estatutos."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.ai.usage import usage_scope
from app.api.v1.nivel1 import get_llm
from app.constitucion import dominios
from app.constitucion.service import Constitucion, company_context, markdown_to_docx
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.core.ratelimit import llm_user
from app.models.models import Document, Project, User

router = APIRouter(prefix="/constitucion", tags=["constitucion"])


class NameBody(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    country: str = Field("", max_length=80)


class GuideBody(BaseModel):
    country: str = Field(..., min_length=2, max_length=80)


class StepBody(BaseModel):
    done: bool


class Partner(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=160)
    documento: str = Field("", max_length=60)
    aporte: str = Field("", max_length=80)
    porcentaje: float | None = Field(None, ge=0, le=100)


class StatutesBody(BaseModel):
    pais: str = Field(..., min_length=2, max_length=80)
    tipo: str = Field(..., min_length=2, max_length=120)
    nombre: str = Field("", max_length=160)
    domicilio: str = Field("", max_length=160)
    objeto: str = Field("", max_length=2000)
    capital: str = Field("", max_length=120)
    administracion: str = Field("", max_length=500)
    socios: list[Partner] = Field(default_factory=list, max_length=20)


def _project(db: Session, company_id: str, user: User):
    company = get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return company, project


@router.post("/{company_id}/nombre")
async def check_name(company_id: str, body: NameBody, db: Session = Depends(get_db), user: User = Depends(llm_user),
                     llm: LLMAdapter = Depends(get_llm)):
    """¿Existe ya una empresa o marca con ese nombre? ¿Qué dominios están libres y a qué precio?"""
    company, project = _project(db, company_id, user)
    country = body.country or company.country or ""
    with usage_scope(db, company_id, level=3):
        name = await Constitucion(llm, db).check_name(body.name.strip(), country, company_context(db, project, company))
    return {**name, **await dominios.check(body.name)}


@router.post("/{company_id}/guia")
async def legal_guide(company_id: str, body: GuideBody, db: Session = Depends(get_db), user: User = Depends(llm_user),
                      llm: LLMAdapter = Depends(get_llm)):
    """La ruta legal completa en el país que el cliente eligió, explicada para quien no sabe nada."""
    company, project = _project(db, company_id, user)
    with usage_scope(db, company_id, level=3):
        guide = await Constitucion(llm, db).legal_guide(project, body.country.strip(), company_context(db, project, company))
    if not guide.get("pasos"):
        raise HTTPException(status_code=502, detail="No se pudo armar la ruta legal esta vez; intenta de nuevo en un momento.")
    return guide


@router.get("/{company_id}/guia")
def latest_guide(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _project(db, company_id, user)
    found = Constitucion(llm=None, db=db).latest_guide(project)  # type: ignore[arg-type]
    if not found:
        raise HTTPException(status_code=404, detail="Todavía no hay ruta legal")
    doc, guide = found
    return {"id": doc.id, **guide}


@router.post("/{company_id}/guia/pasos/{index}")
def mark_step(company_id: str, index: int, body: StepBody, db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    """El cliente marca un paso como hecho: la ruta muestra cuánto falta."""
    _, project = _project(db, company_id, user)
    try:
        return Constitucion(llm=None, db=db).mark_step(project, index, body.done)  # type: ignore[arg-type]
    except LookupError:
        raise HTTPException(status_code=404, detail="Todavía no hay ruta legal")
    except IndexError:
        raise HTTPException(status_code=404, detail="Ese paso no existe")


@router.post("/{company_id}/estatutos")
async def statutes(company_id: str, body: StatutesBody, db: Session = Depends(get_db), user: User = Depends(llm_user),
                   llm: LLMAdapter = Depends(get_llm)):
    """Borrador de estatutos según la ley del país, para revisar con un abogado."""
    company, project = _project(db, company_id, user)
    with usage_scope(db, company_id, level=3):
        doc = await Constitucion(llm, db).statutes(project, company, body.model_dump())
    return {"id": doc.id, "title": doc.title, "markdown": doc.content}


@router.get("/{company_id}/estatutos/{doc_id}.docx")
def statutes_docx(company_id: str, doc_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _project(db, company_id, user)
    doc = db.query(Document).filter(Document.id == doc_id, Document.project_id == project.id,
                                    Document.doc_type == "statutes").first()
    if not doc:
        raise HTTPException(status_code=404, detail="Esos estatutos no existen")
    return Response(markdown_to_docx(doc.content or "", doc.title),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": 'attachment; filename="estatutos.docx"'})
