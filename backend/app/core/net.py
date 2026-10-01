"""Salida HTTP segura: protección SSRF compartida (TEF, DKA, integraciones).

Toda URL que llegue de un usuario o de un agente se valida antes de cada
request, incluidas las redirecciones: solo http(s) y nunca hacia loopback,
redes privadas, link-local (metadatos cloud), multicast o reservadas.
`ALLOW_PRIVATE_HTTP=true` desactiva el bloqueo de red interna (p. ej. para
integrar servicios propios de la intranet).

Riesgo residual documentado: DNS rebinding entre la validación y la conexión.
"""
from __future__ import annotations

import asyncio
import ipaddress
import os
import socket

import httpx


class BlockedURLError(Exception):
    """La URL apunta a un destino no permitido."""


def private_http_allowed() -> bool:
    return os.getenv("ALLOW_PRIVATE_HTTP", "false").lower() == "true"


def ssrf_block_reason(url: str) -> str | None:
    """Devuelve el motivo de bloqueo de `url`, o None si está permitida."""
    try:
        parsed = httpx.URL(url)
    except Exception:
        return "invalid URL"
    if parsed.scheme not in ("http", "https"):
        return "only http/https URLs are allowed"
    host = parsed.host
    if not host:
        return "missing host"
    if private_http_allowed():
        return None
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return None  # no resuelve: httpx devolverá el error de conexión
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return "internal network addresses are not allowed"
    return None


async def _guard_request(request: httpx.Request) -> None:
    reason = await asyncio.to_thread(ssrf_block_reason, str(request.url))
    if reason:
        raise BlockedURLError(f"Request blocked: {reason}")


def safe_async_client(**kwargs) -> httpx.AsyncClient:
    """`httpx.AsyncClient` que valida cada request (y cada redirección)."""
    hooks = kwargs.pop("event_hooks", {}) or {}
    hooks = {**hooks, "request": [_guard_request, *hooks.get("request", [])]}
    return httpx.AsyncClient(event_hooks=hooks, **kwargs)
