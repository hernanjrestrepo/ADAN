"""API de @pples: precios, billetera, compras (Wompi o simulador), pago de Niveles y la red de referidos."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.apples import gateway, pricing, service
from app.apples.models import ApplePurchase
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.models.models import User

router = APIRouter(prefix="/apples", tags=["@pples"])


class PurchaseBody(BaseModel):
    apples: int = Field(..., ge=service.MIN_PURCHASE, le=service.MAX_PURCHASE)


class SimulateBody(BaseModel):
    approve: bool


def _own_purchase(db: Session, purchase_id: str, user: User) -> ApplePurchase:
    p = db.get(ApplePurchase, purchase_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return p


@router.get("/precios")
def prices():
    """La tabla de precios por Nivel, con el costo que hay detrás de cada uno (transparente)."""
    return {**pricing.price_table(), "packs": service.PACKS, "trm": service.settings.APPLE_TRM,
            "provider": gateway.provider()}


@router.get("/billetera")
def wallet(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.ensure_profile(db, user)
    db.commit()
    return {"balance": float(service.balance(db, user.id)), "movements": service.movements(db, user.id),
            "provider": gateway.provider(), "required": service.settings.APPLES_REQUIRED}


@router.post("/compras", status_code=201)
def buy(body: PurchaseBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return service.purchase_view(service.create_purchase(db, user, body.apples))
    except service.AppleError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/compras/{purchase_id}")
async def purchase(purchase_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Estado de una compra; si sigue pendiente se pregunta a la pasarela (por si se perdió el webhook)."""
    p = _own_purchase(db, purchase_id, user)
    if p.status == "pendiente" and p.provider == "wompi":
        status, tx = await gateway.lookup(p.id)
        p = service.resolve_purchase(db, p, status, tx)
    return {**service.purchase_view(p), "balance": float(service.balance(db, user.id))}


@router.post("/compras/{purchase_id}/simular")
def simulate(purchase_id: str, body: SimulateBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Solo en el simulador: aprueba o rechaza la compra como lo haría la pasarela."""
    p = _own_purchase(db, purchase_id, user)
    if p.provider != "simulador":
        raise HTTPException(status_code=409, detail="Esta compra se paga en la pasarela real")
    p = service.resolve_purchase(db, p, "aprobada" if body.approve else "rechazada", f"sim-{p.id[:8]}")
    return {**service.purchase_view(p), "balance": float(service.balance(db, user.id))}


@router.post("/webhook/wompi")
async def wompi_webhook(request: Request, db: Session = Depends(get_db)):
    """Eventos de Wompi. Solo se aceptan con la firma correcta; una transacción repetida no acredita dos veces."""
    event = await request.json()
    if not gateway.verify_event(event):
        raise HTTPException(status_code=401, detail="Firma inválida")
    tx = ((event.get("data") or {}).get("transaction")) or {}
    p = db.get(ApplePurchase, str(tx.get("reference", "")))
    if p is None:
        return {"ok": True, "ignored": "referencia desconocida"}
    if int(tx.get("amount_in_cents") or 0) != p.amount_cop * 100:
        raise HTTPException(status_code=409, detail="El monto no coincide con la compra")
    service.resolve_purchase(db, p, gateway.status_from_wompi(str(tx.get("status", ""))), tx.get("id"))
    return {"ok": True}


@router.get("/niveles/{company_id}")
def company_levels(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company = get_owned_company(db, company_id, user)
    return {"levels": service.levels_for(db, company), "balance": float(service.balance(db, user.id)),
            "required": service.settings.APPLES_REQUIRED}


@router.post("/niveles/{company_id}/{level}")
def pay_level(company_id: str, level: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company = get_owned_company(db, company_id, user)
    try:
        return service.unlock_level(db, user, company, level)
    except service.AppleError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/red")
def referral_network(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = service.network(db, user)
    db.commit()
    return data
