"""Biblioteca de la empresa: todo lo que se va construyendo (marca, paleta, logos, manual, estatutos, trámites,
números, actas e informes, y lo que subió el fundador) en un solo lugar, ordenado por sección y por Nivel."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.levels import entregables
from app.models.models import Company, Document, Project

# doc_type → sección, Nivel donde nace, cómo se ve, herramienta que lo produce y descarga propia
SECTIONS = {
    "marca": "Marca e identidad",
    "legal": "Legal y constitución",
    "numeros": "Números",
    "estrategia": "Estrategia y validación",
    "board": "Board y Arena",
    "cliente": "Tus archivos",
}

TYPES: dict[str, dict] = {
    "diagnosis": {"seccion": "estrategia", "nivel": 1, "titulo": "Diagnóstico"},
    "survey": {"seccion": "estrategia", "nivel": 1, "titulo": "Encuesta"},
    "level_summary": {"seccion": "estrategia", "nivel": None, "titulo": "Resumen de Nivel"},
    "recommendation": {"seccion": "estrategia", "nivel": None, "titulo": "Recomendación"},
    "statutes": {"seccion": "legal", "nivel": 3, "titulo": "Estatutos", "herramienta": "/constitucion",
                 "descarga": "/constitucion/{cid}/estatutos/{id}.docx"},
    "legal_guide": {"seccion": "legal", "nivel": 3, "titulo": "Ruta legal", "herramienta": "/constitucion"},
    "expediente_paquete": {"seccion": "legal", "nivel": 3, "titulo": "Paquete de trámite", "herramienta": "/expediente",
                           "descarga": "/empresa/{cid}/expediente/paquete/{id}.docx"},
    "expediente_soporte": {"seccion": "legal", "nivel": 3, "titulo": "Soporte validado", "herramienta": "/expediente"},
    "financial_model": {"seccion": "numeros", "nivel": 3, "titulo": "Modelo financiero y flujo de caja",
                        "herramienta": "/finanzas", "descarga": "/finanzas/{cid}/modelo.xlsx", "ext": "xlsx"},
    "org_chart": {"seccion": "numeros", "nivel": 3, "titulo": "Organigrama", "herramienta": "/finanzas"},
    "executive_report": {"seccion": "numeros", "nivel": 3, "titulo": "Informe ejecutivo", "herramienta": "/finanzas",
                         "descarga": "/finanzas/{cid}/informe.docx"},
    "board_minutes": {"seccion": "board", "nivel": 3, "titulo": "Acta del Board"},
    "board_override": {"seccion": "board", "nivel": 3, "titulo": "Decisión bajo tu responsabilidad"},
    "arena": {"seccion": "board", "nivel": 5, "titulo": "Sesión de La Arena"},
    "libro_empresa": {"seccion": "estrategia", "nivel": 7, "titulo": "Libro de la Empresa"},
    "code_review": {"seccion": "estrategia", "nivel": 4, "titulo": "Revisión de código"},
    "client_upload": {"seccion": "cliente", "nivel": None, "titulo": "Archivo subido"},
    "web_page": {"seccion": "cliente", "nivel": None, "titulo": "Página web leída"},
}

# Lo que sólo es estado interno (o ya se muestra resumido en otra parte) no se lista como documento
HIDDEN = {"marca", "expediente", "board_dialogue", "client_docs_digest", "memoria_proyecto", "chistes", "graduacion", "seguimiento", "mvp_sitio"}


def _is_json(text: str | None) -> bool:
    if not text:
        return False
    try:
        return isinstance(json.loads(text), (dict, list))
    except (json.JSONDecodeError, ValueError):
        return False


def _brand(db: Session, project: Project, company: Company) -> dict:
    doc = db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "marca") \
        .order_by(Document.updated_at.desc()).first()
    try:
        marca = json.loads(doc.content) if doc and doc.content else {}
    except json.JSONDecodeError:
        marca = {}
    logo = marca.get("logo_elegido") or {}
    palette = [{"nombre": n, "hex": logo[k]} for n, k in (("Primario", "primario"), ("Acento", "acento"), ("Fondo", "fondo"))
               if logo.get(k)]
    if not palette:
        palette = [{"nombre": n, "hex": v} for n, v in (("Primario", company.brand_color), ("Acento", company.brand_accent)) if v]
    return {
        "nombre": company.name, "slogan": marca.get("slogan") or "", "logo": company.logo,
        "logo_concepto": logo.get("nombre_concepto") or "", "tipografia": logo.get("tipografia") or "",
        "paleta": palette, "manual": bool(marca.get("manual")),
        "nombres_considerados": [n.get("nombre") for n in marca.get("nombres") or []][:10],
        "slogans_considerados": [s.get("texto") for s in marca.get("slogans") or []][:10],
    }


def catalog(db: Session, project: Project, company: Company) -> dict:
    docs = db.query(Document).filter(Document.project_id == project.id).order_by(Document.updated_at.desc()).all()
    items = []
    for d in docs:
        if d.doc_type in HIDDEN:
            continue
        meta = TYPES.get(d.doc_type, {"seccion": "estrategia", "nivel": None, "titulo": "Documento"})
        if d.doc_type == entregables.DOC_TYPE:
            meta = {"seccion": entregables.section_of(d.title), "nivel": entregables.level_of(d.title), "titulo": "Entregable"}
        data = _is_json(d.content)
        download = meta.get("descarga")
        if not download and not data and d.content:
            download = "/empresa/{cid}/biblioteca/{id}.docx"
        items.append({
            "id": d.id, "titulo": d.title, "tipo": meta["titulo"], "seccion": meta["seccion"], "nivel": meta["nivel"],
            "origen": "tuyo" if d.origin == "received_from_client" else "adan",
            "creado": d.created_at.isoformat() if d.created_at else None,
            "actualizado": d.updated_at.isoformat() if d.updated_at else None,
            "legible": bool(d.content) and not data,
            "herramienta": f"{meta['herramienta']}/{company.id}" if meta.get("herramienta") else None,
            "descarga": download.format(cid=company.id, id=d.id) if download else None,
            "ext": meta.get("ext", "docx"),
            "palabras": len((d.content or "").split()) if not data else None,
        })
    brand = _brand(db, project, company)
    if brand["manual"]:
        items.insert(0, {"id": "manual", "titulo": "Manual de marca", "tipo": "Manual de marca", "seccion": "marca",
                         "nivel": 2, "origen": "adan", "creado": None, "actualizado": None, "legible": True,
                         "herramienta": f"/marca/{company.id}", "descarga": f"/empresa/{company.id}/marca/manual.docx",
                         "ext": "docx", "palabras": None})
    from app.nivel1 import memoria  # la memoria del proyecto que custodia ADÁN, visible para el fundador

    pending = entregables.missing(db, project)
    return {"marca": brand, "secciones": SECTIONS, "documentos": items,
            "faltan": [{"nivel": n, "entregables": names} for n, names in sorted(pending.items())],
            "memoria": list(reversed(memoria.load(db, project)["acuerdos"])),
            "ficha": memoria.load(db, project).get("ficha", {})}


def read(db: Session, project: Project, doc_id: str) -> Document | None:
    doc = db.query(Document).filter(Document.project_id == project.id, Document.id == doc_id).first()
    if doc is None or doc.doc_type in HIDDEN or _is_json(doc.content):
        return None
    return doc
