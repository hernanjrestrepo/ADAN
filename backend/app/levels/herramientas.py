"""Herramientas del equipo que tardan (corren en segundo plano y responden en la Sala del Nivel):
- Recorrido con clics por una página, opcionalmente con la cuenta del fundador (no se guarda).
- Revisión del código del producto en GitHub (el token, si lo hay, tampoco se guarda).
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.usage import usage_scope
from app.api.v1.nivel1 import get_llm
from app.core.authz import get_owned_company
from app.core.database import get_db
from app.core.ratelimit import llm_user
from app.documents import media, recorrido, repositorio, web
from app.models.models import Document, Project, User
from app.nivel1 import memoria, timeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/herramientas", tags=["herramientas"])


class WalkBody(BaseModel):
    url: str = Field(..., min_length=4, max_length=2000)
    objetivo: str = Field(..., min_length=3, max_length=500)
    usuario: str = Field("", max_length=200)
    clave: str = Field("", max_length=200)
    nivel: int = Field(1, ge=1, le=7)


class RepoBody(BaseModel):
    url: str = Field(..., min_length=10, max_length=500)
    objetivo: str = Field("", max_length=500)
    token: str = Field("", max_length=300)
    nivel: int = Field(1, ge=1, le=7)


def _project(db: Session, company_id: str) -> Project | None:
    return db.query(Project).filter(Project.company_id == company_id).first()


async def walk_later(bind, llm: LLMAdapter, company_id: str, url: str, goal: str, nivel: int,
                     user: str = "", password: str = "") -> None:
    """Recorre la página y cuenta en la Sala lo que encontró (Andrés, de producto)."""
    db = Session(bind=bind)
    try:
        project = _project(db, company_id)
        if project is None:
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        with usage_scope(db, company_id, level=nivel):
            result = await recorrido.walk(llm, url, goal, user, password)
            if result.get("error") and not result.get("steps"):
                timeline.post(db, project, f"Intenté recorrer {url} pero {result['error']}. ¿Me confirmas la dirección?",
                              agent="producto", nivel=nivel, recorrido=True)
                db.commit()
                return
            vision = ""
            shot = (result.get("final") or {}).get("screenshot")
            if shot and media.can_see():
                try:
                    vision = await media.ocr_image(shot, "image/jpeg", web.SCREEN_PROMPT)
                except Exception:  # noqa: BLE001 - sin visión queda el texto de la pantalla
                    vision = ""
            report = recorrido.as_markdown(url, goal, result, vision)
            if password:  # segunda barrera: la clave jamás llega al informe, a la IA ni a la Sala
                report = report.replace(password, "••••")
            db.add(Document(project_id=project.id, title=f"Recorrido: {goal}"[:255], content=report,
                            doc_type="web_page", origin="generated_by_adan"))
            try:
                resp = await llm.chat([
                    LLMMessage("system", (
                        "Eres Andrés, de producto, en el equipo de ADÁN. Acabas de recorrer con clics la página del "
                        "fundador. Cuéntale en máximo 150 palabras qué encontraste paso a paso (lo clave), qué funciona, "
                        "dónde hay fricción y una propuesta concreta. Si te detuviste antes de pagar, dilo: ADÁN nunca "
                        "paga. Termina con una sola pregunta o propuesta para avanzar.")),
                    LLMMessage("user", memoria.context(db, project, goal, nivel)[:3000] + "\n\n" + report[:9000]),
                ], max_tokens=900)
                told = (resp.content or "").strip()
            except Exception:  # noqa: BLE001 - sin resumen, se muestran los pasos tal cual
                told = ""
        timeline.post(db, project, told or report[:2500], agent="producto", nivel=nivel, recorrido=True,
                      reaccion={"agente": "producto", "emocion": "feliz", "frase": "¡Recorrí tu página!"})
        db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("El recorrido en segundo plano falló")
    finally:
        db.close()


async def review_later(bind, llm: LLMAdapter, company_id: str, url: str, goal: str, nivel: int, token: str = "") -> None:
    """Mateo revisa el repositorio y deja la revisión en la Sala y en la Biblioteca."""
    db = Session(bind=bind)
    try:
        project = _project(db, company_id)
        if project is None:
            return
        try:
            with usage_scope(db, company_id, level=nivel):
                data = await repositorio.fetch(url, llm, goal, token)
                text = await repositorio.review(llm, data, goal, memoria.context(db, project, goal, nivel))
        except repositorio.RepoError as exc:
            timeline.post(db, project, str(exc), agent="cto", nivel=nivel, revision_codigo=True)
            db.commit()
            return
        db.add(Document(project_id=project.id, title=f"Revisión de código: {data['repo']}"[:255],
                        content=f"# Revisión de código de {data['repo']}\n\n{text}", doc_type="code_review",
                        origin="generated_by_adan"))
        timeline.post(db, project, f"Revisé el código de **{data['repo']}** ({len(data['archivos'])} archivos clave de "
                                   f"{data['archivos_totales']}).\n\n{text}", agent="cto", nivel=nivel, revision_codigo=True,
                      reaccion={"agente": "cto", "emocion": "pensando", "frase": "Ya leí tu código."})
        db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("La revisión de código falló")
    finally:
        db.close()


JOKES_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["chistes"], "properties": {"chistes": {
    "type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["agente", "texto"],
                               "properties": {"agente": {"type": "string", "enum": list(timeline.TEAM)},
                                              "texto": {"type": "string"}}}}}}


@router.get("/{company_id}/chistes")
async def jokes(company_id: str, db: Session = Depends(get_db), user: User = Depends(llm_user),
                llm: LLMAdapter = Depends(get_llm)):
    """Bromas del equipo sobre ESTE proyecto, para cuando el fundador le da clic a un personaje (una vez al día)."""
    import json
    from datetime import datetime, timedelta, timezone

    get_owned_company(db, company_id, user)
    project = _project(db, company_id)
    doc = db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "chistes") \
        .order_by(Document.updated_at.desc()).first()
    fresh = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=24)
    if doc and doc.updated_at and doc.updated_at.replace(tzinfo=None) > fresh:
        return json.loads(doc.content or '{"chistes": []}')
    try:
        with usage_scope(db, company_id, level=1):
            resp = await llm.chat_json([
                LLMMessage("system", (
                    "Escribe 16 bromas cortas (máximo 18 palabras), amables y de oficina, que el equipo de ADÁN le dice al "
                    "fundador sobre SU proyecto. Estilo: «me voy de vacaciones con tu plataforma», «con este flujo de "
                    "caja no alcanza para las galletas». Reparte entre los personajes según su rol: ceo (ADÁN), cfo "
                    "(Camila, dinero), cmo (Santiago, mercado), cto (Mateo, tecnología), producto (Andrés), legal (Lucía), "
                    "operaciones (Sofía), investigador (Iris). Nada ofensivo; español de Colombia, de tú.")),
                LLMMessage("user", memoria.context(db, project, "", None)[:4000] or "Proyecto en etapa temprana."),
            ], JOKES_SCHEMA, temperature=0.9, max_tokens=1800)
        data = resp.parsed if isinstance(resp.parsed, dict) and resp.parsed.get("chistes") else {"chistes": []}
    except Exception:  # noqa: BLE001 - sin bromas del proyecto quedan las de siempre (en el navegador)
        data = {"chistes": []}
    if data["chistes"]:
        content = json.dumps(data, ensure_ascii=False)
        if doc is None:
            db.add(Document(project_id=project.id, title="Bromas del equipo", doc_type="chistes",
                            origin="generated_by_adan", content=content))
        else:
            doc.content = content
        db.commit()
    return data


@router.post("/{company_id}/recorrido")
async def start_walk(company_id: str, body: WalkBody, background: BackgroundTasks, db: Session = Depends(get_db),
                     user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    get_owned_company(db, company_id, user)
    project = _project(db, company_id)
    note = f"🧭 Recorre {body.url} con este objetivo: {body.objetivo}" + (" (con mi cuenta)" if body.usuario else "")
    msg = timeline.post(db, project, note, role="user", nivel=body.nivel)
    db.commit()
    db.refresh(msg)
    background.add_task(walk_later, db.get_bind(), llm, company_id, body.url.strip(), body.objetivo.strip(), body.nivel,
                        body.usuario, body.clave)
    return {"started": True, "after": msg.id}


@router.post("/{company_id}/repositorio")
async def start_review(company_id: str, body: RepoBody, background: BackgroundTasks, db: Session = Depends(get_db),
                       user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm)):
    get_owned_company(db, company_id, user)
    try:
        repositorio.parse(body.url)
    except repositorio.RepoError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    project = _project(db, company_id)
    msg = timeline.post(db, project, f"💻 Revisa el código de {body.url}" + (f": {body.objetivo}" if body.objetivo else ""),
                        role="user", nivel=body.nivel)
    db.commit()
    db.refresh(msg)
    background.add_task(review_later, db.get_bind(), llm, company_id, body.url.strip(), body.objetivo.strip(), body.nivel,
                        body.token.strip())
    return {"started": True, "after": msg.id}
