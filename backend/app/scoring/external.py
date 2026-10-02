"""Evidencia externa del Nivel 1 (AD-FUNC-01, WO-108).

1. **Verificación de fuentes:** cuando el cliente registra un dato con un enlace, ADÁN lo abre
   (con la protección SSRF de app/core/net.py) y deja constancia de si la fuente existe y de su
   título. "Verificable" pasa a ser "verificado" o "no se pudo verificar", y el cliente lo ve.
2. **CSI** (AD-000 §3): la inteligencia externa del ecosistema. ADÁN le pide señales sobre el
   dolor por un contrato versionado (`POST {CSI_BASE_URL}/v0/signals`; AD-000 §4 regla 4: nunca
   acceso directo a su base). Lo que llega entra como evidencia *propuesta*: cuenta para el Score
   solo cuando el cliente la confirma (AD-CMP-01: aprobación explícita).
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core import net

MAX_BYTES = 200_000
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def looks_like_url(source: str | None) -> bool:
    return bool(source) and bool(re.match(r"^https?://", source.strip(), re.IGNORECASE))


async def verify_source(url: str, timeout: float = 6.0) -> dict:
    """Abre la fuente y devuelve la constancia de verificación (nunca lanza)."""
    try:
        await net.ensure_public_url(url)
        async with net.public_http_client(timeout=timeout, follow_redirects=True) as client:
            async with client.stream("GET", url, headers={"User-Agent": "ADAN-verificador/1.0"}) as resp:
                body = b""
                async for chunk in resp.aiter_bytes():
                    body += chunk
                    if len(body) >= MAX_BYTES:
                        break
        text = body.decode("utf-8", errors="ignore")
        match = TITLE_RE.search(text)
        title = html.unescape(" ".join(match.group(1).split()))[:300] if match else None
        ok = resp.status_code < 400
        return {"status": "verified" if ok else "unreachable", "http_status": resp.status_code,
                "title": title, "checked_at": _now()}
    except net.BlockedURLError as exc:
        return {"status": "blocked", "detail": str(exc)[:300], "checked_at": _now()}
    except (httpx.HTTPError, OSError) as exc:
        return {"status": "unreachable", "detail": type(exc).__name__, "checked_at": _now()}


class CsiUnavailable(RuntimeError):
    """CSI no está conectado (sin CSI_BASE_URL) o no respondió."""


async def csi_signals(query: str, *, country: str | None, industry: str | None, timeout: float = 15.0) -> list[dict]:
    """Señales externas de CSI sobre un dolor (contrato v0).

    Petición: {"query", "country", "industry", "purpose": "pain_validation"}.
    Respuesta: {"signals": [{"claim", "source", "polarity": "supports"|"contradicts"}]}.
    """
    if not settings.CSI_BASE_URL:
        raise CsiUnavailable("CSI no está conectado todavía: falta configurar CSI_BASE_URL")
    headers = {"Authorization": f"Bearer {settings.CSI_API_KEY}"} if settings.CSI_API_KEY else {}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{settings.CSI_BASE_URL}/v0/signals", headers=headers, json={
                "query": query, "country": country, "industry": industry, "purpose": "pain_validation"})
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise CsiUnavailable(f"CSI no respondió: {type(exc).__name__}") from exc
    signals = []
    for raw in (data.get("signals") or [])[:20]:
        claim, source = str(raw.get("claim") or "").strip(), str(raw.get("source") or "").strip()
        if len(claim) < 10 or not source:
            continue  # sin afirmación clara o sin fuente no es un dato verificable
        polarity = raw.get("polarity") if raw.get("polarity") in ("supports", "contradicts") else "supports"
        signals.append({"claim": claim[:5000], "source": source[:2000], "polarity": polarity})
    return signals
