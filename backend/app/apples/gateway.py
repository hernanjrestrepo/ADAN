"""Pasarela de pagos detrás de un solo contrato, como en Xmart Travel: la persona paga en la página ALOJADA por la
pasarela (ADÁN nunca ve la tarjeta) y el resultado llega por webhook firmado o se consulta directamente.

- `simulador`: sin llaves. La "página de pago" es una pantalla de ADÁN que aprueba o rechaza: sirve para probar.
- `wompi`: Web Checkout de Wompi (Bancolombia) con firma de integridad; eventos `transaction.updated` verificados con
  el secreto de eventos. Con llaves de producción no se cobra mientras PAYMENTS_LIVE esté apagado.
"""
from __future__ import annotations

import hashlib
from urllib.parse import urlencode

import httpx

from app.core.config import settings

WOMPI_CHECKOUT = "https://checkout.wompi.co/p/"


class GatewayError(RuntimeError):
    pass


def provider() -> str:
    return "wompi" if settings.PAYMENTS_PROVIDER == "wompi" and settings.WOMPI_PUBLIC_KEY else "simulador"


def is_production_key() -> bool:
    return settings.WOMPI_PUBLIC_KEY.startswith("pub_prod_")


def _api_base() -> str:
    return "https://production.wompi.co/v1" if is_production_key() else "https://sandbox.wompi.co/v1"


def integrity_signature(reference: str, amount_in_cents: int, currency: str = "COP") -> str:
    raw = f"{reference}{amount_in_cents}{currency}{settings.WOMPI_INTEGRITY_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()


def checkout_url(reference: str, amount_cop: int, redirect: str) -> str:
    """Enlace a la página de pago. En el simulador, a la pantalla de prueba de ADÁN."""
    if provider() == "simulador":
        return f"{settings.PUBLIC_URL}/apples?compra={reference}&simulador=1"
    if is_production_key() and not settings.PAYMENTS_LIVE:
        raise GatewayError("El cobro real todavía no está encendido (PAYMENTS_LIVE).")
    cents = amount_cop * 100
    params = {
        "public-key": settings.WOMPI_PUBLIC_KEY, "currency": "COP", "amount-in-cents": cents, "reference": reference,
        "signature:integrity": integrity_signature(reference, cents), "redirect-url": redirect,
    }
    return f"{WOMPI_CHECKOUT}?{urlencode(params)}"


def _dig(data: dict, path: str):
    node = data
    for part in path.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    return node


def verify_event(event: dict) -> bool:
    """Firma de los eventos de Wompi: SHA-256 de los valores de `signature.properties` + `timestamp` + secreto."""
    if not settings.WOMPI_EVENTS_SECRET:
        return False
    sig = event.get("signature") or {}
    props = sig.get("properties") or []
    values = "".join(str(_dig(event.get("data") or {}, p)) for p in props)
    raw = f"{values}{event.get('timestamp', '')}{settings.WOMPI_EVENTS_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest() == str(sig.get("checksum", "")).lower()


def status_from_wompi(status: str) -> str:
    return {"APPROVED": "aprobada", "DECLINED": "rechazada", "VOIDED": "rechazada", "ERROR": "rechazada"}.get(
        status, "pendiente")


async def lookup(reference: str) -> tuple[str, str | None]:
    """Si el webhook se perdió, se pregunta a Wompi por la referencia. Devuelve (estado, id de la transacción)."""
    if provider() != "wompi" or not settings.WOMPI_PRIVATE_KEY:
        return "pendiente", None
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{_api_base()}/transactions", params={"reference": reference},
                             headers={"Authorization": f"Bearer {settings.WOMPI_PRIVATE_KEY}"})
    if r.status_code != 200:
        return "pendiente", None
    items = r.json().get("data") or []
    if not items:
        return "pendiente", None
    tx = items[0]
    return status_from_wompi(tx.get("status", "")), tx.get("id")
