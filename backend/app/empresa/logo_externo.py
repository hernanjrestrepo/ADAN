"""El logo de una empresa que ya existe: se toma de su página web (con permiso del fundador) o lo sube él.

Se descarga con el cliente HTTP seguro, se guarda como imagen incrustada (data URL) y de ahí sale la paleta:
los colores dominantes de la imagen (o los que declara el SVG).
"""
from __future__ import annotations

import base64
import io
import re
from collections import Counter

import httpx

from app.core.net import BlockedURLError, public_http_client

MAX_BYTES = 600_000
_HEX = re.compile(r"#([0-9a-f]{6}|[0-9a-f]{3})\b", re.I)
IMAGE_TYPES = ("image/png", "image/jpeg", "image/webp", "image/svg+xml", "image/gif", "image/x-icon",
               "image/vnd.microsoft.icon")


class LogoError(ValueError):
    pass


async def download(url: str) -> tuple[bytes, str]:
    try:
        async with public_http_client(timeout=10, follow_redirects=True,
                                      headers={"User-Agent": "Mozilla/5.0 ADAN-Paradixe/1.0"}) as client:
            resp = await client.get(url)
    except BlockedURLError as e:
        raise LogoError("La dirección del logo no es pública.") from e
    except httpx.HTTPError as e:
        raise LogoError("No se pudo descargar el logo.") from e
    ctype = resp.headers.get("content-type", "").split(";")[0].strip().lower()
    if resp.status_code >= 400 or not ctype.startswith("image/"):
        raise LogoError("Esa dirección no es una imagen.")
    if len(resp.content) > MAX_BYTES:
        raise LogoError("La imagen del logo es muy pesada (máximo 600 KB).")
    return resp.content, ctype


def data_url(data: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _norm(h: str) -> str:
    h = h.lower()
    return "#" + "".join(c * 2 for c in h[1:]) if len(h) == 4 else h


def _plain(hexcolor: str) -> bool:
    """Blancos, negros y grises casi puros no sirven como color de marca."""
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    return max(r, g, b) - min(r, g, b) < 18 or max(r, g, b) < 25 or min(r, g, b) > 235


def palette(data: bytes, mime: str) -> list[str]:
    """Hasta 3 colores de marca, del más al menos presente."""
    if "svg" in mime:
        found = [_norm("#" + m) for m in _HEX.findall(data.decode("utf-8", "ignore"))]
        counts = Counter(c for c in found if not _plain(c))
        return [c for c, _ in counts.most_common(3)]
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:  # noqa: BLE001 - un ícono raro no impide adoptar el logo
        return []
    img.thumbnail((96, 96))
    pixels = [(r // 16 * 16, g // 16 * 16, b // 16 * 16) for r, g, b, a in img.getdata() if a > 128]
    counts = Counter(_hex(p) for p in pixels)
    colors = [c for c, _ in counts.most_common(30) if not _plain(c)]
    out: list[str] = []
    for c in colors:  # colores distintos entre sí
        if all(sum(abs(int(c[i:i + 2], 16) - int(o[i:i + 2], 16)) for i in (1, 3, 5)) > 90 for o in out):
            out.append(c)
        if len(out) == 3:
            break
    return out
