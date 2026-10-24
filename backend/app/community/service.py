"""Comunidad ADÁN: perfiles, vitrina de empresas con Sello ADÁN, conexiones y Selecciones Paradixe."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.community.models import (
    CONNECTION_KINDS, LOOKING_FOR, PROFILE_KINDS, STAGES, CommunityProfile, CompanyListing, Connection,
)
from app.core.config import settings
from app.models.models import Company, Document, Level, NivelStatus, Project, Score, ScoreType, User
from app.scoring import service as scoring
from app.services.gemelo_digital import GemeloDigitalService


def is_curator(user: User) -> bool:
    curators = {e.strip().lower() for e in settings.PARADIXE_CURATORS.split(",") if e.strip()}
    return user.email.lower() in curators


def _latest_json(db: Session, project: Project, doc_type: str) -> dict | None:
    doc = db.query(Document).filter(Document.project_id == project.id, Document.doc_type == doc_type) \
        .order_by(Document.created_at.desc()).first()
    try:
        return json.loads(doc.content) if doc and doc.content else None
    except ValueError:
        return None


def seal(db: Session, company: Company) -> dict:
    """El Sello ADÁN: lo que el Gemelo Digital sabe de la empresa, verificable y no editable por ella."""
    project = db.query(Project).filter(Project.company_id == company.id).first()
    if not project:
        return {}
    levels = db.query(Level).filter(Level.project_id == project.id).order_by(Level.number).all()
    closed = [lv.number for lv in levels if lv.status == NivelStatus.COMPLETED]
    active = next((lv for lv in levels if lv.status == NivelStatus.ACTIVE), None)
    problem = db.query(Score).filter(Score.project_id == project.id, Score.score_type == ScoreType.PROBLEM) \
        .order_by(Score.created_at.desc()).first()
    evidence = scoring.active_evidence(db, project, "problem")
    board = GemeloDigitalService(db).get_last_board_consensus(project) or {}
    arena = _latest_json(db, project, "arena") or {}
    guide = _latest_json(db, project, "legal_guide") or {}
    model = _latest_json(db, project, "financial_model") or {}
    kpis = (model.get("base") or {}).get("kpis") or {}
    return {
        "levels_closed": closed,
        "current_level": active.number if active else (max(closed) + 1 if closed and max(closed) < 7 else None),
        "current_level_name": active.name if active else "",
        "problem_score": round(problem.value) if problem else None,
        "problem_confidence": round(problem.confidence_level) if problem else None,
        "testimonies": sum(1 for e in evidence if e.kind == "testimony" and e.polarity != "contradicts"),
        "external_sources": sum(1 for e in evidence if e.kind == "external" and e.polarity != "contradicts"),
        "board_decision": board.get("decision"),
        "board_confidence": round(board["confidence"]) if isinstance(board.get("confidence"), (int, float)) else None,
        "arena_passed": arena.get("passed") if arena.get("phase") == "decided" else None,
        "legal_steps": [sum(1 for d in guide.get("done", []) if d), len(guide.get("pasos") or [])] if guide else None,
        "legal_country": guide.get("pais"),
        "breakeven_month": kpis.get("punto_equilibrio_mes"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def _clip(value, n: int) -> str:
    return str(value or "").strip()[:n]


class Community:
    def __init__(self, db: Session):
        self.db = db

    # --- perfiles ---

    def profile(self, user: User) -> CommunityProfile | None:
        return self.db.query(CommunityProfile).filter(CommunityProfile.user_id == user.id).first()

    def save_profile(self, user: User, data: dict) -> CommunityProfile:
        p = self.profile(user) or CommunityProfile(user_id=user.id, display_name=user.name)
        p.display_name = _clip(data.get("display_name") or user.name, 120)
        p.headline = _clip(data.get("headline"), 200)
        p.bio = _clip(data.get("bio"), 3000)
        p.kind = data.get("kind") if data.get("kind") in PROFILE_KINDS else "emprendedor"
        p.city, p.country = _clip(data.get("city"), 80), _clip(data.get("country"), 80)
        p.website, p.linkedin = _clip(data.get("website"), 300), _clip(data.get("linkedin"), 300)
        p.public = bool(data.get("public"))
        p.ticket_min_usd = data.get("ticket_min_usd") if p.kind == "inversionista" else None
        p.ticket_max_usd = data.get("ticket_max_usd") if p.kind == "inversionista" else None
        p.sectors = [_clip(s, 60) for s in (data.get("sectors") or [])][:10]
        p.stages = [s for s in (data.get("stages") or []) if s in STAGES]
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def people(self, kind: str = "", q: str = "") -> list[CommunityProfile]:
        query = self.db.query(CommunityProfile).filter(CommunityProfile.public.is_(True))
        if kind in PROFILE_KINDS:
            query = query.filter(CommunityProfile.kind == kind)
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(or_(CommunityProfile.display_name.ilike(like), CommunityProfile.headline.ilike(like),
                                     CommunityProfile.bio.ilike(like)))
        return query.order_by(CommunityProfile.updated_at.desc()).limit(100).all()

    # --- vitrina de empresas ---

    def publish(self, user: User, company: Company, data: dict) -> CompanyListing:
        listing = self.db.query(CompanyListing).filter(CompanyListing.company_id == company.id).first() \
            or CompanyListing(company_id=company.id, owner_id=user.id)
        listing.published = data.get("published", True) is not False
        listing.name = _clip(data.get("name") or company.name, 160)
        listing.tagline = _clip(data.get("tagline"), 200)
        listing.description = _clip(data.get("description") or company.description, 4000)
        listing.sector = _clip(data.get("sector") or company.industry, 120)
        listing.country = _clip(data.get("country") or company.country, 80)
        listing.city = _clip(data.get("city"), 80)
        listing.stage = data.get("stage") if data.get("stage") in STAGES else "idea"
        listing.looking_for = [x for x in (data.get("looking_for") or []) if x in LOOKING_FOR]
        amount = data.get("amount_sought_usd")
        listing.amount_sought_usd = float(amount) if isinstance(amount, (int, float)) and amount > 0 else None
        listing.website = _clip(data.get("website"), 300)
        listing.seal = seal(self.db, company)
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def refresh_seal(self, listing: CompanyListing) -> CompanyListing:
        company = self.db.get(Company, listing.company_id)
        if company:
            listing.seal = seal(self.db, company)
            self.db.commit()
        return listing

    def listings(self, sector: str = "", stage: str = "", looking_for: str = "", selection: bool = False,
                 q: str = "") -> list[CompanyListing]:
        query = self.db.query(CompanyListing).filter(CompanyListing.published.is_(True))
        if stage in STAGES:
            query = query.filter(CompanyListing.stage == stage)
        if sector:
            query = query.filter(CompanyListing.sector.ilike(f"%{sector.strip()}%"))
        if selection:
            query = query.filter(CompanyListing.paradixe_selection.is_(True))
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(or_(CompanyListing.name.ilike(like), CompanyListing.tagline.ilike(like),
                                     CompanyListing.description.ilike(like)))
        rows = query.order_by(CompanyListing.paradixe_selection.desc(), CompanyListing.updated_at.desc()).limit(200).all()
        return [r for r in rows if not looking_for or looking_for in (r.looking_for or [])]

    def select(self, curator: User, listing: CompanyListing, selected: bool, note: str) -> CompanyListing:
        listing.paradixe_selection = selected
        listing.selection_note = _clip(note, 2000) if selected else ""
        listing.selected_by = curator.id if selected else None
        self.db.commit()
        return listing

    # --- conexiones ---

    def connect(self, user: User, kind: str, message: str, listing: CompanyListing | None = None,
                to_user: User | None = None) -> Connection:
        if kind not in CONNECTION_KINDS:
            raise ValueError("Tipo de conexión no válido")
        target = listing.owner_id if listing else to_user.id if to_user else None
        if not target or target == user.id:
            raise ValueError("No puedes conectarte contigo mismo")
        existing = self.db.query(Connection).filter(Connection.from_user_id == user.id, Connection.to_user_id == target,
                                                    Connection.kind == kind,
                                                    Connection.listing_id == (listing.id if listing else None),
                                                    Connection.status != "rechazada").first()
        if existing:
            return existing
        conn = Connection(from_user_id=user.id, to_user_id=target, listing_id=listing.id if listing else None, kind=kind,
                          message=_clip(message, 2000), status="aceptada" if kind == "seguir" else "pendiente")
        self.db.add(conn)
        self.db.commit()
        self.db.refresh(conn)
        return conn

    def respond(self, user: User, conn: Connection, accept: bool) -> Connection:
        if conn.to_user_id != user.id:
            raise PermissionError("Esa solicitud no es para ti")
        conn.status = "aceptada" if accept else "rechazada"
        conn.responded_at = datetime.now(timezone.utc)
        self.db.commit()
        return conn

    def inbox(self, user: User) -> dict:
        received = self.db.query(Connection).filter(Connection.to_user_id == user.id).order_by(Connection.created_at.desc()).all()
        sent = self.db.query(Connection).filter(Connection.from_user_id == user.id).order_by(Connection.created_at.desc()).all()
        return {"received": received, "sent": sent}
