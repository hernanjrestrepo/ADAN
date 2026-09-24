"""Salida HTTP segura — bloquea peticiones hacia redes internas (SSRF).

Toda petición HTTP cuyo destino lo decide un usuario o un agente debe usar
public_http_client(): valida cada request, incluidas las redirecciones.
Riesgo residual conocido: DNS rebinding entre la validación y la conexión.
"""
from __future__ import annotations

import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

import httpx

ALLOWED_SCHEMES = {"http", "https"}


class BlockedURLError(ValueError):
    """La URL usa un esquema no permitido o resuelve a una dirección no pública."""


async def ensure_public_url(url: str) -> None:
    """Lanza BlockedURLError si la URL no es http(s) o resuelve a una dirección no pública."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.hostname:
        raise BlockedURLError(f"Only http(s) URLs with a host are allowed: {url}")

    try:
        infos = await asyncio.get_running_loop().getaddrinfo(parsed.hostname, None)
    except socket.gaierror as e:
        raise BlockedURLError(f"Cannot resolve host {parsed.hostname}: {e}") from e

    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if ip.version == 6 and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if not ip.is_global:
            raise BlockedURLError(f"Blocked non-public address {ip} for host {parsed.hostname}")


async def _guard_request(request: httpx.Request) -> None:
    await ensure_public_url(str(request.url))


def public_http_client(**kwargs) -> httpx.AsyncClient:
    """AsyncClient que valida cada request (incluidas las redirecciones) contra SSRF."""
    return httpx.AsyncClient(event_hooks={"request": [_guard_request]}, **kwargs)
