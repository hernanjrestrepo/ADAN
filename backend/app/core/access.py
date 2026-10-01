"""Control de acceso por empresa (aislamiento entre clientes, WO-093).

Toda entidad de negocio cuelga de una `Company`, cuyo dueño es
`Company.primary_user_id`. Un recurso ajeno responde 404 (no 403) para no
revelar que existe.
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Company, User


def require_company(db: Session, user: User, company_id: str) -> Company:
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


def require_organization(db: Session, user: User, organization_id: str):
    from app.oos.models import Organization

    org = (
        db.query(Organization)
        .join(Company, Company.id == Organization.company_id)
        .filter(Organization.id == organization_id, Company.primary_user_id == user.id)
        .first()
    )
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


def require_work_order(db: Session, user: User, work_order_id: str):
    from app.oos.models import Organization, WorkOrder

    wo = (
        db.query(WorkOrder)
        .join(Organization, Organization.id == WorkOrder.organization_id)
        .join(Company, Company.id == Organization.company_id)
        .filter(WorkOrder.id == work_order_id, Company.primary_user_id == user.id)
        .first()
    )
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    return wo
