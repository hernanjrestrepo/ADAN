"""Companies & Projects endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.authz import get_owned_company, get_owned_project, owned_companies
from app.ai.usage import LLMUsage
from app.core.database import get_db
from app.models.models import Company, FoundingNarrative, Level, Project, User
from app.schemas.schemas import CompanyCreate, CompanyResponse, ProjectResponse

router = APIRouter(prefix="/companies", tags=["companies"])

LEVEL_NAMES = [
    "El Dolor",
    "Propuesta de Valor",
    "Plan de Negocios",
    "MVP",
    "Validación Simulada",
    "Lanzamiento",
    "Escalamiento",
]


@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(
    body: CompanyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    company = Company(
        name=body.name,
        description=body.description,
        industry=body.industry,
        country=body.country,
        created_by=user.id,
        primary_user_id=user.id,
    )
    db.add(company)
    db.flush()

    # Create founding narrative placeholder
    narrative = FoundingNarrative(company_id=company.id)
    db.add(narrative)

    # Create project (1:1 with company per AD-006 §4)
    project = Project(
        company_id=company.id,
        name=f"Proyecto {body.name}",
    )
    db.add(project)
    db.flush()

    # Create all 7 levels (Nivel 1 starts active, rest blocked)
    for i, name in enumerate(LEVEL_NAMES, 1):
        level = Level(
            project_id=project.id,
            number=i,
            name=name,
            status="active" if i == 1 else "blocked",
        )
        db.add(level)

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
