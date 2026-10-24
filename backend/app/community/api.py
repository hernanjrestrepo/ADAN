"""Comunidad ADÁN: la red de empresas, emprendedores, inversionistas y mentores del ecosistema Paradixe."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.community.models import CommunityProfile, CompanyListing, Connection
from app.community.service import Community, is_curator
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.models.models import User

router = APIRouter(prefix="/comunidad", tags=["comunidad"])


class ProfileBody(BaseModel):
    display_name: str = Field("", max_length=120)
    headline: str = Field("", max_length=200)
    bio: str = Field("", max_length=3000)
    kind: str = "emprendedor"
    city: str = Field("", max_length=80)
    country: str = Field("", max_length=80)
    website: str = Field("", max_length=300)
    linkedin: str = Field("", max_length=300)
    public: bool = False
    ticket_min_usd: float | None = Field(None, ge=0)
    ticket_max_usd: float | None = Field(None, ge=0)
    sectors: list[str] = Field(default_factory=list, max_length=10)
    stages: list[str] = Field(default_factory=list, max_length=4)


class ListingBody(BaseModel):
    published: bool = True
    name: str = Field("", max_length=160)
    tagline: str = Field("", max_length=200)
    description: str = Field("", max_length=4000)
    sector: str = Field("", max_length=120)
    country: str = Field("", max_length=80)
    city: str = Field("", max_length=80)
    stage: str = "idea"
    looking_for: list[str] = Field(default_factory=list, max_length=6)
    amount_sought_usd: float | None = Field(None, ge=0)
    website: str = Field("", max_length=300)


class ConnectBody(BaseModel):
    kind: str
    message: str = Field("", max_length=2000)
    listing_id: str | None = None
    to_profile_id: str | None = None


class RespondBody(BaseModel):
    accept: bool


class SelectBody(BaseModel):
    selected: bool
    note: str = Field("", max_length=2000)


def profile_out(p: CommunityProfile) -> dict:
    return {k: getattr(p, k) for k in ("id", "display_name", "headline", "bio", "kind", "city", "country", "website",
                                        "linkedin", "public", "ticket_min_usd", "ticket_max_usd", "sectors", "stages")}


def listing_out(item: CompanyListing, viewer: User | None = None) -> dict:
    return {**{k: getattr(item, k) for k in ("id", "company_id", "published", "name", "tagline", "description", "sector",
                                              "country", "city", "stage", "looking_for", "amount_sought_usd", "website",
                                              "seal", "paradixe_selection", "selection_note")},
            "mine": bool(viewer and item.owner_id == viewer.id)}


def connection_out(db: Session, c: Connection, viewer: User) -> dict:
    other_id = c.to_user_id if c.from_user_id == viewer.id else c.from_user_id
    other = db.get(User, other_id)
    profile = db.query(CommunityProfile).filter(CommunityProfile.user_id == other_id).first()
    listing = db.get(CompanyListing, c.listing_id) if c.listing_id else None
    return {"id": c.id, "kind": c.kind, "message": c.message, "status": c.status, "created_at": c.created_at,
            "direction": "sent" if c.from_user_id == viewer.id else "received",
            "other_name": profile.display_name if profile else (other.name if other else ""),
            "other_headline": profile.headline if profile else "",
            "listing_name": listing.name if listing else None,
            # El correo solo se comparte cuando la solicitud se aceptó (mínimo dato, Ley 1581)
            "other_email": other.email if other and c.status == "aceptada" and c.kind != "seguir" else None}


@router.get("/perfil")
def my_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = Community(db).profile(user)
    return {**(profile_out(p) if p else {"display_name": user.name, "public": False, "kind": "emprendedor"}),
            "is_curator": is_curator(user)}


@router.put("/perfil")
def save_profile(body: ProfileBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return profile_out(Community(db).save_profile(user, body.model_dump()))


@router.get("/personas")
def people(kind: str = "", q: str = "", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [profile_out(p) for p in Community(db).people(kind, q)]


@router.get("/empresas")
def listings(sector: str = "", stage: str = "", looking_for: str = "", seleccion: bool = False, q: str = "",
             db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [listing_out(x, user) for x in Community(db).listings(sector, stage, looking_for, seleccion, q)]


@router.get("/empresas/{listing_id}")
def listing(listing_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(CompanyListing, listing_id)
    if not item or (not item.published and item.owner_id != user.id):
        raise HTTPException(status_code=404, detail="Esa empresa no está publicada")
    return listing_out(item, user)


@router.get("/mis-empresas/{company_id}")
def my_listing(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_owned_company(db, company_id, user)
    item = db.query(CompanyListing).filter(CompanyListing.company_id == company_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Todavía no publicaste esta empresa")
    return listing_out(Community(db).refresh_seal(item), user)


@router.put("/mis-empresas/{company_id}")
def publish(company_id: str, body: ListingBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Publicar (o actualizar) la vitrina de una empresa propia; el Sello ADÁN se recalcula del Gemelo Digital."""
    company = get_owned_company(db, company_id, user)
    return listing_out(Community(db).publish(user, company, body.model_dump()), user)


@router.post("/empresas/{listing_id}/seleccion")
def select(listing_id: str, body: SelectBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Selección Paradixe: solo los curadores de Paradixe (PARADIXE_CURATORS)."""
    if not is_curator(user):
        raise HTTPException(status_code=403, detail="Solo los curadores de Paradixe hacen Selecciones")
    item = db.get(CompanyListing, listing_id)
    if not item:
        raise HTTPException(status_code=404, detail="Esa empresa no está publicada")
    return listing_out(Community(db).select(user, item, body.selected, body.note), user)


@router.post("/conexiones", status_code=201)
def connect(body: ConnectBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(CompanyListing, body.listing_id) if body.listing_id else None
    profile = db.get(CommunityProfile, body.to_profile_id) if body.to_profile_id else None
    if body.listing_id and (not item or not item.published):
        raise HTTPException(status_code=404, detail="Esa empresa no está publicada")
    if body.to_profile_id and (not profile or not profile.public):
        raise HTTPException(status_code=404, detail="Ese perfil no es público")
    to_user = db.get(User, profile.user_id) if profile else None
    try:
        conn = Community(db).connect(user, body.kind, body.message, item, to_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return connection_out(db, conn, user)


@router.get("/conexiones")
def inbox(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    box = Community(db).inbox(user)
    return {k: [connection_out(db, c, user) for c in v] for k, v in box.items()}


@router.post("/conexiones/{connection_id}/responder")
def respond(connection_id: str, body: RespondBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conn = db.get(Connection, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Esa solicitud no existe")
    try:
        return connection_out(db, Community(db).respond(user, conn, body.accept), user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
