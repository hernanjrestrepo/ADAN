"""API de Genexis (Nivel 4): las páginas públicas del MVP, el formulario de interesados y el taller del fundador."""
from __future__ import annotations

import csv
import html
import io
import json
import logging
import re

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.ai.usage import usage_scope
from app.api.v1.nivel1 import get_llm
from app.apples import service as apples
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.core.ratelimit import client_ip, limiter, llm_user
from app.empresa.service import Marca
from app.genexis import service as gx
from app.genexis.models import Lead
from app.models.models import Company, Project, User
from app.nivel1 import timeline

logger = logging.getLogger(__name__)
router = APIRouter(tags=["genexis"])

# La página generada corre aislada: origen opaco, sin la sesión de ADÁN, solo puede mostrar y enviar el formulario
SANDBOX = "sandbox allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox"
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TIPOS = ("landing", "prototipo")


def _page(content: str, status: int = 200) -> Response:
    return Response(content, status_code=status, media_type="text/html; charset=utf-8",
                    headers={"Content-Security-Policy": SANDBOX, "X-Robots-Tag": "noindex",
                             "Referrer-Policy": "no-referrer"})


def _ctx(db: Session, company_id: str, user: User) -> tuple[Company, Project]:
    company = get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company.id).first()
    return company, project


# --- Público -----------------------------------------------------------------------------------------------------

@router.get("/sitio/{slug}")
def public_site(slug: str, db: Session = Depends(get_db)):
    doc, data = gx.by_slug(db, slug)
    if doc is None or not data.get("html"):
        return _page("<h1 style='font-family:sans-serif'>Esta página no existe.</h1>", 404)
    project = db.get(Project, doc.project_id)
    company = db.get(Company, project.company_id)
    return _page(gx.render(data, Marca(None, db).identity(company, project), company.name))


@router.post("/sitio/{slug}/interes")
def public_lead(slug: str, request: Request, nombre: str = Form("", max_length=120), correo: str = Form("", max_length=200),
                celular: str = Form("", max_length=40), mensaje: str = Form("", max_length=1000),
                autorizo: str = Form(""), db: Session = Depends(get_db)):
    """Un interesado deja sus datos: solo con la autorización marcada y un correo válido."""
    doc, data = gx.by_slug(db, slug)
    if doc is None:
        return _page("<h1 style='font-family:sans-serif'>Esta página no existe.</h1>", 404)
    project = db.get(Project, doc.project_id)
    company = db.get(Company, project.company_id)
    back = f"<p><a href='/api/v1/sitio/{html.escape(slug)}'>Volver</a></p>"
    if limiter.hit(f"lead:{request.headers.get('cf-connecting-ip') or client_ip(request)}", 20, 3600):
        return _page("<h2 style='font-family:sans-serif'>Recibimos muchos envíos. Intenta más tarde.</h2>" + back, 429)
    if autorizo != "si" or not _EMAIL.match(correo.strip()):
        return _page("<h2 style='font-family:sans-serif'>Para contactarte necesitamos un correo válido y tu autorización "
                     "de tratamiento de datos.</h2>" + back, 422)
    db.add(Lead(company_id=company.id, site=slug, name=nombre.strip()[:120], email=correo.strip()[:200],
                phone=celular.strip()[:40], message=mensaje.strip()[:1000], consent=True,
                consent_version=gx.CONSENT_VERSION))
    db.commit()
    color = html.escape(Marca(None, db).identity(company, project).get("color") or "#2563eb")
    return _page(
        "<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,"
        "initial-scale=1'><title>¡Gracias!</title></head><body style='font-family:system-ui,sans-serif;display:grid;"
        f"place-items:center;min-height:100vh;margin:0;background:#f8fafc'><div style='text-align:center;padding:24px'>"
        f"<div style='font-size:56px'>🎉</div><h1 style='color:{color}'>¡Gracias, {html.escape(nombre.strip() or 'de verdad')}!</h1>"
        f"<p>El equipo de {html.escape(company.name)} te escribirá muy pronto.</p>{back}</div></body></html>")


# --- Taller del fundador -----------------------------------------------------------------------------------------

class SiteBody(BaseModel):
    tipo: str = Field(..., pattern="^(landing|prototipo)$")
    aprobar_apples: bool = False


class TweakBody(BaseModel):
    instruccion: str = Field(..., min_length=3, max_length=1000)
    aprobar_apples: bool = False


class EvalBody(BaseModel):
    url: str = Field(..., min_length=4, max_length=2000)


def _status(db: Session, company: Company, project: Project) -> dict:
    sites = {}
    for tipo in TIPOS:
        doc = gx.site_doc(db, project, tipo)
        data = json.loads(doc.content) if doc else {}
        sites[tipo] = {k: data.get(k) for k in ("slug", "version", "estado", "error", "ajustes", "actualizado",
                                                "ultimo_ajuste")} if data else None
        if sites[tipo]:
            sites[tipo]["url"] = f"/api/v1/sitio/{data['slug']}" if data.get("html") else None
    spec = Genexis_spec(db, project)
    plan = db.query(gx.Document).filter(gx.Document.project_id == project.id, gx.Document.title == gx.PLAN_TITLE).first()
    return {
        "empresa_existente": company.origin_stage == "existing",
        "especificacion": {"id": spec.id, "markdown": spec.content} if spec else None,
        "plan_mejoras": {"id": plan.id, "markdown": plan.content} if plan else None,
        "sitios": sites,
        "interesados": db.query(Lead).filter(Lead.company_id == company.id).count(),
        "precio_prototipo": gx.quote(gx.PROTOTYPE_TOKENS),
        "precio_ajuste": gx.quote(gx.TWEAK_TOKENS),
        "ajustes_gratis": gx.FREE_TWEAKS,
    }


def Genexis_spec(db: Session, project: Project):  # noqa: N802 - atajo de lectura
    return db.query(gx.Document).filter(gx.Document.project_id == project.id, gx.Document.title == gx.SPEC_TITLE).first()


@router.get("/genexis/{company_id}")
def workshop(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    return _status(db, company, project)


@router.post("/genexis/{company_id}/especificacion")
async def write_spec(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                     llm: LLMAdapter = Depends(get_llm)):
    company, project = _ctx(db, company_id, user)
    try:
        with usage_scope(db, company_id, level=4):
            await gx.Genexis(llm, db).spec(project, company)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _status(db, company, project)


async def _build_later(bind, llm, company_id: str, tipo: str, instruction: str = "") -> None:
    db = Session(bind=bind)
    try:
        project = db.query(Project).filter(Project.company_id == company_id).first()
        company = db.get(Company, company_id)
        engine = gx.Genexis(llm, db)
        try:
            with usage_scope(db, company_id, level=4):
                data = await (engine.tweak(project, company, tipo, instruction) if instruction
                              else engine.build(project, company, tipo))
        except Exception as exc:  # noqa: BLE001 - el fundador ve el error y puede reintentar
            logger.exception("Genexis no pudo construir %s", tipo)
            gx.save_site(db, project, company, tipo, estado="error", error=str(exc)[:200] or "Error al construir")
            return
        what = "la landing" if tipo == "landing" else "el prototipo"
        timeline.post(db, project, (f"🛠️ Listo: {'ajusté' if instruction else 'construí'} {what} de **{company.name}** "
                                    f"(versión {data['version']}). Mírala en el Taller de Genexis o en su enlace: "
                                    f"/api/v1/sitio/{data['slug']}"), agent="genexis", nivel=4,
                      reaccion={"agente": "genexis", "emocion": "celebrando", "frase": "¡Construido!"})
        db.commit()
    finally:
        db.close()


@router.post("/genexis/{company_id}/sitio")
def build_site(company_id: str, body: SiteBody, background: BackgroundTasks, db: Session = Depends(get_db),
               user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    """Construye la landing (incluida en el Nivel 4) o el prototipo (cobrado aparte, con aprobación)."""
    company, project = _ctx(db, company_id, user)
    current = gx.site_doc(db, project, body.tipo)
    version = (json.loads(current.content).get("version", 0) if current else 0) + 1
    if body.tipo == "prototipo":
        price = gx.quote(gx.PROTOTYPE_TOKENS)
        if not body.aprobar_apples:
            raise HTTPException(status_code=402, detail=f"El prototipo cuesta {price} @pples. Apruébalo para construirlo.")
        try:
            apples.spend(db, user, company, price, f"prototipo:{company.id}:{version}", "Prototipo navegable (Genexis)")
        except apples.AppleError as exc:
            raise HTTPException(status_code=402, detail=str(exc)) from exc
    gx.save_site(db, project, company, body.tipo, estado="construyendo", error="")
    background.add_task(_build_later, db.get_bind(), llm, company_id, body.tipo)
    return _status(db, company, project)


@router.post("/genexis/{company_id}/sitio/{tipo}/ajustar")
def tweak_site(company_id: str, tipo: str, body: TweakBody, background: BackgroundTasks, db: Session = Depends(get_db),
               user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    """Ajusta la página conversando («cambia el botón…»). Los primeros ajustes de cada página van incluidos."""
    if tipo not in TIPOS:
        raise HTTPException(status_code=404, detail="Página no encontrada")
    company, project = _ctx(db, company_id, user)
    doc = gx.site_doc(db, project, tipo)
    data = json.loads(doc.content) if doc else {}
    if not data.get("html"):
        raise HTTPException(status_code=409, detail="Primero construye la página.")
    if data.get("ajustes", 0) >= gx.FREE_TWEAKS:
        price = gx.quote(gx.TWEAK_TOKENS)
        if not body.aprobar_apples:
            raise HTTPException(status_code=402, detail=f"Este ajuste cuesta {price} @pples (los primeros "
                                                        f"{gx.FREE_TWEAKS} van incluidos). Apruébalo para seguir.")
        try:
            apples.spend(db, user, company, price, f"ajuste:{tipo}:{company.id}:{data.get('version', 0)}",
                         f"Ajuste de la {tipo} (Genexis)")
        except apples.AppleError as exc:
            raise HTTPException(status_code=402, detail=str(exc)) from exc
    gx.save_site(db, project, company, tipo, estado="construyendo", error="")
    background.add_task(_build_later, db.get_bind(), llm, company_id, tipo, body.instruccion.strip())
    return _status(db, company, project)


@router.get("/genexis/{company_id}/interesados")
def leads(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, _ = _ctx(db, company_id, user)
    rows = db.query(Lead).filter(Lead.company_id == company.id).order_by(Lead.created_at.desc()).limit(500).all()
    return [{"id": r.id, "nombre": r.name, "correo": r.email, "celular": r.phone, "mensaje": r.message,
             "pagina": r.site, "fecha": r.created_at.isoformat()} for r in rows]


@router.get("/genexis/{company_id}/interesados.csv")
def leads_csv(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, _ = _ctx(db, company_id, user)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["fecha", "nombre", "correo", "celular", "mensaje", "pagina", "autorizacion"])
    for r in db.query(Lead).filter(Lead.company_id == company.id).order_by(Lead.created_at).all():
        w.writerow([r.created_at.isoformat(), r.name, r.email, r.phone, r.message, r.site, r.consent_version])
    return Response("﻿" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": 'attachment; filename="interesados.csv"'})


@router.get("/genexis/{company_id}/codigo.zip")
def code(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    return Response(gx.Genexis(None, db).code_zip(project, company), media_type="application/zip",
                    headers={"Content-Disposition": f'attachment; filename="{gx.slugify(company.name)}-mvp.zip"'})


async def _evaluate_later(bind, llm, company_id: str, url: str) -> None:
    from app.ai.router import for_tier
    from app.documents import recorrido

    db = Session(bind=bind)
    try:
        project = db.query(Project).filter(Project.company_id == company_id).first()
        company = db.get(Company, company_id)
        with usage_scope(db, company_id, level=4):
            result = await recorrido.walk(for_tier(llm, "standard"), url,
                                          "Recorrer el producto como un cliente nuevo: entender qué ofrece, probar el "
                                          "flujo principal y llegar lo más lejos posible sin pagar")
            report = recorrido.as_markdown(url, "Evaluación del producto", result)
            doc = await gx.Genexis(llm, db).improvement_plan(project, company, report)
        timeline.post(db, project, f"🛠️ Recorrí tu producto y dejé el **plan de mejoras** en el Taller y en la "
                                   f"Biblioteca.\n\n{(doc.content or '')[:1200]}", agent="genexis", nivel=4,
                      reaccion={"agente": "genexis", "emocion": "pensando", "frase": "Revisé tu producto."})
        db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("La evaluación del producto falló")
    finally:
        db.close()


@router.post("/genexis/{company_id}/evaluar")
def evaluate(company_id: str, body: EvalBody, background: BackgroundTasks, db: Session = Depends(get_db),
             user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    """La empresa ya tiene producto: Genexis lo recorre (y usa la revisión de código si existe) y propone mejoras."""
    company, project = _ctx(db, company_id, user)
    url = body.url.strip()
    background.add_task(_evaluate_later, db.get_bind(), llm, company_id, url if url.startswith("http") else "https://" + url)
    return {"started": True}
