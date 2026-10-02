"""API de Onboarding (WO-108): /api/v1/onboarding/..."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core import privacy
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Consent, User
from app.onboarding import service
from app.twin import lifecycle

router = APIRouter(prefix="/onboarding", tags=["Onboarding (WO-108)"])


class StartBody(BaseModel):
    """Lo mínimo antes de la primera pregunta (AD-FUNC-06 §2): una señal de que hay Empresa o intención."""
    model_config = ConfigDict(extra="forbid")
    company_name: str = Field(..., min_length=1, max_length=255)
    stage: Literal["idea", "existing"] = "idea"


class ConsentBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    purpose: Literal["data_processing", "aggregated_intelligence"]
    granted: bool


@router.get("/me")
def me(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"identity": service.identity(db, user), "consents": service.current_consents(db, user),
            "next": service.next_step(db, user), "policy_version": privacy.POLICY_VERSION}


@router.post("/start", status_code=201)
def start(body: StartBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Nace la Empresa con lo mínimo y ADÁN hace su primera pregunta real (AD-FUNC-06 §1, §3)."""
    origin = {"onboarding": True, "stage": body.stage}
    company = lifecycle.birth(db, user, body.company_name.strip(), origin=origin)
    message = service.seed_first_question(db, user, company)
    db.commit()
    return {"company_id": company.id, "first_question": message.content if message else None}


@router.post("/consents")
def change_consent(body: ConsentBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Cambiar un consentimiento deja una constancia nueva; la anterior se conserva (Ley 1581)."""
    if body.purpose == privacy.DATA_PROCESSING and not body.granted:
        raise HTTPException(status_code=409, detail=(
            "Retirar el consentimiento de tratamiento de datos equivale a pedir la supresión de la cuenta: "
            "se tramita como solicitud de supresión, porque sin esos datos no se puede prestar el servicio."))
    db.add(Consent(user_id=user.id, purpose=body.purpose, granted=body.granted,
                   policy_version=privacy.POLICY_VERSION))
    db.commit()
    return service.current_consents(db, user)
