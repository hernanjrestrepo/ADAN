"""POST /visitas: la app avisa cada página que se abre. GET /admin/visitas: las cifras y el mapa para la consola."""
from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import SESSION_COOKIE, decode_token
from app.core.authz import require_superadmin
from app.core.config import settings
from app.core.database import get_db
from app.core.ratelimit import client_ip, limiter
from app.models.models import User
from app.visitas.models import Visit

router = APIRouter(tags=["visitas"])
_MOBILE = ("mobile", "android", "iphone", "ipad")


class NewVisit(BaseModel):
    ruta: str = Field(..., max_length=200)
    referente: str | None = Field(None, max_length=500)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.post("/visitas", status_code=204)
def visit(body: NewVisit, request: Request, db: Session = Depends(get_db)) -> Response:
    ip = request.headers.get("cf-connecting-ip") or client_ip(request)
    if limiter.hit(f"visitas:{ip}", 600, 3600):
        return Response(status_code=204)  # se ignora en silencio: contar no es crítico
    ua = request.headers.get("user-agent") or ""
    day = _now().date().isoformat()
    # El visitante: resumen de IP + navegador + día (no permite seguir a nadie de un día a otro)
    visitor = hashlib.sha256(f"{ip}|{ua}|{day}|{settings.JWT_SECRET[:8]}".encode()).hexdigest()[:24]
    user_id = None
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        try:
            user_id = decode_token(token).get("sub")
        except Exception:  # noqa: BLE001 - una sesión vencida igual cuenta como visita
            user_id = None
    ref = urlparse(body.referente or "").hostname
    host = (request.headers.get("host") or "").split(":")[0]
    country = (request.headers.get("cf-ipcountry") or "").upper()[:2] or None
    db.add(Visit(path=body.ruta.split("?")[0][:200], referrer=ref if ref and ref != host else None,
                 country=country if country not in ("XX", "T1") else None, visitor=visitor,
                 mobile=any(m in ua.lower() for m in _MOBILE), user_id=user_id))
    db.commit()
    return Response(status_code=204)


def _section(path: str) -> str:
    """/nivel/3/abc… → /nivel/3: se agrupan las páginas por sección, sin los identificadores."""
    parts = [p for p in path.split("/") if p]
    keep = [p for p in parts if len(p) < 20]
    return "/" + "/".join(keep[:2]) if keep else "/"


@router.get("/admin/visitas")
def stats(dias: int = Query(30, ge=1, le=3660), db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    since = _now() - timedelta(days=dias)
    rows = db.query(Visit).filter(Visit.created_at >= since).all()
    visitors = {v.visitor for v in rows}
    by_country: dict[str, list] = defaultdict(lambda: [0, set()])
    by_day: dict[str, list] = defaultdict(lambda: [0, set()])
    for v in rows:
        if v.country:
            by_country[v.country][0] += 1
            by_country[v.country][1].add(v.visitor)
        d = v.created_at.date().isoformat()
        by_day[d][0] += 1
        by_day[d][1].add(v.visitor)
    pages = Counter(_section(v.path) for v in rows)
    refs = Counter(v.referrer for v in rows if v.referrer)
    online = {v.visitor for v in rows if v.created_at >= _now() - timedelta(minutes=5)}
    total = len(rows)
    return {
        "dias": dias, "visitas": total, "visitantes": len(visitors), "ahora": len(online),
        "moviles": sum(1 for v in rows if v.mobile), "con_cuenta": sum(1 for v in rows if v.user_id),
        "paises": sorted(({"pais": k, "visitas": c, "visitantes": len(s)} for k, (c, s) in by_country.items()),
                         key=lambda x: -x["visitas"]),
        "por_dia": [{"dia": k, "visitas": c, "visitantes": len(s)} for k, (c, s) in sorted(by_day.items())],
        "paginas": [{"ruta": k, "visitas": n} for k, n in pages.most_common(12)],
        "referentes": [{"origen": k, "visitas": n} for k, n in refs.most_common(10)],
        "directas": sum(1 for v in rows if not v.referrer),
    }
