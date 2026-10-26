"""La memoria del proyecto, custodiada por ADÁN y compartida con todo el equipo en cada turno.

Tres partes:
- Libro de acuerdos: lo decidido, lo descartado («no volver a preguntar») y los datos confirmados por el fundador.
  Se actualiza cada turno con lo que el modelo detecta y viaja a todos los Niveles, al Board y a La Arena.
- Resúmenes: lo esencial de las conversaciones largas (lo viejo que ya no cabe en la ventana de mensajes).
- Fragmentos (chunks) de la Biblioteca: páginas leídas, archivos subidos, paquetes y actas, partidos en trozos;
  en cada turno entran los más relacionados con lo que el fundador está diciendo.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models.models import Company, Document, Project, User

DOC_TYPE = "memoria_proyecto"
KINDS = {"decidido": "Decidido", "descartado": "Descartado (no volver a proponerlo ni preguntarlo)",
         "dato": "Dato confirmado por el fundador", "pendiente": "Pendiente acordado"}
MAX_AGREEMENTS = 80
CHUNK_CHARS = 900
MAX_CHUNKS = 4
# Documentos de la Biblioteca que alimentan los fragmentos (los JSON de estado interno no)
CHUNK_TYPES = ("web_page", "code_review", "client_upload", "expediente_paquete", "board_minutes", "level_summary", "legal_guide",
               "statutes", "diagnosis", "executive_report")
_WORD = re.compile(r"[a-záéíóúñü0-9]{4,}", re.I)


def _doc(db: Session, project: Project) -> Document | None:
    return db.query(Document).filter(Document.project_id == project.id, Document.doc_type == DOC_TYPE) \
        .order_by(Document.updated_at.desc()).first()


def load(db: Session, project: Project) -> dict:
    doc = _doc(db, project)
    try:
        data = json.loads(doc.content) if doc and doc.content else {}
    except json.JSONDecodeError:
        data = {}
    data.setdefault("acuerdos", [])
    data.setdefault("resumenes", {})
    return data


def save(db: Session, project: Project, data: dict) -> None:
    doc = _doc(db, project)
    content = json.dumps(data, ensure_ascii=False)
    if doc is None:
        db.add(Document(project_id=project.id, title="Memoria del proyecto", doc_type=DOC_TYPE,
                        origin="generated_by_adan", content=content))
    else:
        doc.content = content
    db.commit()


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def remember(db: Session, project: Project, items: list, nivel: int) -> int:
    """Agrega los acuerdos nuevos del turno; uno parecido a uno anterior lo reemplaza (la corrección manda)."""
    clean = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        kind, text = it.get("tipo"), str(it.get("texto", "")).strip()
        if kind in KINDS and 8 <= len(text) <= 300:
            clean.append((kind, text))
    if not clean:
        return 0
    data = load(db, project)
    agreements = data["acuerdos"]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for kind, text in clean:
        same = next((a for a in agreements if _similar(a["texto"], text) > 0.72), None)
        if same is not None:
            same.update({"tipo": kind, "texto": text, "nivel": nivel, "fecha": now})
        else:
            agreements.append({"tipo": kind, "texto": text, "nivel": nivel, "fecha": now})
    data["acuerdos"] = agreements[-MAX_AGREEMENTS:]
    save(db, project, data)
    return len(clean)


def set_summary(db: Session, project: Project, key: str, text: str, covered: int) -> None:
    data = load(db, project)
    data["resumenes"][key] = {"texto": text[:4000], "mensajes": covered}
    save(db, project, data)


def summary_of(db: Session, project: Project, key: str) -> dict:
    return load(db, project)["resumenes"].get(key) or {}


def founder_name(db: Session, project: Project) -> str:
    company = db.get(Company, project.company_id)
    user = db.get(User, company.primary_user_id) if company else None
    return (user.name or "").strip() if user else ""


def chunks(db: Session, project: Project, query: str, limit: int = MAX_CHUNKS) -> list[tuple[str, str]]:
    """Los fragmentos de la Biblioteca que más se relacionan con `query` (por palabras compartidas)."""
    words = {w.lower() for w in _WORD.findall(query or "")}
    if not words:
        return []
    docs = db.query(Document).filter(Document.project_id == project.id, Document.doc_type.in_(CHUNK_TYPES)) \
        .order_by(Document.updated_at.desc()).limit(40).all()
    scored = []
    for d in docs:
        text = d.content or ""
        if text.lstrip().startswith(("{", "[")):
            continue
        for i in range(0, min(len(text), 30_000), CHUNK_CHARS):
            piece = text[i:i + CHUNK_CHARS]
            hits = len(words & {w.lower() for w in _WORD.findall(piece)})
            if hits >= 2:
                scored.append((hits, d.title, piece))
    scored.sort(key=lambda s: -s[0])
    out, seen = [], set()
    for _, title, piece in scored:
        if (title, piece[:50]) in seen:
            continue
        seen.add((title, piece[:50]))
        out.append((title, piece.strip()))
        if len(out) >= limit:
            break
    return out


def context(db: Session, project: Project, query: str = "", nivel: int | None = None) -> str:
    """El bloque de memoria que reciben todos los agentes."""
    data = load(db, project)
    parts = []
    name = founder_name(db, project)
    if name:
        parts.append(f"El fundador se llama {name}. Andrés, Camila, Santiago, Mateo, Lucía, Sofía e Iris son del equipo de "
                     f"ADÁN: nunca llames así al fundador.")
    if data["acuerdos"]:
        by_kind: dict[str, list[str]] = {}
        for a in data["acuerdos"]:
            by_kind.setdefault(a["tipo"], []).append(f"{a['texto']} (Nivel {a.get('nivel', '?')})")
        lines = []
        for kind, label in KINDS.items():
            if by_kind.get(kind):
                lines.append(f"{label}:\n" + "\n".join(f"- {t}" for t in by_kind[kind][-25:]))
        parts.append("LIBRO DE ACUERDOS (manda sobre todo lo demás; no lo contradigas ni vuelvas a preguntarlo):\n"
                     + "\n".join(lines))
    summaries = [(k, v) for k, v in data["resumenes"].items() if v.get("texto")]
    if summaries:
        parts.append("Resumen de lo conversado antes:\n" + "\n".join(
            f"[{k}] {v['texto'][:1500]}" for k, v in sorted(summaries)))
    found = chunks(db, project, query)
    if found:
        parts.append("Fragmentos de la Biblioteca relacionados con lo que dice el fundador:\n" + "\n\n".join(
            f"«{title}»: {piece}" for title, piece in found))
    if not parts:
        return ""
    return "MEMORIA DEL PROYECTO (la custodia ADÁN; todo el equipo la conoce):\n" + "\n\n".join(parts)
