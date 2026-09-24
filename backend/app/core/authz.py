"""Autorización centralizada (WO-097).

Única definición de "a qué tiene acceso un usuario": hoy, a las empresas de las que es
Usuario Principal y a todo lo que cuelga de ellas. Cuando haya miembros por empresa, se
cambia aquí y no en cada router. Todo recurso ajeno responde 404 (no se revela que existe).
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Query, Session

from app.models.models import Company, Project, User


def owned_companies(db: Session, user: User) -> Query:
    """Consulta de las empresas a las que el usuario tiene acceso."""
    return db.query(Company).filter(Company.primary_user_id == user.id)


def get_owned_company(db: Session, company_id: str, user: User) -> Company:
    company = owned_companies(db, user).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return company


def get_owned_project(db: Session, company_id: str, user: User) -> Project:
    """El proyecto de una empresa del usuario."""
    project = (
        db.query(Project)
        .join(Company, Company.id == Project.company_id)
        .filter(Project.company_id == company_id, Company.primary_user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


def get_owned_organization(db: Session, organization_id: str, user: User):
    """Una organización del OOS que pertenece a una empresa del usuario."""
    from app.oos.models import Organization

    org = (
        db.query(Organization)
        .join(Company, Company.id == Organization.company_id)
        .filter(Organization.id == organization_id, Company.primary_user_id == user.id)
        .first()
    )
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    return org


def get_owned_work_order(db: Session, work_order_id: str, user: User):
    """Una Work Order del OOS que pertenece a una organización del usuario."""
    from app.oos.models import Organization, WorkOrder

    wo = (
        db.query(WorkOrder)
        .join(Organization, Organization.id == WorkOrder.organization_id)
        .join(Company, Company.id == Organization.company_id)
        .filter(WorkOrder.id == work_order_id, Company.primary_user_id == user.id)
        .first()
    )
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order no encontrada")
    return wo
