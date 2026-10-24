"""Billetera de @pples, cobro de Niveles y la red de referidos.

Referidos (decisión de Hernán, 2026-10-24): 7 niveles hacia arriba, el nivel 1 es quien invitó directamente ("el
papá"), 0,5 % por nivel = 3,5 %. Se paga en @pples sobre consumo real (cuando se paga un Nivel), nunca por inscribir
a alguien (Ley 1700 de 2013). Si la cadena es más corta, lo que no se reparte queda en Paradixe.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from decimal import ROUND_DOWN, Decimal

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.apples import gateway, pricing
from app.apples.models import AppleMovement, ApplePurchase, LevelUnlock, ReferralProfile
from app.core.config import settings
from app.models.models import Company, User

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
MIN_PURCHASE, MAX_PURCHASE = 5, 5000
PACKS = [25, 60, 120, 360]


class AppleError(ValueError):
    pass


def _q(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_DOWN)


# ---------- Red de referidos ----------

def _new_code(db: Session) -> str:
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(6))
        if not db.query(ReferralProfile).filter(ReferralProfile.code == code).first():
            return code


def ensure_profile(db: Session, user: User, sponsor_code: str | None = None) -> ReferralProfile:
    """La cuenta de referidos nace con la cuenta. El patrocinador solo se fija la primera vez."""
    prof = db.get(ReferralProfile, user.id)
    if prof:
        return prof
    sponsor = None
    if sponsor_code:
        sponsor = db.query(ReferralProfile).filter(ReferralProfile.code == sponsor_code.strip().upper()).first()
    prof = ReferralProfile(user_id=user.id, code=_new_code(db),
                           sponsor_id=sponsor.user_id if sponsor and sponsor.user_id != user.id else None)
    db.add(prof)
    db.flush()
    if prof.sponsor_id and settings.APPLES_WELCOME_REFERRAL > 0:
        # Regalo a quien llega invitado (no a quien invita: inscribir no paga), solo para usar en ADÁN
        _move(db, user.id, "bienvenida", settings.APPLES_WELCOME_REFERRAL, f"bienvenida:{user.id}",
              "Regalo de bienvenida por llegar con un enlace de invitación")
    return prof


def upline(db: Session, user_id: str) -> list[str]:
    """Quienes están por encima: [nivel 1 (quien invitó), nivel 2, …] hasta 7, sin ciclos."""
    chain: list[str] = []
    current = db.get(ReferralProfile, user_id)
    while current and current.sponsor_id and len(chain) < pricing.REFERRAL_DEPTH:
        if current.sponsor_id in chain or current.sponsor_id == user_id:
            break
        chain.append(current.sponsor_id)
        current = db.get(ReferralProfile, current.sponsor_id)
    return chain


def network(db: Session, user: User) -> dict:
    prof = ensure_profile(db, user)
    levels = []
    frontier = [user.id]
    for depth in range(1, pricing.REFERRAL_DEPTH + 1):
        frontier = [p.user_id for p in db.query(ReferralProfile).filter(ReferralProfile.sponsor_id.in_(frontier)).all()] \
            if frontier else []
        earned = db.query(func.coalesce(func.sum(AppleMovement.amount), 0)).filter(
            AppleMovement.user_id == user.id, AppleMovement.kind == "referido", AppleMovement.depth == depth).scalar()
        levels.append({"depth": depth, "people": len(frontier), "earned": float(earned or 0)})
    sponsor = db.get(User, prof.sponsor_id) if prof.sponsor_id else None
    return {"code": prof.code, "link": f"{settings.PUBLIC_URL}/register?ref={prof.code}",
            "sponsor": sponsor.name if sponsor else None, "levels": levels,
            "rate_per_level": pricing.REFERRAL_RATE, "depth": pricing.REFERRAL_DEPTH,
            "total_earned": round(sum(lv["earned"] for lv in levels), 3)}


# ---------- Billetera ----------

GIFT_KINDS = ("bienvenida", "regalo", "nivel_bono")


def gift_balance(db: Session, user_id: str) -> Decimal:
    """Lo que queda de @pples regaladas (bienvenida y regalos de Paradixe): se gastan primero y no generan comisión."""
    total = db.query(func.coalesce(func.sum(AppleMovement.amount), 0)).filter(
        AppleMovement.user_id == user_id, AppleMovement.kind.in_(GIFT_KINDS)).scalar()
    return max(_q(total or 0), Decimal("0"))


def gift(db: Session, admin: User, user: User, apples: int, reason: str) -> AppleMovement:
    """Un superadministrador regala @pples (pruebas, soporte, campañas). Queda escrito quién y por qué."""
    if not 1 <= apples <= 10000:
        raise AppleError("Se regalan entre 1 y 10.000 @pples por vez.")
    ensure_profile(db, user)
    m = _move(db, user.id, "regalo", apples, f"regalo:{secrets.token_hex(8)}",
              f"Regalo de Paradixe ({admin.email}): {reason or 'pruebas'}")
    db.commit()
    return m


def balance(db: Session, user_id: str) -> Decimal:
    total = db.query(func.coalesce(func.sum(AppleMovement.amount), 0)).filter(AppleMovement.user_id == user_id).scalar()
    return _q(total or 0)


def movements(db: Session, user_id: str, limit: int = 50) -> list[dict]:
    rows = (db.query(AppleMovement).filter(AppleMovement.user_id == user_id)
            .order_by(AppleMovement.created_at.desc()).limit(limit).all())
    return [{"id": m.id, "kind": m.kind, "amount": float(m.amount), "detail": m.detail, "level": m.level_number,
             "depth": m.depth, "created_at": m.created_at.isoformat()} for m in rows]


def _move(db: Session, user_id: str, kind: str, amount, reference: str, detail: str, **extra) -> AppleMovement | None:
    """Escribe un movimiento una sola vez (idempotente por tipo + referencia + persona)."""
    exists = db.query(AppleMovement).filter(AppleMovement.kind == kind, AppleMovement.reference == reference,
                                            AppleMovement.user_id == user_id).first()
    if exists:
        return None
    m = AppleMovement(user_id=user_id, kind=kind, amount=_q(amount), reference=reference, detail=detail[:200], **extra)
    db.add(m)
    db.flush()
    return m


# ---------- Compras con dinero real ----------

def amount_cop(apples: int) -> int:
    return apples * settings.APPLE_TRM


def create_purchase(db: Session, user: User, apples: int) -> ApplePurchase:
    if not MIN_PURCHASE <= apples <= MAX_PURCHASE:
        raise AppleError(f"Puedes comprar entre {MIN_PURCHASE} y {MAX_PURCHASE} @pples por compra.")
    ensure_profile(db, user)
    p = ApplePurchase(user_id=user.id, apples=apples, amount_cop=amount_cop(apples), trm=settings.APPLE_TRM,
                      provider=gateway.provider())
    db.add(p)
    db.flush()
    try:
        p.checkout_url = gateway.checkout_url(p.id, p.amount_cop, f"{settings.PUBLIC_URL}/apples?compra={p.id}")
    except gateway.GatewayError as exc:
        db.rollback()
        raise AppleError(str(exc)) from exc
    db.commit()
    return p


def resolve_purchase(db: Session, purchase: ApplePurchase, status: str, external_id: str | None = None) -> ApplePurchase:
    """Aplica el resultado de la pasarela. Acreditar es idempotente: un webhook repetido no duplica @pples."""
    if purchase.status != "pendiente" or status == "pendiente":
        return purchase
    purchase.status = status
    purchase.external_id = external_id or purchase.external_id
    purchase.resolved_at = datetime.now(timezone.utc)
    if status == "aprobada":
        _move(db, purchase.user_id, "compra", purchase.apples, purchase.id,
              f"Compra de {purchase.apples} @pples ({purchase.provider})")
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    db.refresh(purchase)
    return purchase


def purchase_view(p: ApplePurchase) -> dict:
    return {"id": p.id, "apples": p.apples, "amount_cop": p.amount_cop, "provider": p.provider, "status": p.status,
            "checkout_url": p.checkout_url, "created_at": p.created_at.isoformat()}


# ---------- Niveles ----------

def levels_for(db: Session, company: Company) -> list[dict]:
    paid = {u.level_number: u for u in db.query(LevelUnlock).filter(LevelUnlock.company_id == company.id).all()}
    return [{"level": n, "name": pricing.LEVEL_NAMES[n], "apples": pricing.apples_for(n), "paid": n in paid,
             "paid_at": paid[n].created_at.isoformat() if n in paid else None} for n in range(1, 8)]


def is_unlocked(db: Session, company_id: str, level: int) -> bool:
    if not settings.APPLES_REQUIRED:
        return True
    return db.query(LevelUnlock).filter(LevelUnlock.company_id == company_id, LevelUnlock.level_number == level).first() \
        is not None


def unlock_level(db: Session, user: User, company: Company, level: int) -> dict:
    if level not in pricing.LEVEL_NAMES:
        raise AppleError("Ese Nivel no existe.")
    if db.query(LevelUnlock).filter(LevelUnlock.company_id == company.id, LevelUnlock.level_number == level).first():
        raise AppleError("Ese Nivel ya está pagado.")
    price = pricing.apples_for(level)
    if balance(db, user.id) < price:
        raise AppleError(f"Te faltan @pples: el Nivel {level} cuesta {price} y tienes {balance(db, user.id)}.")
    reference = f"{company.id}:{level}"
    db.add(LevelUnlock(company_id=company.id, level_number=level, user_id=user.id, apples=price))
    from_gift = min(gift_balance(db, user.id), Decimal(price))
    paid = Decimal(price) - from_gift
    label = f"Nivel {level} · {pricing.LEVEL_NAMES[level]} · {company.name}"
    if from_gift > 0:
        _move(db, user.id, "nivel_bono", -from_gift, reference, f"{label} (con @pples regaladas)",
              company_id=company.id, level_number=level)
    if paid > 0:
        _move(db, user.id, "nivel", -paid, reference, label, company_id=company.id, level_number=level)
    # Comisiones de la red solo sobre lo pagado con @pples compradas (consumo real)
    for depth, sponsor_id in enumerate(upline(db, user.id) if paid > 0 else [], start=1):
        _move(db, sponsor_id, "referido", paid * Decimal(str(pricing.REFERRAL_RATE)), reference,
              f"Red nivel {depth}: {user.name.split(' ')[0]} pagó el Nivel {level}", company_id=company.id,
              level_number=level, depth=depth, source_user_id=user.id)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppleError("Ese Nivel ya está pagado.") from exc
    return {"level": level, "apples": price, "balance": float(balance(db, user.id))}
