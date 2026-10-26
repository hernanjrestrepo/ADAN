"""Genexis, el constructor del MVP (Nivel 4).

Para una empresa que es idea: escribe la especificación del producto, construye una landing de validación con la
marca (incluida en el Nivel 4) y un prototipo navegable (cobrado aparte en @pples), los publica en ADÁN con su
enlace, los ajusta conversando y entrega el código descargable. Para una empresa que ya tiene producto: lo
recorre, lee su código si lo hay y deja un plan de mejoras con cotización.

Las páginas se generan con IA y se sirven con una política de seguridad «sandbox»: corren en un origen aislado,
sin acceso a la sesión de ADÁN. El formulario de interesados lo pone ADÁN (no la IA), con la autorización de
datos de la Ley 1581 a nombre de la empresa del fundador.
"""
from __future__ import annotations

import html
import io
import json
import re
import unicodedata
import uuid
import zipfile
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.router import for_tier
from app.apples import pricing
from app.empresa.service import Marca
from app.models.models import Company, Document, Project
from app.nivel1 import memoria

SITE_DOC = "mvp_sitio"
CONSENT_VERSION = "v1-2026-10"
LOGO = "{{LOGO}}"
FORM = "<!--FORMULARIO-->"
# Lo que cuesta construir y ajustar el prototipo (tokens estimados de Kimi, con la regla costo ÷ 0,10)
PROTOTYPE_TOKENS = (60_000, 26_000)
TWEAK_TOKENS = (30_000, 16_000)
FREE_TWEAKS = 3

BUILDER = (
    "Eres Genexis, el constructor de ADÁN: diseñas y programas páginas web modernas, rápidas y hermosas. Devuelves "
    "UN SOLO archivo HTML completo (empieza en <!DOCTYPE html>), con todo el CSS y el JavaScript dentro del "
    "archivo, responsive (se ve perfecto en celular), accesible y en el idioma del mercado de la empresa. Usa la "
    "marca de la empresa: sus colores (variables CSS), su nombre, su slogan y su logo con <img src=\"{{LOGO}}\">. "
    "Puedes usar Google Fonts. No uses otras librerías externas, ni imágenes de internet (usa formas, degradados, "
    "emojis o SVG en línea). Nada de datos inventados presentados como reales: si muestras cifras o testimonios, "
    "que sean ejemplos marcados como tales. Donde va el formulario de interesados escribe exactamente "
    "<!--FORMULARIO--> (ADÁN pone ahí el formulario con la autorización de datos). Solo el HTML, sin explicaciones."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(text: str) -> str:
    s = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "empresa"


def quote(tokens: tuple[int, int]) -> int:
    return pricing.mvp_quote(*tokens)["apples"]


def _sites(db: Session, project: Project) -> list[Document]:
    return db.query(Document).filter(Document.project_id == project.id, Document.doc_type == SITE_DOC) \
        .order_by(Document.created_at).all()


def site_doc(db: Session, project: Project, tipo: str) -> Document | None:
    return next((d for d in _sites(db, project) if json.loads(d.content or "{}").get("tipo") == tipo), None)


def by_slug(db: Session, slug: str) -> tuple[Document, dict] | tuple[None, None]:
    for d in db.query(Document).filter(Document.doc_type == SITE_DOC, Document.title == f"sitio:{slug}").all():
        return d, json.loads(d.content or "{}")
    return None, None


def save_site(db: Session, project: Project, company: Company, tipo: str, **changes) -> dict:
    doc = site_doc(db, project, tipo)
    data = json.loads(doc.content) if doc else {
        "tipo": tipo, "slug": f"{slugify(company.name)}-{tipo[:4]}-{uuid.uuid4().hex[:4]}", "version": 0, "html": "",
        "estado": "vacio", "ajustes": 0, "creado": _now()}
    data.update(changes)
    data["actualizado"] = _now()
    if doc is None:
        db.add(Document(project_id=project.id, title=f"sitio:{data['slug']}", doc_type=SITE_DOC,
                        origin="generated_by_adan", content=json.dumps(data, ensure_ascii=False)))
    else:
        doc.content = json.dumps(data, ensure_ascii=False)
    db.commit()
    return data


def consent_text(company_name: str) -> str:
    return (f"Autorizo a {company_name} a tratar mis datos (nombre, correo y celular) para contactarme sobre su "
            "producto, de acuerdo con la Ley 1581 de 2012 de protección de datos personales. Puedo conocer, "
            f"actualizar, rectificar o pedir que se eliminen mis datos en cualquier momento a través de los canales "
            f"de contacto de {company_name}.")


def form_html(slug: str, company_name: str, color: str) -> str:
    """El formulario de interesados: lo pone ADÁN, nunca la IA, con la autorización de datos."""
    c = html.escape(color or "#2563eb")
    return (
        f'<form method="post" action="/api/v1/sitio/{html.escape(slug)}/interes" '
        'style="display:grid;gap:10px;max-width:420px;margin:0 auto;text-align:left;font-family:inherit">'
        '<input name="nombre" placeholder="Tu nombre" maxlength="120" required '
        'style="padding:12px;border-radius:10px;border:1px solid #cbd5e1;font-size:16px">'
        '<input name="correo" type="email" placeholder="Tu correo" maxlength="200" required '
        'style="padding:12px;border-radius:10px;border:1px solid #cbd5e1;font-size:16px">'
        '<input name="celular" placeholder="Tu celular (opcional)" maxlength="40" '
        'style="padding:12px;border-radius:10px;border:1px solid #cbd5e1;font-size:16px">'
        '<textarea name="mensaje" placeholder="¿Qué te gustaría resolver? (opcional)" maxlength="1000" rows="3" '
        'style="padding:12px;border-radius:10px;border:1px solid #cbd5e1;font-size:16px"></textarea>'
        '<label style="display:flex;gap:8px;align-items:flex-start;font-size:12px;line-height:1.4;color:#475569">'
        f'<input type="checkbox" name="autorizo" value="si" required style="margin-top:2px"> {html.escape(consent_text(company_name))}</label>'
        f'<button type="submit" style="padding:14px;border:0;border-radius:12px;background:{c};color:#fff;font-size:16px;'
        'font-weight:700;cursor:pointer">Quiero saber más</button></form>'
    )


def render(data: dict, identity: dict, company_name: str) -> str:
    """El HTML listo para servir: con el logo y el formulario de ADÁN."""
    page = data.get("html") or ""
    logo = identity.get("logo") or ""
    if not logo:
        initial = html.escape((company_name or "?")[:1].upper())
        color = identity.get("color") or "#2563eb"
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" '
               f'fill="{color}"/><text x="32" y="43" font-size="34" text-anchor="middle" fill="#fff" '
               f'font-family="Arial">{initial}</text></svg>')
        import base64
        logo = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
    page = page.replace(LOGO, logo)
    form = form_html(data["slug"], company_name, identity.get("color") or "")
    return page.replace(FORM, form) if FORM in page else page.replace("</body>", f'<section style="padding:40px 16px">{form}</section></body>')


def _clean_html(text: str) -> str:
    text = (text or "").strip()
    m = re.search(r"```(?:html)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    start = text.lower().find("<!doctype html")
    if start < 0:
        start = text.lower().find("<html")
    return text[start:] if start >= 0 else ""


class Genexis:
    def __init__(self, llm: LLMAdapter | None, db: Session):
        self.llm = for_tier(llm, "complex") if llm is not None else None
        self.db = db

    async def _write(self, messages: list[LLMMessage], max_tokens: int) -> str:
        """Escribe en streaming: una página completa tarda más que la espera de una respuesta normal."""
        parts = []
        async for token in self.llm.chat_stream(messages, temperature=0.6, max_tokens=max_tokens):
            parts.append(token)
        return "".join(parts)

    def _context(self, project: Project) -> str:
        memory = memoria.context(self.db, project, query="producto propuesta de valor cliente MVP alcance", nivel=4)
        spec = self._spec_doc(project)
        delivered = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "entregable",
                                                   Document.title.like("Nivel %")).order_by(Document.title).limit(20).all()
        parts = [memory[:7000]]
        if spec:
            parts.append("Especificación del producto (Genexis):\n" + (spec.content or "")[:6000])
        parts += [f"### {d.title}\n{(d.content or '')[:600]}" for d in delivered if "Nivel 2" in d.title or "Nivel 4" in d.title]
        return "\n\n".join(p for p in parts if p)

    def _spec_doc(self, project: Project) -> Document | None:
        return self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "entregable",
                                              Document.title == SPEC_TITLE).first()

    async def spec(self, project: Project, company: Company) -> Document:
        resp = await self.llm.chat([
            LLMMessage("system", (
                "Eres Genexis, arquitecto de producto de ADÁN. Escribe la especificación del MVP de esta empresa en "
                "Markdown: 1) problema y cliente, 2) propuesta de valor, 3) alcance del MVP (lo que entra y lo que NO "
                "entra), 4) historias de usuario priorizadas (formato «Como… quiero… para…» con criterios de "
                "aceptación), 5) pantallas y flujo principal, 6) modelo de datos (entidades y campos), 7) "
                "integraciones (pagos, mensajería, etc.), 8) métricas de éxito del MVP, 9) riesgos técnicos. Solo lo "
                "que sale de la memoria y los acuerdos; si algo es supuesto, márcalo. Español, máximo 1.200 palabras.")),
            LLMMessage("user", f"Empresa: {company.name}\n\n{self._context(project)}"),
        ], max_tokens=5000)
        text = (resp.content or "").strip()
        if not text or resp.metadata.get("degraded"):
            raise RuntimeError("Genexis no pudo escribir la especificación en este momento.")
        doc = self._spec_doc(project)
        if doc is None:
            doc = Document(project_id=project.id, title=SPEC_TITLE, doc_type="entregable", origin="generated_by_adan",
                           content=text)
            self.db.add(doc)
        else:
            doc.content = text
        self.db.commit()
        self.db.refresh(doc)
        return doc

    async def build(self, project: Project, company: Company, tipo: str) -> dict:
        identity = Marca(None, self.db).identity(company, project)
        what = ("una LANDING de validación de una sola página: promesa clara arriba, el dolor que resuelve, cómo "
                "funciona en 3 pasos, beneficios, preguntas frecuentes y el formulario de interesados (escribe "
                "<!--FORMULARIO--> en la sección de contacto)" if tipo == "landing" else
                "un PROTOTIPO NAVEGABLE del producto: las pantallas principales del flujo de la especificación "
                "(inicio, el flujo central paso a paso, resultado o confirmación y un panel del usuario), con "
                "navegación real entre pantallas en JavaScript, datos de ejemplo realistas marcados como ejemplo y "
                "una barra discreta que diga «Prototipo de demostración». Que se sienta como el producto real.")
        text = await self._write([
            LLMMessage("system", BUILDER),
            LLMMessage("user", (f"Construye {what}\n\nMarca: nombre «{identity['nombre']}», slogan «{identity['slogan']}», "
                                f"color principal {identity.get('color') or '#2563eb'}, acento "
                                f"{identity.get('acento') or '#f59e0b'}.\n\nLo que se sabe de la empresa:\n"
                                f"{self._context(project)}")),
        ], 16000)
        page = _clean_html(text)
        if not page:
            raise RuntimeError("Genexis no pudo construir la página en este momento.")
        doc = site_doc(self.db, project, tipo)
        version = (json.loads(doc.content).get("version", 0) if doc else 0) + 1
        return save_site(self.db, project, company, tipo, html=page, version=version, estado="listo", error="")

    async def tweak(self, project: Project, company: Company, tipo: str, instruction: str) -> dict:
        doc = site_doc(self.db, project, tipo)
        data = json.loads(doc.content) if doc else {}
        if not data.get("html"):
            raise RuntimeError("Primero construye la página.")
        text = await self._write([
            LLMMessage("system", BUILDER + " Te dan una página que ya existe y un cambio: aplica SOLO ese cambio y "
                                           "devuelve la página completa."),
            LLMMessage("user", f"Cambio pedido por el fundador: {instruction}\n\nPágina actual:\n{data['html']}"),
        ], 16000)
        page = _clean_html(text)
        if not page:
            raise RuntimeError("Genexis no pudo aplicar el cambio en este momento.")
        return save_site(self.db, project, company, tipo, html=page, version=data.get("version", 0) + 1,
                         estado="listo", error="", ajustes=data.get("ajustes", 0) + 1, ultimo_ajuste=instruction[:300])

    def code_zip(self, project: Project, company: Company) -> bytes:
        """El código para seguir desarrollando: las páginas, la especificación y cómo publicarlas."""
        identity = Marca(None, self.db).identity(company, project)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            names = []
            for tipo in ("landing", "prototipo"):
                doc = site_doc(self.db, project, tipo)
                data = json.loads(doc.content) if doc else {}
                if data.get("html"):
                    page = render(data, identity, company.name)
                    z.writestr(f"{tipo}/index.html", page)
                    names.append(tipo)
            spec = self._spec_doc(project)
            if spec:
                z.writestr("especificacion.md", spec.content or "")
            z.writestr("README.md", (
                f"# {company.name} — MVP construido con ADÁN (Genexis)\n\n"
                + "".join(f"- `{n}/index.html`: {'landing de validación' if n == 'landing' else 'prototipo navegable'}\n"
                          for n in names)
                + "- `especificacion.md`: la especificación del producto (historias de usuario, pantallas y datos).\n\n"
                "## Cómo verlo\nAbre cualquier `index.html` en el navegador: no necesita instalar nada.\n\n"
                "## Cómo publicarlo\nArrastra la carpeta a Netlify Drop o Vercel, o súbela a tu hosting.\n\n"
                "## Formulario de interesados\nEn ADÁN, el formulario envía los datos a tu cuenta (con la autorización "
                "de la Ley 1581). Si lo publicas por tu cuenta, cambia el `action` del formulario a tu propio servicio "
                "(por ejemplo Formspree o tu backend) y conserva el texto de autorización.\n\n"
                "## Siguiente paso\nPara el software de producción (pagos, cuentas, base de datos), Paradixe cotiza el "
                "desarrollo a partir de `especificacion.md`.\n"))
        return buf.getvalue()

    async def improvement_plan(self, project: Project, company: Company, walk_report: str) -> Document:
        """Empresa que ya tiene producto: plan de mejoras a partir del recorrido real y del código si se revisó."""
        review = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "code_review") \
            .order_by(Document.created_at.desc()).first()
        resp = await self.llm.chat([
            LLMMessage("system", (
                "Eres Genexis. La empresa YA tiene su producto funcionando: no diseñes un MVP nuevo. Con el recorrido "
                "real por el producto, la revisión de código (si existe) y la memoria, escribe en Markdown el PLAN DE "
                "MEJORAS: 1) lo que funciona bien, 2) fricciones encontradas (con la pantalla o paso), 3) mejoras "
                "priorizadas por impacto en ventas y esfuerzo (tabla), 4) lo que hay que medir, 5) cotización "
                "estimada en horas de desarrollo por mejora (marcada como estimación). Español, máximo 900 palabras.")),
            LLMMessage("user", (f"Empresa: {company.name}\n\n{self._context(project)}\n\nRecorrido por el producto:\n"
                                f"{walk_report[:9000]}" + (f"\n\nRevisión de código:\n{(review.content or '')[:6000]}"
                                                           if review else ""))),
        ], max_tokens=4500)
        text = (resp.content or "").strip()
        if not text or resp.metadata.get("degraded"):
            raise RuntimeError("Genexis no pudo escribir el plan de mejoras en este momento.")
        doc = Document(project_id=project.id, title=PLAN_TITLE, doc_type="entregable", origin="generated_by_adan",
                       content=text)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc


SPEC_TITLE = "Nivel 4 · Especificación del producto (Genexis)"
PLAN_TITLE = "Nivel 4 · Plan de mejoras del producto (Genexis)"
