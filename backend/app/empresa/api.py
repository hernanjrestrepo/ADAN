"""API de la construcción de la empresa: Expediente de creación, marca (nombre, logo, slogan, manual), identidad para
las oficinas y el presupuesto y flujo de caja construidos dentro de la Sala del Nivel 3."""
from __future__ import annotations

import base64

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.ai.usage import usage_scope
from app.api.v1.nivel1 import get_llm
from app.constitucion.service import company_context, markdown_to_docx
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.core.ratelimit import llm_user
from app.documents import extract as doc_extract
from app.documents import media
from app.empresa import biblioteca, logo_externo
from app.empresa.catalog import COUNTRIES, items_for
from app.empresa.service import STATUSES, Expediente, Marca
from app.levels import entregables
from app.models.models import Document, Project, User
from app.nivel1 import memoria, timeline
from app.nivel1.service import Nivel1Service

router = APIRouter(prefix="/empresa", tags=["empresa"])


class CountryBody(BaseModel):
    pais: str = Field(..., max_length=10)


class StatusBody(BaseModel):
    estado: str
    nota: str = Field("", max_length=500)


class IdeasBody(BaseModel):
    ideas: str = Field("", max_length=1000)


class NameChoice(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    adoptar: bool = True


class LogoChoice(BaseModel):
    concepto: str = Field(..., max_length=10)
    imagen: str | None = Field(None, max_length=400_000)


class SloganChoice(BaseModel):
    texto: str = Field(..., min_length=2, max_length=120)


def _ctx(db: Session, company_id: str, user: User):
    company = get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return company, project


def _context(db: Session, project: Project, company, llm) -> str:
    before = Nivel1Service(llm, db).levels_brief(project, 4)
    return company_context(db, project, company) + (f"\n\nLo construido en los Niveles:\n{before[:6000]}" if before else "")


def _item(code: str, item_id: str) -> dict:
    item = next((i for i in items_for(code) if i["id"] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Ese trámite no está en el Expediente")
    return item


# ------------------------------ Expediente ------------------------------

@router.get("/{company_id}/expediente")
def expediente(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    return Expediente(None, db).view(project, company)


@router.put("/{company_id}/expediente/pais")
def expediente_country(company_id: str, body: CountryBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    if body.pais not in COUNTRIES:
        raise HTTPException(status_code=422, detail="País no soportado")
    exp = Expediente(None, db)
    exp.set_country(project, body.pais)
    return exp.view(project, company)


@router.post("/{company_id}/expediente/{item_id}/estado")
def expediente_status(company_id: str, item_id: str, body: StatusBody, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    exp = Expediente(None, db)
    _item(exp.view(project, company)["pais"], item_id)
    if body.estado not in STATUSES:
        raise HTTPException(status_code=422, detail="Estado no válido")
    exp.set_status(project, item_id, body.estado, body.nota)
    return exp.view(project, company)


@router.post("/{company_id}/expediente/{item_id}/preparar")
async def expediente_prepare(company_id: str, item_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                             llm: LLMAdapter = Depends(get_llm)):
    """ADÁN deja listo el trámite: documentos redactados, qué llevar, portal y paso a paso."""
    company, project = _ctx(db, company_id, user)
    exp = Expediente(llm, db)
    view = exp.view(project, company)
    item = _item(view["pais"], item_id)
    with usage_scope(db, company_id, level=3):
        doc = await exp.prepare(project, company, item, _context(db, project, company, llm), view["pais_nombre"])
    return {"id": doc.id, "title": doc.title, "markdown": doc.content}


@router.get("/{company_id}/expediente/paquete/{doc_id}.docx")
def expediente_docx(company_id: str, doc_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _ctx(db, company_id, user)
    doc = db.query(Document).filter(Document.id == doc_id, Document.project_id == project.id,
                                    Document.doc_type == "expediente_paquete").first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Ese paquete no existe")
    return Response(markdown_to_docx(doc.content or "", doc.title),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": 'attachment; filename="tramite.docx"'})


@router.get("/{company_id}/expediente/paquete/{doc_id}")
def expediente_doc(company_id: str, doc_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _ctx(db, company_id, user)
    doc = db.query(Document).filter(Document.id == doc_id, Document.project_id == project.id,
                                    Document.doc_type == "expediente_paquete").first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Ese paquete no existe")
    return {"id": doc.id, "title": doc.title, "markdown": doc.content}


@router.post("/{company_id}/expediente/{item_id}/documento")
async def expediente_upload(company_id: str, item_id: str, file: UploadFile = File(...), db: Session = Depends(get_db),
                            user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    """El fundador carga el documento oficial (PDF o foto) y ADÁN lo lee y valida contra los datos de la empresa."""
    company, project = _ctx(db, company_id, user)
    exp = Expediente(llm, db)
    item = _item(exp.view(project, company)["pais"], item_id)
    data = await file.read(doc_extract.MAX_FILE_BYTES + 1)
    try:
        d = doc_extract.extract(file.filename or "documento", data)
    except doc_extract.ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    text = d.text
    try:
        if d.pending == "ocr" and d.kind == "Imagen":
            text = await media.ocr_image(d.data, media.IMAGE_TYPES.get(doc_extract.extension(d.filename), "image/png"))
        elif d.pending == "ocr":
            text = (await media.ocr_pdf(d.data))[0] or text
    except media.MediaError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if d.pending == "transcribir" or len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="No encontré texto legible en ese archivo. Súbelo en PDF o como foto nítida.")
    with usage_scope(db, company_id, level=3):
        result = await exp.validate(project, company, item, d.filename, text)
    return {"validacion": result, "expediente": exp.view(project, company)}


# ------------------------------ Marca ------------------------------

@router.get("/{company_id}/marca")
def marca(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    return {**Marca(None, db).view(project), "identidad": Marca(None, db).identity(company, project)}


@router.post("/{company_id}/marca/nombres")
async def marca_names(company_id: str, body: IdeasBody, db: Session = Depends(get_db), user: User = Depends(llm_user),
                      llm: LLMAdapter = Depends(get_llm)):
    company, project = _ctx(db, company_id, user)
    with usage_scope(db, company_id, level=2):
        return await Marca(llm, db).names(project, _context(db, project, company, llm), body.ideas.strip())


@router.post("/{company_id}/marca/nombre")
def marca_choose_name(company_id: str, body: NameChoice, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    data = Marca(None, db).choose_name(project, company, body.nombre.strip(), body.adoptar)
    Expediente(None, db).set_status(project, "nombre", "validado", f"Nombre elegido: {body.nombre.strip()}")
    return data


@router.post("/{company_id}/marca/logos")
async def marca_logos(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                      llm: LLMAdapter = Depends(get_llm)):
    company, project = _ctx(db, company_id, user)
    m = Marca(llm, db)
    name = m.view(project).get("nombre_elegido") or company.name
    with usage_scope(db, company_id, level=2):
        return await m.logos(project, _context(db, project, company, llm), name)


@router.post("/{company_id}/marca/logo")
def marca_choose_logo(company_id: str, body: LogoChoice, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    if body.imagen and not body.imagen.startswith(("data:image/svg+xml;base64,", "data:image/png;base64,")):
        raise HTTPException(status_code=422, detail="El logo debe ser SVG o PNG")
    try:
        data = Marca(None, db).choose_logo(project, company, body.concepto, body.imagen)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    Expediente(None, db).set_status(project, "logo", "en_curso", "Logo elegido; falta el manual de marca.")
    return data


class ExistingLogo(BaseModel):
    url: str | None = Field(None, max_length=2000)
    imagen: str | None = Field(None, max_length=900_000)


@router.post("/{company_id}/marca/logo-actual")
async def marca_existing_logo(company_id: str, body: ExistingLogo, db: Session = Depends(get_db),
                              user: User = Depends(get_current_user)):
    """Adopta el logo que la empresa ya tiene: desde una dirección de su web o subido como imagen."""
    company, project = _ctx(db, company_id, user)
    try:
        if body.url:
            raw, mime = await logo_externo.download(body.url)
            source = f"tomado de {body.url}"
        elif body.imagen and body.imagen.startswith("data:image/"):
            head, _, b64 = body.imagen.partition(",")
            mime = head[5:].split(";")[0]
            raw = base64.b64decode(b64, validate=False)
            if len(raw) > logo_externo.MAX_BYTES:
                raise logo_externo.LogoError("La imagen del logo es muy pesada (máximo 600 KB).")
            source = "subido por el fundador"
        else:
            raise logo_externo.LogoError("Envía la dirección del logo o la imagen.")
        if mime not in logo_externo.IMAGE_TYPES:
            raise logo_externo.LogoError("El logo debe ser PNG, JPG, WEBP, SVG o ICO.")
    except logo_externo.LogoError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="La imagen no se pudo leer.") from exc
    data = Marca(None, db).adopt_existing(project, company, logo_externo.data_url(raw, mime),
                                          logo_externo.palette(raw, mime), source)
    Expediente(None, db).set_status(project, "logo", "en_curso", "Se adoptó el logo actual; falta el manual de marca.")
    return {**data, "identidad": Marca(None, db).identity(company, project)}


@router.post("/{company_id}/marca/slogans")
async def marca_slogans(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                        llm: LLMAdapter = Depends(get_llm)):
    company, project = _ctx(db, company_id, user)
    m = Marca(llm, db)
    with usage_scope(db, company_id, level=2):
        return await m.slogans(project, _context(db, project, company, llm), m.view(project).get("nombre_elegido") or company.name)


@router.post("/{company_id}/marca/slogan")
def marca_choose_slogan(company_id: str, body: SloganChoice, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _ctx(db, company_id, user)
    return Marca(None, db).choose_slogan(project, body.texto.strip())


@router.post("/{company_id}/marca/manual")
async def marca_manual(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                       llm: LLMAdapter = Depends(get_llm)):
    company, project = _ctx(db, company_id, user)
    with usage_scope(db, company_id, level=2):
        data = await Marca(llm, db).manual(project, _context(db, project, company, llm))
    if data.get("logo_elegido"):
        Expediente(None, db).set_status(project, "logo", "validado", "Logo y manual de marca listos.")
    return data


@router.get("/{company_id}/marca/manual.docx")
def marca_manual_docx(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _ctx(db, company_id, user)
    text = Marca(None, db).view(project).get("manual") or ""
    if not text:
        raise HTTPException(status_code=404, detail="Todavía no hay manual de marca")
    return Response(markdown_to_docx(text, "Manual de marca"),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": 'attachment; filename="manual-de-marca.docx"'})


@router.get("/{company_id}/identidad")
def identity(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Nombre, slogan, logo y colores: lo que las oficinas muestran mientras la empresa se construye."""
    company, project = _ctx(db, company_id, user)
    exp = Expediente(None, db).view(project, company)
    return {**Marca(None, db).identity(company, project), "expediente": {"hechos": exp["hechos"], "total": exp["total"]}}


# ------------------------------ Números en la Sala ------------------------------

@router.post("/{company_id}/numeros")
async def numbers_in_room(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                          llm: LLMAdapter = Depends(get_llm)):
    """Camila arma el organigrama y el flujo de caja y los cuenta en la conversación del Nivel 3, con su gráfico."""
    from app.finanzas.service import Finanzas

    company, project = _ctx(db, company_id, user)
    fin = Finanzas(llm, db)
    ctx = _context(db, project, company, llm)
    with usage_scope(db, company_id, level=3):
        org = fin.org(project) or await fin.build_org(project, ctx)
        model = await fin.build_model(project, ctx)
    base = model.get("base") or {}
    k = base.get("kpis") or {}
    rows = base.get("rows") or []
    currency = (model.get("assumptions") or {}).get("moneda") or org.get("moneda") or ""
    step = max(1, len(rows) // 12)
    sample = rows[::step][:12]
    chart = ('```chart\n{"type":"line","title":"Caja mes a mes (' + currency + ')","labels":['
             + ",".join(f'"M{r.get("mes")}"' for r in sample) + '],"series":[{"name":"Caja","data":['
             + ",".join(str(round(float(r.get("caja") or 0))) for r in sample) + "]}]}\n```")
    be = k.get("punto_equilibrio_mes")
    text = (f"🧮 Listo el **presupuesto y el flujo de caja a 24 meses**.\n\n"
            f"- Punto de equilibrio: **{'mes ' + str(be) if be else 'no se alcanza en 24 meses con estos supuestos'}**\n"
            f"- Capital que necesitas: **{currency} {k.get('capital_necesario', 0):,.0f}**\n"
            f"- Caja más baja: **{currency} {k.get('caja_minima', 0):,.0f}** en el mes {k.get('caja_minima_mes', '—')}\n"
            f"- Organización: {org.get('resumen', '')}\n\n{chart}\n\n"
            "Puedes ajustar cualquier supuesto en 🧮 Finanzas y el flujo se recalcula al instante. ¿Revisamos juntos el que más te preocupe?")
    timeline.post(db, project, text, agent="cfo", nivel=3, reaccion={"agente": "cfo", "emocion": "feliz", "frase": "¡Números listos!"})
    Expediente(None, db).set_status(project, "presupuesto", "validado", "Flujo de caja a 24 meses construido.")
    Expediente(None, db).set_status(project, "organigrama", "validado", "Organigrama con IA y Paradixe construido.")
    db.commit()
    return {"ok": True, "kpis": k}


# --- Biblioteca: todo lo construido, en un solo lugar --------------------------------------------------------------

@router.get("/{company_id}/biblioteca")
def library(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company, project = _ctx(db, company_id, user)
    return biblioteca.catalog(db, project, company)


@router.post("/{company_id}/biblioteca/entregables")
def library_deliverables(company_id: str, background: BackgroundTasks, db: Session = Depends(get_db),
                         user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    """Prepara en segundo plano los entregables de los Niveles cerrados que todavía no están en la Biblioteca."""
    _, project = _ctx(db, company_id, user)
    pending = entregables.missing(db, project)
    if pending:
        background.add_task(entregables.build_later, db.get_bind(), llm, company_id)
    return {"pendientes": sum(len(v) for v in pending.values())}


def _library_doc(db: Session, project: Project, doc_id: str) -> tuple[str, str]:
    if doc_id == "manual":
        text = Marca(None, db).view(project).get("manual") or ""
        if text:
            return "Manual de marca", text
    else:
        doc = biblioteca.read(db, project, doc_id)
        if doc is not None:
            return doc.title, doc.content or ""
    raise HTTPException(status_code=404, detail="Documento no encontrado")


@router.get("/{company_id}/biblioteca/{doc_id}.docx")
def library_docx(company_id: str, doc_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _ctx(db, company_id, user)
    title, text = _library_doc(db, project, doc_id)
    return Response(markdown_to_docx(text, title),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": 'attachment; filename="documento.docx"'})


@router.get("/{company_id}/biblioteca/{doc_id}")
def library_doc(company_id: str, doc_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _, project = _ctx(db, company_id, user)
    title, text = _library_doc(db, project, doc_id)
    return {"id": doc_id, "titulo": title, "markdown": text}


# --- Ficha de la empresa y memoria del proyecto ---------------------------------------------------------------------

class FichaBody(BaseModel):
    ficha: dict[str, str] = Field(default_factory=dict)


@router.put("/{company_id}/ficha")
def update_ficha(company_id: str, body: FichaBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """El fundador corrige la ficha (fuente única de verdad de todo el equipo): lo que él escribe manda."""
    if len(body.ficha) > 60:
        raise HTTPException(status_code=422, detail="La ficha admite hasta 60 campos.")
    _, project = _ctx(db, company_id, user)
    return {"ficha": memoria.set_ficha(db, project, body.ficha)["ficha"]}


@router.post("/{company_id}/memoria/consolidar")
async def consolidate_memory(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                             llm: LLMAdapter = Depends(get_llm)):
    """ADÁN relee todas las conversaciones, recupera los acuerdos, quita contradicciones y arma la ficha."""
    _, project = _ctx(db, company_id, user)
    with usage_scope(db, company_id, level=1):
        data = await memoria.consolidate(llm, db, project)
    return {"ficha": data.get("ficha", {}), "acuerdos": len(data.get("acuerdos", []))}
