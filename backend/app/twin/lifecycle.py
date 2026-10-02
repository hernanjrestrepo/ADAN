"""Ciclo de vida del Gemelo Digital (AD-CMP-06) — WO-098.

- **Nace** con su Empresa y su Proyecto (y su Workspace): los tres juntos (§1).
- **Crece** solo: cada cambio es una versión (app/twin/hooks.py), no hay mecanismo aparte (§2).
- **Cambia** con una Reinvención (Ley 9): cambia la Narrativa Fundacional, no el Gemelo,
  que conserva su identidad e historial (§3).
- **Se divide** cuando una Iniciativa se separa como Empresa nueva: Gemelo nuevo que hereda
  *por referencia* (linaje), y la Iniciativa queda marcada "separada hacia" (§4).
- **Se fusiona**: Gemelo nuevo, los originales se archivan y quedan referenciados (§5).
- **Se archiva** y sigue siendo consultable para siempre; nunca se borra (§6).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.models import Company, EntityStatus, Event, FoundingNarrative, Level, Project, User
from app.twin.actor import Actor, acting_as, current_actor, current_reason
from app.twin.models import CompanyInitiative, PatternA, TwinLineage, Workspace

LEVEL_NAMES = [
    "El Dolor", "Propuesta de Valor", "Plan de Negocios", "MVP", "Validación Simulada", "Lanzamiento",
    "Escalamiento",
]


class LifecycleError(ValueError):
    """La operación de ciclo de vida no es válida en el estado actual del Gemelo."""


def _event(db: Session, company: Company, project: Project | None, event_type: str, data: dict) -> None:
    actor = current_actor()
    db.add(Event(project_id=project.id if project else None, company_id=company.id, event_type=event_type,
                 entity_type="companies", entity_id=company.id, data={"label": company.name, **data},
                 category="domain", actor_type=actor.kind, actor_id=actor.id or actor.label))


def project_of(db: Session, company: Company) -> Project | None:
    return db.query(Project).filter(Project.company_id == company.id).first()


def ensure_writable(company: Company) -> None:
    """Un Gemelo archivado es de solo lectura (AD-CMP-06 §6)."""
    if _status(company) == EntityStatus.ARCHIVED.value:
        raise LifecycleError("El Gemelo está archivado: se puede consultar, no modificar")


def _status(company: Company) -> str:
    return company.status.value if hasattr(company.status, "value") else company.status


def birth(db: Session, user: User, name: str, description: str | None = None, industry: str | None = None,
          country: str | None = None, origin: dict | None = None) -> Company:
    """Nace un Gemelo: Empresa + Narrativa + Proyecto + Workspace + 7 Niveles (§1)."""
    actor = current_actor()
    if actor.kind != "user":
        actor = Actor.user(user.id, user.name)
    with acting_as(actor, reason=current_reason()):
        company = Company(name=name, description=description, industry=industry, country=country,
                          created_by=user.id, primary_user_id=user.id)
        db.add(company)
        db.flush()
        db.add(FoundingNarrative(company_id=company.id))
        project = Project(company_id=company.id, name=f"Proyecto {name}")
        db.add(project)
        db.flush()
        db.add(Workspace(project_id=project.id, company_id=company.id))
        for number, level_name in enumerate(LEVEL_NAMES, 1):
            db.add(Level(project_id=project.id, number=number, name=level_name,
                         status="active" if number == 1 else "blocked"))
        _event(db, company, project, "twin_born", origin or {})
        db.flush()
    return company


def reinvent(db: Session, company: Company, user: User, origin_story: str, reason: str,
             founding_motivation: str | None = None, irreversible_commitment: str | None = None) -> Company:
    """Reinvención (Ley 9): nueva Narrativa Fundacional, mismo Gemelo e historial (§3)."""
    ensure_writable(company)
    if not reason or len(reason.strip()) < 10:
        raise LifecycleError("Una reinvención exige explicar qué aprendizaje la motiva")
    with acting_as(Actor.user(user.id, user.name), reason=reason):
        narrative = db.query(FoundingNarrative).filter(FoundingNarrative.company_id == company.id).first()
        if narrative is None:
            narrative = FoundingNarrative(company_id=company.id)
            db.add(narrative)
        before = narrative.origin_story
        narrative.origin_story = origin_story
        if founding_motivation is not None:
            narrative.founding_motivation = founding_motivation
        if irreversible_commitment is not None:
            narrative.irreversible_commitment = irreversible_commitment
        company.founding_narrative = origin_story
        _event(db, company, project_of(db, company), "twin_reinvented",
               {"reason": reason, "previous_origin_story": before})
        db.commit()
    return company


def split(db: Session, company: Company, user: User, initiative_id: str, name: str, reason: str,
          description: str | None = None) -> Company:
    """División (§4): la Iniciativa se separa como Empresa nueva, con herencia por referencia."""
    ensure_writable(company)
    initiative = db.query(CompanyInitiative).filter(
        CompanyInitiative.id == initiative_id, CompanyInitiative.company_id == company.id).first()
    if initiative is None:
        raise LifecycleError("La Iniciativa no existe en este Gemelo")
    if initiative.spun_off_company_id:
        raise LifecycleError("La Iniciativa ya se separó como otra Empresa")
    if initiative.state not in (PatternA.APPROVED, PatternA.EXECUTED):
        raise LifecycleError("Solo se separa una Iniciativa aprobada por el cliente (Patrón A)")

    with acting_as(Actor.user(user.id, user.name), reason=reason):
        child = birth(db, user, name, description or initiative.objective, company.industry, company.country,
                      origin={"split_from": company.id, "initiative_id": initiative.id})
        db.add(TwinLineage(company_id=child.id, source_company_id=company.id, relation="split_from",
                           initiative_id=initiative.id, note=reason, actor_type="user", actor_id=user.id))
        initiative.spun_off_company_id = child.id
        _event(db, company, project_of(db, company), "twin_split",
               {"child_company_id": child.id, "initiative_id": initiative.id, "reason": reason})
        db.commit()
    return child


def merge(db: Session, companies: list[Company], user: User, name: str, reason: str,
          description: str | None = None) -> Company:
    """Fusión (§5): Gemelo nuevo; los originales se archivan y quedan referenciados."""
    if len({c.id for c in companies}) < 2:
        raise LifecycleError("Una fusión necesita al menos dos Empresas distintas")
    for company in companies:
        ensure_writable(company)
    with acting_as(Actor.user(user.id, user.name), reason=reason):
        merged = birth(db, user, name, description, companies[0].industry, companies[0].country,
                       origin={"merged_from": [c.id for c in companies]})
        for company in companies:
            db.add(TwinLineage(company_id=merged.id, source_company_id=company.id, relation="merged_from",
                               note=reason, actor_type="user", actor_id=user.id))
            _archive(db, company, reason, merged_into=merged.id)
        db.commit()
    return merged


def _archive(db: Session, company: Company, reason: str, merged_into: str | None = None) -> None:
    project = project_of(db, company)
    company.status = EntityStatus.ARCHIVED
    if project is not None and project.status != EntityStatus.ARCHIVED:
        project.status = EntityStatus.ARCHIVED
    workspace = db.query(Workspace).filter(Workspace.company_id == company.id).first()
    if workspace is not None and workspace.status != "archived":
        workspace.status = "archived"
    _event(db, company, project, "twin_archived", {"reason": reason, **({"merged_into": merged_into}
                                                                        if merged_into else {})})


def archive(db: Session, company: Company, user: User, reason: str) -> Company:
    """Archivo (§6, Ley 8): queda consultable para siempre, nunca se borra."""
    ensure_writable(company)
    with acting_as(Actor.user(user.id, user.name), reason=reason):
        _archive(db, company, reason)
        db.commit()
    return company


def pause(db: Session, company: Company, user: User, reason: str | None = None) -> Company:
    ensure_writable(company)
    with acting_as(Actor.user(user.id, user.name), reason=reason):
        company.status = EntityStatus.PAUSED
        project = project_of(db, company)
        if project is not None and project.status == EntityStatus.ACTIVE:
            project.status = EntityStatus.PAUSED
        _event(db, company, project, "twin_paused", {"reason": reason})
        db.commit()
    return company


def resume(db: Session, company: Company, user: User, reason: str | None = None) -> Company:
    if _status(company) != EntityStatus.PAUSED.value:
        raise LifecycleError("Solo se reanuda un Gemelo pausado")
    with acting_as(Actor.user(user.id, user.name), reason=reason):
        company.status = EntityStatus.ACTIVE
        project = project_of(db, company)
        if project is not None and project.status == EntityStatus.PAUSED:
            project.status = EntityStatus.ACTIVE
        _event(db, company, project, "twin_resumed", {"reason": reason})
        db.commit()
    return company
