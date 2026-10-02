"""Companies & Projects endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.authz import get_owned_company, get_owned_project, owned_companies
from app.ai.usage import LLMUsage
from app.core.database import get_db
from app.onboarding.service import seed_first_question
from app.twin import lifecycle
from app.models.models import Company, User
from app.schemas.schemas import CompanyCreate, CompanyResponse, ProjectResponse

router = APIRouter(prefix="/companies", tags=["companies"])



@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(
    body: CompanyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Nace el Gemelo: Empresa, Narrativa Fundacional, Proyecto, Workspace y 7 Niveles (AD-CMP-06 §1)
    company = lifecycle.birth(db, user, body.name, body.description, body.industry, body.country)
    # ADÁN hace la primera pregunta real del Nivel 1 sin esperar a que el cliente escriba (AD-FUNC-06)
    seed_first_question(db, user, company)
    db.commit()
    db.refresh(company)
    return CompanyResponse.model_validate(company)


@router.get("/", response_model=list[CompanyResponse])
def list_companies(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    companies = owned_companies(db, user).filter(Company.status == "active").all()
    return [CompanyResponse.model_validate(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    company = get_owned_company(db, company_id, user)
    return CompanyResponse.model_validate(company)


@router.get("/{company_id}/project", response_model=ProjectResponse)
def get_project(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = get_owned_project(db, company_id, user)
    return ProjectResponse.model_validate(project)


@router.get("/{company_id}/llm-usage")
def get_llm_usage(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Costo de IA de la empresa: total, por Nivel y por modelo (WO-099, AD-IA-03)."""
    get_owned_company(db, company_id, user)
    rows = db.query(LLMUsage).filter(LLMUsage.company_id == company_id).all()

    def summarize(key):
        groups: dict = {}
        for r in rows:
            g = groups.setdefault(str(key(r)), {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0})
            g["calls"] += 1
            g["input_tokens"] += r.input_tokens
            g["output_tokens"] += r.output_tokens
            g["cost_usd"] = round(g["cost_usd"] + r.cost_usd, 6)
        return groups

    return {
        "calls": len(rows),
        "cost_usd": round(sum(r.cost_usd for r in rows), 6),
        "degraded_calls": sum(1 for r in rows if r.degraded),
        "by_level": summarize(lambda r: r.level_number),
        "by_model": summarize(lambda r: f"{r.provider}:{r.model}"),
    }


# Vista de Nivel y Cards (AD-UX-05 vía AD-FUNC-01; WO-108)
LEVEL_GUIDE = {
    1: ("Si el problema es real, urgente y le duele a más personas que a ti, validado con evidencia externa",
        "Diagnóstico del Dolor", "problem"),
    2: ("Cómo se diferencia tu propuesta de las alternativas y qué tan defendible es", "Propuesta de Valor",
        "solution"),
    3: ("Estructura legal y tributaria, proyecciones financieras contrastadas y marketing con costos reales",
        "Plan de Negocios", "business"),
    4: ("Qué construir exactamente para tu MVP", "Blueprint del MVP", "product"),
    5: ("Cómo reaccionarían clientes e inversionistas simulados ante tu MVP", "Informe de Validación", "market"),
    6: ("Cómo se comporta la empresa en el mundo real: primeros clientes, ingresos y gastos",
        "Primeros resultados reales", "venture"),
    7: ("Patrones de crecimiento y cuellos de botella para escalar", "Plan de Escalamiento", "venture"),
}


@router.get("/{company_id}/levels")
def levels(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Los 7 Niveles con su estado, su entregable, sus Cards y el último Score que los acompaña."""
    from app.models.models import Card, Level, Score

    project = get_owned_project(db, company_id, user)
    latest: dict[str, Score] = {}
    for s in db.query(Score).filter(Score.project_id == project.id).order_by(Score.created_at).all():
        latest[s.score_type.value] = s
    cards_by_level: dict[str, list[Card]] = {}
    for card in db.query(Card).filter(Card.project_id == project.id).order_by(Card.created_at).all():
        cards_by_level.setdefault(card.level_id, []).append(card)
    out = []
    for level in db.query(Level).filter(Level.project_id == project.id).order_by(Level.number).all():
        discovers, deliverable, score_key = LEVEL_GUIDE.get(level.number, ("", "", None))
        score = latest.get(score_key) if score_key else None
        out.append({
            "id": level.id, "number": level.number, "name": level.name, "status": level.status.value,
            "completed_at": level.completed_at.isoformat() if level.completed_at else None,
            "discovers": discovers, "deliverable": deliverable, "score_key": score_key,
            "score": None if score is None else {"value": score.value, "confidence": score.confidence_level},
            "cards": [{"id": c.id, "title": c.title, "description": c.description, "card_type": c.card_type,
                       "status": c.status.value} for c in cards_by_level.get(level.id, [])],
        })
    return out
