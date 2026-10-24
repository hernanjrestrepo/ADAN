"""Constitución de la empresa: ¿el nombre ya existe?, la ruta legal del país que el cliente elija (tipo de
sociedad, régimen tributario, paso a paso) y el borrador de estatutos. Explicado para alguien que no sabe nada.

Cada respuesta investiga en internet (Kimi, $web_search) y cita fuentes. Si la búsqueda no está disponible,
el resultado lo dice (`searched: False`) y nada se presenta como verificado. ADÁN es una IA: no reemplaza a un
abogado ni a un contador, y lo advierte siempre.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.ai.router import for_tier
from app.models.models import Company, Document, Project

DISCLAIMER = ("ADÁN es una inteligencia artificial: esta guía orienta, pero no reemplaza la asesoría de un abogado "
              "y un contador del país. Verifica cada paso en las fuentes oficiales antes de actuar.")

NAME_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["veredicto", "explicacion", "coincidencias", "registros_oficiales", "alternativas"],
    "properties": {
        "veredicto": {"type": "string", "enum": ["libre_probable", "conflicto", "incierto"]},
        "explicacion": {"type": "string"},
        "coincidencias": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["nombre", "tipo", "donde", "fuente"],
            "properties": {"nombre": {"type": "string"}, "tipo": {"type": "string"}, "donde": {"type": "string"},
                           "fuente": {"type": "string"}}}},
        "registros_oficiales": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["nombre", "url", "que_verificar"],
            "properties": {"nombre": {"type": "string"}, "url": {"type": "string"}, "que_verificar": {"type": "string"}}}},
        "alternativas": {"type": "array", "items": {"type": "string"}},
    },
}

_STEP = {
    "type": "object", "additionalProperties": False,
    "required": ["titulo", "que_es", "donde", "url", "documentos", "costo", "tiempo", "errores_comunes"],
    "properties": {"titulo": {"type": "string"}, "que_es": {"type": "string"}, "donde": {"type": "string"},
                   "url": {"type": "string"}, "documentos": {"type": "array", "items": {"type": "string"}},
                   "costo": {"type": "string"}, "tiempo": {"type": "string"},
                   "errores_comunes": {"type": "array", "items": {"type": "string"}}},
}

GUIDE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["pais", "resumen", "tipos_sociedad", "recomendada", "regimenes", "regimen_recomendado", "pasos",
                 "obligaciones", "costo_total", "tiempo_total", "fuentes"],
    "properties": {
        "pais": {"type": "string"},
        "resumen": {"type": "string"},
        "tipos_sociedad": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["nombre", "para_quien", "ventajas", "desventajas", "socios", "responsabilidad"],
            "properties": {"nombre": {"type": "string"}, "para_quien": {"type": "string"},
                           "ventajas": {"type": "array", "items": {"type": "string"}},
                           "desventajas": {"type": "array", "items": {"type": "string"}},
                           "socios": {"type": "string"}, "responsabilidad": {"type": "string"}}}},
        "recomendada": {"type": "object", "additionalProperties": False, "required": ["nombre", "por_que"],
                        "properties": {"nombre": {"type": "string"}, "por_que": {"type": "string"}}},
        "regimenes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["nombre", "quien_puede", "como_funciona", "conviene_si"],
            "properties": {"nombre": {"type": "string"}, "quien_puede": {"type": "string"},
                           "como_funciona": {"type": "string"}, "conviene_si": {"type": "string"}}}},
        "regimen_recomendado": {"type": "object", "additionalProperties": False, "required": ["nombre", "por_que"],
                                "properties": {"nombre": {"type": "string"}, "por_que": {"type": "string"}}},
        "pasos": {"type": "array", "items": _STEP},
        "obligaciones": {"type": "array", "items": {"type": "string"}},
        "costo_total": {"type": "string"},
        "tiempo_total": {"type": "string"},
        "fuentes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["nombre", "url"],
            "properties": {"nombre": {"type": "string"}, "url": {"type": "string"}}}},
    },
}

EXPERT = ("Eres el área legal y tributaria de ADÁN. Explicas a una persona que NO sabe nada de empresas: cada "
          "término técnico se explica la primera vez con palabras sencillas y un ejemplo. Eres preciso: cifras, "
          "nombres de entidades y leyes vigentes, con la fuente oficial (sitio .gov o de la entidad) y su fecha. Si "
          "algo cambió recientemente o no estás seguro, lo dices. Español, de tú.")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def company_context(db: Session, project: Project, company: Company) -> str:
    """Qué es la empresa, para que la guía y el nombre se piensen para ella (no en abstracto)."""
    digest = db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "client_docs_digest") \
        .order_by(Document.created_at.desc()).first()
    parts = [f"Empresa: {company.name}", f"Sector: {company.industry or 'sin dato'}", f"País actual: {company.country or 'sin dato'}"]
    if company.description:
        parts.append(f"Descripción: {company.description}")
    if digest and digest.content:
        parts.append("Lo que ADÁN sabe de su documentación:\n" + digest.content[:2500])
    return "\n".join(parts)


class Constitucion:
    def __init__(self, llm: LLMAdapter, db: Session):
        self.llm = for_tier(llm, "standard")
        self.db = db

    async def _research(self, question: str) -> tuple[str, bool]:
        search = getattr(self.llm, "chat_search", None)
        messages = [LLMMessage("system", EXPERT), LLMMessage("user", question)]
        if search is None:  # un adaptador sin búsqueda (pruebas, modelo local)
            resp = await self.llm.chat(messages, max_tokens=4096)
            return resp.content, False
        resp = await search(messages, max_tokens=6000)
        return resp.content, bool(resp.metadata.get("searched"))

    async def _structure(self, instructions: str, research: str, schema: dict, max_tokens: int = 6000) -> dict:
        resp = await self.llm.chat_json([LLMMessage("system", EXPERT + "\n\n" + instructions),
                                         LLMMessage("user", "Investigación hecha:\n\n" + research)],
                                        schema, temperature=0.2, max_tokens=max_tokens)
        return resp.parsed if isinstance(resp.parsed, dict) else {}

    async def check_name(self, name: str, country: str, context: str) -> dict:
        research, searched = await self._research(
            f"Quiero crear una empresa llamada «{name}» en {country or 'mi país'}.\n{context}\n\n"
            f"Investiga en internet: ¿existen empresas registradas, marcas registradas, apps o sitios web con ese nombre "
            f"o uno muy parecido en {country or 'el país'} o en el mismo sector en otros países? Revisa el registro "
            "mercantil y el de marcas del país. Cita cada hallazgo con su fuente (URL).")
        data = await self._structure(
            "Estructura la investigación. `veredicto`: libre_probable si no hay coincidencias relevantes, conflicto "
            "si hay una empresa o marca igual o muy parecida en el mismo sector o país, incierto si no se pudo "
            "verificar bien. `explicacion`: qué significa para el cliente, en 2 a 4 frases sencillas (incluye que "
            "solo el registro oficial lo confirma). `coincidencias`: lo que se encontró, con la URL en `fuente`. "
            "`registros_oficiales`: dónde verificarlo oficialmente en el país (registro mercantil y de marcas), con "
            "URL y qué buscar. `alternativas`: 5 nombres alternativos si hay conflicto o incertidumbre, que "
            "conserven la idea.", research, NAME_SCHEMA, 3000)
        return {"name": name, "country": country, "searched": searched, **data,
                "disclaimer": "Esta búsqueda orienta; solo el registro mercantil y la oficina de marcas del país lo confirman."}

    async def legal_guide(self, project: Project, country: str, context: str) -> dict:
        research, searched = await self._research(
            f"Voy a constituir esta empresa en {country}:\n{context}\n\n"
            f"Investiga en fuentes oficiales vigentes de {country}: 1) los tipos de sociedad posibles y cuál conviene; "
            "2) los regímenes tributarios para una empresa nueva y cuál conviene; 3) el paso a paso completo para "
            "constituirla y empezar a operar legalmente (registro mercantil, identificación tributaria, cuenta bancaria, "
            "facturación electrónica, permisos del sector, seguridad social, registro de marca), con la entidad, el "
            "sitio oficial, los documentos, el costo aproximado en moneda local y el tiempo de cada paso; 4) las "
            "obligaciones del primer año. Cita las fuentes.")
        data = await self._structure(
            "Arma la ruta legal completa para este cliente. `resumen`: 3 frases sencillas. `tipos_sociedad`: de 2 a "
            "4 opciones reales del país, cada una explicada. `recomendada`: la que conviene a ESTA empresa y por "
            "qué. `regimenes` y `regimen_recomendado`: igual para impuestos. `pasos`: de 8 a 14 pasos en orden, cada "
            "uno con: qué es (explicado como a alguien que no sabe nada), dónde se hace, la URL oficial, los "
            "documentos, el costo aproximado en moneda local, el tiempo y los errores comunes que hay que evitar. "
            "`obligaciones`: lo que hay que cumplir el primer año (declaraciones, nómina, renovaciones). "
            "`costo_total` y `tiempo_total`: estimados. `fuentes`: las oficiales usadas, con URL.", research, GUIDE_SCHEMA, 8000)
        guide = {**data, "pais": data.get("pais") or country, "searched": searched, "generated_at": _now(),
                 "done": [False] * len(data.get("pasos") or []), "disclaimer": DISCLAIMER}
        doc = Document(project_id=project.id, title=f"Ruta legal: {guide['pais']}"[:255], doc_type="legal_guide",
                       origin="generated_by_adan", content=json.dumps(guide, ensure_ascii=False))
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return {"id": doc.id, **guide}

    def latest_guide(self, project: Project) -> tuple[Document, dict] | None:
        doc = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "legal_guide") \
            .order_by(Document.created_at.desc()).first()
        return (doc, json.loads(doc.content)) if doc and doc.content else None

    def mark_step(self, project: Project, index: int, done: bool) -> dict:
        found = self.latest_guide(project)
        if not found:
            raise LookupError("Todavía no hay ruta legal")
        doc, guide = found
        if not 0 <= index < len(guide.get("pasos") or []):
            raise IndexError("Ese paso no existe")
        guide["done"][index] = done
        doc.content = json.dumps(guide, ensure_ascii=False)
        doc.version += 1
        self.db.commit()
        return {"id": doc.id, **guide}

    async def statutes(self, project: Project, company: Company, data: dict) -> Document:
        partners = "\n".join(f"- {p.get('nombre')} ({p.get('documento') or 'documento por definir'}): aporte "
                             f"{p.get('aporte') or 'por definir'}, {p.get('porcentaje') or '?'} %" for p in data.get("socios") or [])
        prompt = (
            f"Redacta el borrador completo de los estatutos de constitución de esta empresa, según la ley vigente de "
            f"{data['pais']}, para el tipo de sociedad «{data['tipo']}».\n\n"
            f"Razón social: {data.get('nombre') or company.name}\nDomicilio: {data.get('domicilio') or 'por definir'}\n"
            f"Objeto social: {data.get('objeto') or company.description or 'por definir'}\n"
            f"Capital: {data.get('capital') or 'por definir'}\nAdministración: {data.get('administracion') or 'por definir'}\n"
            f"Socios o accionistas:\n{partners or '- por definir'}\n\n"
            "Formato Markdown: título, capítulos con `##` y artículos numerados en negrilla. Incluye todo lo que la ley "
            "exige (nombre, domicilio, término, objeto, capital y acciones o cuotas, órganos de dirección y "
            "administración, representación legal, reuniones y mayorías, utilidades y reservas, disolución y "
            "liquidación, solución de conflictos) y cláusulas útiles para socios nuevos (transferencia de acciones, "
            "salida de socios). Donde falte un dato escribe [COMPLETAR: qué va aquí]. Al inicio, una nota de 3 líneas "
            "que explique qué es este documento y que debe revisarlo un abogado antes de firmarlo.")
        resp = await self.llm.chat([LLMMessage("system", EXPERT), LLMMessage("user", prompt)], temperature=0.2, max_tokens=8000)
        doc = Document(project_id=project.id, title=f"Estatutos: {data.get('nombre') or company.name} ({data['tipo']}, {data['pais']})"[:255],
                       doc_type="statutes", origin="generated_by_adan", content=resp.content.strip())
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc


def markdown_to_docx(markdown: str, title: str) -> bytes:
    """Los estatutos en Word, para editarlos y llevarlos al abogado."""
    import io
    import re

    from docx import Document as Docx

    doc = Docx()
    doc.core_properties.title = title
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=0)
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=1)
        elif line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
        elif re.match(r"^\s*[-*] ", line):
            _runs(doc.add_paragraph(style="List Bullet"), re.sub(r"^\s*[-*] ", "", line))
        else:
            _runs(doc.add_paragraph(), line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _runs(paragraph, text: str) -> None:
    import re

    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if part:
            paragraph.add_run(part).bold = i % 2 == 1
