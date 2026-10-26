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
    if data.get("ficha"):
        parts.append("FICHA DE LA EMPRESA (fuente única de verdad: todas las cuentas y afirmaciones salen de aquí; si "
                     "algo la contradice, gana la ficha):\n"
                     + "\n".join(f"- {k}: {v}" for k, v in data["ficha"].items()))
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


# --- Consolidación: memoria sin contradicciones y ficha de parámetros --------------------------------------------

CONSOLIDATE_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["ficha", "acuerdos"],
    "properties": {
        "ficha": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["campo", "valor"],
            "properties": {"campo": {"type": "string"}, "valor": {"type": "string"}}}},
        "acuerdos": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["tipo", "texto", "nivel"],
            "properties": {"tipo": {"type": "string", "enum": list(KINDS)}, "texto": {"type": "string"},
                           "nivel": {"type": "integer"}}}},
    },
}

CONSOLIDATOR = (
    "Eres ADÁN, custodio de la memoria del proyecto. Lees lo que dijo el FUNDADOR en las conversaciones de los "
    "Niveles (sus palabras mandan; lo que propuso el equipo solo cuenta si él lo aprobó) y el libro de acuerdos "
    "actual. Devuelves:\n"
    "1) `ficha`: los parámetros de la empresa como fuente única de verdad, cada uno con `campo` y `valor` corto: "
    "modelo de ingresos, comisión, costos fijos, quién paga la pasarela de pagos, programa de referidos (niveles y "
    "porcentajes), financiamiento (capital propio, deuda, inversión), mercado (geografía, idiomas, nacional o "
    "internacional, B2C/B2B), segmento de clientes, estado del producto (lanzado o no, qué hace), socios y su rol, "
    "canales, metas aprobadas. Solo lo que el fundador dijo o aprobó; si algo no está claro, no lo pongas.\n"
    "2) `acuerdos`: el libro depurado. Si dos acuerdos se contradicen, queda el MÁS RECIENTE (o el que el "
    "fundador corrigió); fusiona duplicados; quita pendientes ya resueltos; incluye lo que el fundador descartó o "
    "pidió no volver a preguntar (tipo «descartado»). Máximo 60, cada uno en una frase. `nivel`: el Nivel donde "
    "se acordó.\n"
    "Nunca inventes: nada de cifras que el fundador no dio. Español."
)


async def consolidate(llm, db: Session, project: Project) -> dict:
    """Recupera los acuerdos de TODAS las conversaciones (también las anteriores a la memoria), resuelve
    contradicciones y arma la ficha de parámetros. Reemplaza el libro de acuerdos."""
    from app.ai.base import LLMMessage
    from app.ai.router import for_tier
    from app.models.models import Card, Conversation, Level, Message

    llm = for_tier(llm, "standard")
    data = load(db, project)
    talks = []
    levels = db.query(Level).filter(Level.project_id == project.id).order_by(Level.number).all()
    for lv in levels:
        cards = db.query(Card).filter(Card.project_id == project.id, Card.level_id == lv.id).all()
        conv_ids = [c.id for card in cards for c in db.query(Conversation).filter(Conversation.card_id == card.id).all()]
        if not conv_ids:
            continue
        msgs = db.query(Message).filter(Message.conversation_id.in_(conv_ids)).order_by(Message.created_at).all()
        lines = []
        for m in msgs:
            if m.role == "user":
                lines.append(f"FUNDADOR: {m.content[:900]}")
            elif not (isinstance(m.metadata_json, dict) and m.metadata_json.get("mesa")):
                lines.append(f"{m.agent_name or 'ADÁN'}: {m.content[:300]}")
        if lines:
            talks.append(f"=== Nivel {lv.number} ===\n" + "\n".join(lines)[-14000:])
    current = "\n".join(f"- [{a['tipo']}, Nivel {a.get('nivel', '?')}] {a['texto']}" for a in data["acuerdos"])

    async def ask(prompt: str) -> dict:
        try:
            resp = await llm.chat_json([LLMMessage("system", CONSOLIDATOR), LLMMessage("user", prompt)],
                                       CONSOLIDATE_SCHEMA, temperature=0.1, max_tokens=3000)
        except Exception:  # noqa: BLE001 - un Nivel que falla no impide consolidar los demás
            return {}
        if resp.metadata.get("degraded"):
            return {}  # el modelo local de respaldo no tiene calidad para reescribir la memoria
        return resp.parsed if isinstance(resp.parsed, dict) else {}

    # Nivel por Nivel (cada conversación cabe holgada) y al final una pasada corta que une y depura
    candidates: list[dict] = []
    fragments: dict[str, str] = {}
    for talk in talks:
        part = await ask("Conversación de un Nivel:\n" + talk)
        candidates += [a for a in part.get("acuerdos", []) if isinstance(a, dict)]
        fragments.update({str(f.get("campo", "")): str(f.get("valor", "")) for f in part.get("ficha", [])
                          if isinstance(f, dict)})
    if not candidates and not fragments:
        return data
    merged = "\n".join(f"- [{a.get('tipo')}, Nivel {a.get('nivel', '?')}] {a.get('texto', '')}" for a in candidates)
    parsed = await ask(
        "Une y depura. Libro de acuerdos actual (lo más reciente):\n" + (current or "(vacío)")
        + "\n\nAcuerdos encontrados en las conversaciones, Nivel por Nivel (en orden):\n" + merged
        + "\n\nFicha encontrada por partes (la más reciente manda):\n"
        + "\n".join(f"- {k}: {v}" for k, v in fragments.items()))
    if not parsed.get("acuerdos") and not parsed.get("ficha"):
        return data  # sin la pasada final no se reemplaza la memoria: se intenta de nuevo más tarde
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    agreements = [{"tipo": a["tipo"], "texto": str(a["texto"]).strip()[:300], "nivel": a.get("nivel"), "fecha": now}
                  for a in parsed.get("acuerdos", []) if a.get("tipo") in KINDS and str(a.get("texto", "")).strip()]
    ficha = {str(f["campo"]).strip()[:60]: str(f["valor"]).strip()[:300] for f in parsed.get("ficha", [])
             if str(f.get("campo", "")).strip() and str(f.get("valor", "")).strip()}
    data["acuerdos"] = agreements[:MAX_AGREEMENTS] or data["acuerdos"]
    data["ficha"] = {**data.get("ficha", {}), **ficha}
    data["consolidado"] = now
    save(db, project, data)
    return data


def set_ficha(db: Session, project: Project, ficha: dict[str, str]) -> dict:
    """El fundador corrige la ficha a mano: lo que él escribe manda."""
    data = load(db, project)
    data["ficha"] = {str(k).strip()[:60]: str(v).strip()[:300] for k, v in ficha.items() if str(k).strip() and str(v).strip()}
    save(db, project, data)
    return data
