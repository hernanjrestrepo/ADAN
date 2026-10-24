"""Consola de Paradixe (superadministradores): ver y controlar ADÁN. Usuarios, empresas, @pples, compras, Niveles
pagados y la red; regalar @pples para pruebas, soporte o campañas. Todo regalo queda escrito con quién y por qué."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.apples import gateway, pricing, service
from app.apples.models import AppleMovement, ApplePurchase, LevelUnlock, ReferralProfile
from app.core.authz import require_superadmin
from app.core.config import settings
from app.core.database import get_db
from app.models.models import Company, User

router = APIRouter(prefix="/admin", tags=["consola Paradixe"])


class GiftBody(BaseModel):
    apples: int = Field(..., ge=1, le=10000)
    reason: str = Field("", max_length=120)


def _sum(db: Session, *filters) -> float:
    return float(db.query(func.coalesce(func.sum(AppleMovement.amount), 0)).filter(*filters).scalar() or 0)


@router.get("/resumen")
def summary(db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    since = datetime.now(timezone.utc) - timedelta(days=30)
    approved = db.query(ApplePurchase).filter(ApplePurchase.status == "aprobada")
    unlocks = db.query(LevelUnlock.level_number, func.count()).group_by(LevelUnlock.level_number).all()
    by_level = {n: c for n, c in unlocks}
    level_rows = []
    for n in range(1, 8):
        p = pricing.level_price(n)
        count = by_level.get(n, 0)
        level_rows.append({"level": n, "name": p.name, "apples": p.apples, "paid": count,
                           "revenue": count * p.apples, "cost": round(count * p.cost_usd, 2)})
    revenue_levels = sum(r["revenue"] for r in level_rows)
    cost_levels = sum(r["cost"] for r in level_rows)
    return {
        "users": db.query(User).count(),
        "users_30d": db.query(User).filter(User.created_at >= since.replace(tzinfo=None)).count(),
        "companies": db.query(Company).count(),
        "referred_users": db.query(ReferralProfile).filter(ReferralProfile.sponsor_id.isnot(None)).count(),
        "purchases": approved.count(),
        "purchases_cop": int(approved.with_entities(func.coalesce(func.sum(ApplePurchase.amount_cop), 0)).scalar() or 0),
        "apples_sold": int(approved.with_entities(func.coalesce(func.sum(ApplePurchase.apples), 0)).scalar() or 0),
        "apples_gifted": _sum(db, AppleMovement.kind.in_(("regalo", "bienvenida"))),
        "apples_referral": _sum(db, AppleMovement.kind == "referido"),
        "apples_in_wallets": _sum(db),
        "levels": level_rows,
        "levels_revenue": revenue_levels,
        "levels_cost": round(cost_levels, 2),
        "levels_margin": round(1 - cost_levels / revenue_levels, 4) if revenue_levels else None,
        "config": {"provider": gateway.provider(), "live": settings.PAYMENTS_LIVE, "required": settings.APPLES_REQUIRED,
                   "welcome_referral": settings.APPLES_WELCOME_REFERRAL, "trm": settings.APPLE_TRM},
    }


@router.get("/usuarios")
def users(q: str = "", db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    query = db.query(User)
    if q.strip():
        like = f"%{q.strip().lower()}%"
        query = query.filter(or_(func.lower(User.email).like(like), func.lower(User.name).like(like)))
    rows = query.order_by(User.created_at.desc()).limit(100).all()
    out = []
    for u in rows:
        prof = db.get(ReferralProfile, u.id)
        sponsor = db.get(User, prof.sponsor_id) if prof and prof.sponsor_id else None
        out.append({
            "id": u.id, "name": u.name, "email": u.email, "created_at": u.created_at.isoformat() if u.created_at else None,
            "balance": float(service.balance(db, u.id)), "gift_balance": float(service.gift_balance(db, u.id)),
            "companies": db.query(Company).filter(Company.primary_user_id == u.id).count(),
            "levels_paid": db.query(LevelUnlock).filter(LevelUnlock.user_id == u.id).count(),
            "purchased_cop": int(db.query(func.coalesce(func.sum(ApplePurchase.amount_cop), 0)).filter(
                ApplePurchase.user_id == u.id, ApplePurchase.status == "aprobada").scalar() or 0),
            "code": prof.code if prof else None, "sponsor": sponsor.email if sponsor else None,
            "invited": db.query(ReferralProfile).filter(ReferralProfile.sponsor_id == u.id).count(),
        })
    return out


@router.post("/usuarios/{user_id}/regalo", status_code=201)
def gift(user_id: str, body: GiftBody, db: Session = Depends(get_db), admin: User = Depends(require_superadmin)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    try:
        service.gift(db, admin, target, body.apples, body.reason)
    except service.AppleError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"balance": float(service.balance(db, target.id))}


@router.get("/compras")
def purchases(db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    rows = db.query(ApplePurchase, User).join(User, User.id == ApplePurchase.user_id) \
        .order_by(ApplePurchase.created_at.desc()).limit(100).all()
    return [{**service.purchase_view(p), "email": u.email, "external_id": p.external_id,
             "resolved_at": p.resolved_at.isoformat() if p.resolved_at else None} for p, u in rows]


@router.get("/movimientos")
def movements(db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    rows = db.query(AppleMovement, User).join(User, User.id == AppleMovement.user_id) \
        .order_by(AppleMovement.created_at.desc()).limit(150).all()
    return [{"id": m.id, "email": u.email, "kind": m.kind, "amount": float(m.amount), "detail": m.detail,
             "created_at": m.created_at.isoformat()} for m, u in rows]


@router.get("/empresas")
def companies(db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    rows = db.query(Company, User).join(User, User.id == Company.primary_user_id) \
        .order_by(Company.created_at.desc()).limit(150).all()
    out = []
    for c, u in rows:
        paid = [lu.level_number for lu in db.query(LevelUnlock).filter(LevelUnlock.company_id == c.id).all()]
        out.append({"id": c.id, "name": c.name, "owner": u.email, "status": str(getattr(c.status, "value", c.status)),
                    "stage": c.origin_stage, "created_at": c.created_at.isoformat(), "levels_paid": sorted(paid)})
    return out
