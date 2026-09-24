"""Companies & Projects endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
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
    companies = db.query(Company).filter(
        Company.primary_user_id == user.id,
        Company.status == "active",
    ).all()
    return [CompanyResponse.model_validate(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse.model_validate(company)


@router.get("/{company_id}/project", response_model=ProjectResponse)
def get_project(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = db.query(Project).join(Company).filter(
        Project.company_id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)
