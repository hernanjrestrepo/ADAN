"""Nivel 1 Service — the core business logic for Level 1 (El Dolor).

Implements the complete Level 1 flow per AD-FUNC-01:
1. Onboarding (pain discovery)
2. Dynamic questions
3. Board Room (real consensus)
4. Diagnosis
5. Recommendations
6. Gate Review (80/100 threshold)
7. Gemelo Digital persistence
"""
from __future__ import annotations

import json
import re
import time
from difflib import SequenceMatcher
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.ai.router import for_tier
from app.documents import learn as doc_learning
from app.documents import web
from app.levels.scripts import script_for
from app.nivel1 import board_dialogue, discovery, memoria, timeline
from app.nivel1.context import ContextLayers
from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_string, normalize_list
from app.models.models import (
    Card, CardStatus, Company, Conversation, Decision, DecisionStatus,
    Document, Event, Level, Message, NivelStatus, Project, Score, ScoreType,
)
from app.nivel1.board_room import BoardRoom, BoardConsensus
from app.nivel1.gate_review import GateReviewResult, build_result
from app.scoring import service as scoring
from app.services.gemelo_digital import GemeloDigitalService

# Mensajes recientes que se envían completos al modelo; los anteriores van resumidos
MAX_CONTEXT_MESSAGES = 16
MAX_SUMMARY_CHARS = 2000


def script_of(db: Session, conversation: Conversation | None):
    card = db.get(Card, conversation.card_id) if conversation is not None else None
    kind = card.card_type if card is not None else ""
    return script_for(int(kind[5:])) if kind.startswith("nivel") and kind[5:].isdigit() else script_for(1)


def discovery_progress(db: Session, conversation: Conversation | None, project: Project) -> dict:
    """Avance del guion para la interfaz; la evidencia ya registrada no se vuelve a sugerir."""
    history = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(
        Message.created_at).all() if conversation else []
    script = script_of(db, conversation)
    state = discovery.current_state(history, script)
    known = {e.claim.strip().lower() for e in scoring.active_evidence(db, project, script.dimension or "problem",
                                                                       include_unconfirmed=True)}
    state["evidencia_sugerida"] = [e for e in state["evidencia_sugerida"] if e["afirmacion"].strip().lower() not in known]
    return discovery.progress(state, script)


# Lo que es una tarea por conseguir (no un hecho) no entra como evidencia
_PENDING = re.compile(r"\b(describa|describan|conseguir|consigue|deber[ií]a|necesitas|pide|pedir|graba|grabar|"
                      r"haz|hacer|realiza|realizar|por validar|pendiente)\b", re.IGNORECASE)


def auto_register_evidence(db: Session, project: Project, user, message: Message) -> int:
    """La evidencia que el cliente menciona o que ADÁN encuentra investigando se registra sola, sin confirmar
    (decisión de Hernán, 2026-10-24). Solo entran hechos con fuente; lo que es una tarea por conseguir, no."""
    state = (message.metadata_json or {}).get("discovery") or {}
    dimension = script_of(db, db.get(Conversation, message.conversation_id)).dimension
    if dimension is None:
        return 0  # Niveles sin Score propio: la evidencia queda en la conversación
    known = {e.claim.strip().lower() for e in scoring.active_evidence(db, project, dimension, include_unconfirmed=True)}
    added = 0
    for s in state.get("evidencia_sugerida") or []:
        claim, kind, source = (s.get("afirmacion") or "").strip(), s.get("tipo"), (s.get("fuente") or "").strip()
        if not claim or claim.lower() in known or _PENDING.search(claim) or kind not in ("external", "testimony"):
            continue
        if kind == "external" and not source:
            continue
        try:
            scoring.record_evidence(db, project, user, dimension=dimension, claim=claim, kind=kind, source=source or None)
            known.add(claim.lower())
            added += 1
        except scoring.EvidenceError:
            db.rollback()
    return added


def _work(parsed: dict, repo_url: str | None, degraded) -> dict | None:
    if degraded:
        return None
    if repo_url:
        return {"tipo": "repositorio", "url": repo_url, "objetivo": ""}
    walk = parsed.get("recorrer") if isinstance(parsed.get("recorrer"), dict) else {}
    url, goal = str(walk.get("url", "")).strip(), str(walk.get("objetivo", "")).strip()
    if url and goal and "." in url:
        return {"tipo": "recorrido", "url": url[:2000], "objetivo": goal[:500]}
    return None


_NAMES = ("ADÁN", "Adán", "Santiago", "Camila", "Mateo", "Lucía", "Andrés", "Sofía", "Iris", "Orión", "Eva", "Teo")
_NAME_PREFIX = re.compile(r"^\s*(?:(?:" + "|".join(_NAMES) + r")(?:\s*(?:·|,|-)\s*[A-Za-zÁÉÍÓÚáéíóú ]{2,20})?"
                          r"(?:\s+aquí)?\s*[.:,—-]\s+)", re.I)


def _without_name(text: str) -> str:
    """Quita «Santiago.» o «Camila, CFO:» al inicio: el nombre ya se ve en el chat y en la oficina."""
    out = _NAME_PREFIX.sub("", text or "", count=1)
    return out[:1].upper() + out[1:]


def _options(parsed: dict) -> list[str]:
    raw = parsed.get("opciones") if isinstance(parsed.get("opciones"), list) else []
    return [str(o).strip()[:60] for o in raw if str(o).strip()][:3]


def _questions(texts: list[str]) -> list[str]:
    """Las preguntas (frases que terminan en «?») de los mensajes del equipo."""
    out = []
    for t in texts:
        for q in re.findall(r"[^.!?\n]*\?", t or ""):
            q = q.strip(" ¿*_-").strip()
            if len(q) > 12 and q not in out:
                out.append(q)
    return out


def _is_mesa(m: Message) -> bool:
    """Intervención corta de otro personaje (formato anterior): no cuenta como turno de la conversación."""
    return isinstance(m.metadata_json, dict) and bool(m.metadata_json.get("mesa"))


def _similar(a: str, b: str) -> float:
    """Qué tanto se parecen dos textos (0 a 1), sin mayúsculas ni espacios de más."""
    a, b = " ".join(a.lower().split())[:1500], " ".join(b.lower().split())[:1500]
    return SequenceMatcher(None, a, b).ratio() if a and b else 0.0


class Nivel1Service:
    """Orchestrates the complete Level 1 flow with real intelligence."""

    def __init__(self, llm: LLMAdapter, db: Session):
        # Conversación, diagnóstico y recomendaciones: nivel "standard" (WO-099)
        self.llm = for_tier(llm, "standard")
        self.db = db
        self.gemelo = GemeloDigitalService(db)
        self.board_room = BoardRoom(llm)

    # --- Step 1: Pain Discovery Card ---

    def get_or_create_level_card(self, project: Project, level: Level) -> Card:
        """La Card de trabajo del Nivel: la del dolor en el Nivel 1; una por Nivel desde el 2."""
        if level.number == 1:
            return self.get_or_create_pain_card(project, level)
        script = script_for(level.number)
        kind = f"nivel{level.number}"
        card = self.db.query(Card).filter(Card.project_id == project.id, Card.card_type == kind).first()
        if card is None:
            card = Card(project_id=project.id, level_id=level.id, title=f"Nivel {level.number}: {script.name}",
                        description=script.goal, card_type=kind, status=CardStatus.ACTIVE)
            self.db.add(card)
            self.db.commit()
            self.db.refresh(card)
        return card

    def get_or_create_pain_card(self, project: Project, level: Level) -> Card:
        """Get or create the Pain Discovery card for Level 1."""
        card = self.db.query(Card).filter(
            Card.project_id == project.id,
            Card.level_id == level.id,
            Card.card_type == "pain_discovery",
        ).first()

        if not card:
            card = Card(
                project_id=project.id,
                level_id=level.id,
                title="Descubrimiento del Dolor",
                description="¿Qué problema real resuelve tu empresa? ¿A quién afecta? ¿Qué tan urgente es?",
                card_type="pain_discovery",
                status=CardStatus.ACTIVE,
            )
            self.db.add(card)
            self.db.commit()
            self.db.refresh(card)

        return card

    def get_or_create_conversation(self, card: Card) -> Conversation:
        """Get or create conversation for a card."""
        conv = self.db.query(Conversation).filter(
            Conversation.card_id == card.id,
            Conversation.status == "active",
        ).first()

        if not conv:
            conv = Conversation(
                card_id=card.id,
                title="Conversación de Descubrimiento",
            )
            self.db.add(conv)
            self.db.commit()
            self.db.refresh(conv)

        return conv

    async def read_links(self, project: Project, text: str) -> str:
        """Abre los enlaces que el fundador pegó: quedan en la Biblioteca y el equipo los lee en este turno."""
        urls = web.find_urls(text)
        # Un repositorio de GitHub no se lee como página: lo revisa Mateo en segundo plano
        repos = [u for u in urls if "github.com/" in u.lower() and u.lower().rstrip("/").count("/") >= 4]
        if repos:
            self.repo_url = repos[0]
            urls = [u for u in urls if u not in repos]
        read = self.db.query(Document).filter(Document.project_id == project.id, Document.doc_type == "web_page") \
            .order_by(Document.created_at.desc()).limit(6).all()
        repo_note = ("\n\nEl fundador compartió su repositorio de GitHub: Mateo (CTO) ya lo está leyendo en segundo "
                     "plano y dejará su revisión en la Sala en un par de minutos. Díselo en una frase y sigue."
                     if repos else "")
        if not urls:
            # Las páginas que ya se leyeron siguen siendo parte de lo que el equipo sabe de la empresa
            if not read:
                return repo_note.strip()
            return ("Páginas web que YA ABRISTE en esta empresa (con el navegador; sí puedes ver páginas web). Úsalas; "
                    "si el fundador pide revisarlas otra vez, pídele el enlace y se vuelven a abrir:\n\n"
                    + "\n\n---\n\n".join((d.content or "")[:3500] for d in read[:2]) + repo_note)
        fresh_after = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=6)
        cached = {}
        for d in read:
            m = re.search(r"^Fuente: (\S+)", d.content or "", re.M)
            if m and d.created_at and d.created_at.replace(tzinfo=None) > fresh_after:
                cached.setdefault(m.group(1).rstrip("/").lower(), d.content)
        todo = [u for u in urls if u.rstrip("/").lower() not in cached]
        pages = await web.fetch_all(todo) if todo else []
        blocks = [cached[u.rstrip("/").lower()][:9000] for u in urls if u.rstrip("/").lower() in cached]
        for page in pages:
            if page.get("error"):
                blocks.append(f"- {page['url']}: NO se pudo abrir ({page['error']}). Díselo con honestidad y pide el texto.")
                continue
            host = urlparse(page["url"]).hostname or page["url"]
            content = web.as_markdown(page)
            self.db.add(Document(project_id=project.id, title=f"Página web: {page.get('titulo') or host}"[:255],
                                 content=content, doc_type="web_page", origin="received_from_client"))
            blocks.append(content[:9000])
        self.db.commit()
        note = ""
        company = self.db.get(Company, project.company_id)
        found = next((m.group(1) for b in blocks for m in [re.search(r"^Logo probable: (\S+)", b, re.M)] if m), None)
        if company is not None and not company.logo and found:
            # El fundador ve la imagen en el chat y confirma con un clic si es su logo
            self.found_logo = {"url": found}
            note = ("\n\nEn su sitio encontré lo que parece su logo; se le muestra en el chat con un botón para adoptarlo. "
                    "Menciónalo en una frase («¿este es tu logo? Si es, lo adopto y saco tu paleta de colores»).")
        return ("El fundador compartió enlaces y TÚ ABRISTE LAS PÁGINAS con un navegador real (sí puedes ver páginas "
                "web, incluso las hechas con JavaScript, y ves una descripción de la pantalla). Esto es lo que "
                "contienen; úsalo, cita lo que dicen y no le pidas que te lo describa ni digas que tienes "
                "restricciones para navegar:\n\n" + "\n\n---\n\n".join(blocks) + note + repo_note)

    # --- Step 2: Chat with ADÁN ---

    async def chat(
        self,
        project: Project,
        level: Level,
        user_message: str,
        conversation: Conversation | None = None,
    ) -> tuple[Message, Conversation]:
        """Un turno del guion de descubrimiento: ADÁN entiende la respuesta y hace la siguiente pregunta.

        Una sola llamada con salida estructurada devuelve la respuesta y el estado de los siete temas
        (discovery.py). Si responde el modelo local de respaldo, el estado no se toca y el mensaje
        queda marcado como degradado para que el cliente lo sepa.
        """
        card = self.get_or_create_level_card(project, level)
        if conversation is None:
            conversation = self.get_or_create_conversation(card)
        script = script_of(self.db, conversation)
        schema = discovery.schema_for(script.topic_ids)

        self.db.add(Message(conversation_id=conversation.id, role="user", content=user_message))
        self.db.commit()

        history = self._history(conversation)
        state = discovery.current_state(history, script)
        messages = self.build_llm_messages(conversation, state)
        # Lo ya investigado en esta conversación: no se vuelve a buscar (cada búsqueda tarda) ni se repite
        done = [m.metadata_json["investigado"]["consulta"] for m in history
                if m.role == "assistant" and isinstance(m.metadata_json, dict)
                and isinstance(m.metadata_json.get("investigado"), dict)]
        if done:
            messages[0] = LLMMessage(role="system", content=messages[0].content + (
                "\n\nYa investigaste en internet (no repitas estas búsquedas; usa lo encontrado, que está en tus "
                "respuestas anteriores): " + " | ".join(q[:160] for q in done[-6:])))
        pages = await self.read_links(project, user_message)
        if pages:
            messages[0] = LLMMessage(role="system", content=messages[0].content + "\n\n" + pages)
        # Las últimas respuestas del equipo: ninguna se puede repetir
        last_replies = [m.content for m in history if m.role == "assistant" and not _is_mesa(m)][-3:]
        # Ni las preguntas ya hechas: se le recuerdan al modelo y, si repite una, se le pide otra respuesta
        asked = _questions([m.content for m in history if m.role == "assistant" and not _is_mesa(m)][-10:])
        if asked:
            messages[0] = LLMMessage(role="system", content=messages[0].content + (
                "\n\nPreguntas que el equipo YA hizo (no repitas ninguna, ni con otras palabras; si no la respondió, "
                "asume y sigue):\n" + "\n".join(f"- {q}" for q in asked[-8:])))
        response = await self.llm.chat_json(messages, schema, temperature=0.4, max_tokens=2048)

        degraded = response.metadata.get("degraded")
        parsed = response.parsed if isinstance(response.parsed, dict) else {}
        query = parsed.get("investigar") if isinstance(parsed.get("investigar"), str) else ""
        if query.strip() and any(_similar(query, q) > 0.6 for q in done):
            query = ""  # ya se buscó algo equivalente: se responde con lo que hay, sin esperar otra búsqueda
        pending = query.strip() if query.strip() and not degraded else ""
        # Nunca repetir la respuesta anterior: si sale casi igual, se pide una nueva que atienda lo que dijo el cliente
        draft = parsed.get("respuesta") if isinstance(parsed.get("respuesta"), str) else ""
        repeated_q = [q for q in _questions([draft]) if any(_similar(q, old) > 0.72 for old in asked)] if draft else []
        if draft and (repeated_q or any(_similar(draft, r) > 0.75 for r in last_replies)) and not degraded:
            retry = await self.llm.chat_json(messages + [
                LLMMessage(role="assistant", content=draft),
                LLMMessage(role="user", content=(
                    ("[Nota interna: ese borrador vuelve a preguntar «" + repeated_q[0] + "», que ya preguntaste. No lo "
                     "repitas: asume la opción más razonable como supuesto, propón el borrador del siguiente tema y "
                     "avanza. Deja `investigar` vacío.]") if repeated_q else
                    ("[Nota interna: ese borrador repite casi igual tu respuesta anterior. Responde a lo NUEVO que "
                     "acaba de decir el cliente, sin repetir datos ni tablas que ya le diste. Deja `investigar` vacío.]"))),
            ], schema, temperature=0.6, max_tokens=2048)
            if isinstance(retry.parsed, dict) and retry.parsed.get("respuesta"):
                parsed, response = retry.parsed, retry
        reply = _without_name(parsed.get("respuesta") if isinstance(parsed.get("respuesta"), str) else "")
        if reply.strip():
            content = reply.strip()
            if not degraded:
                state = discovery.merge(state, parsed)
        elif response.content.strip() and not response.content.lstrip().startswith(("{", "[")):
            content = response.content.strip()  # el modelo respondió en texto: se muestra tal cual
        else:
            content = ("No pude procesar tu mensaje esta vez. Quedó guardado: escríbeme de nuevo la idea "
                       "principal y seguimos donde íbamos.")

        speaker = parsed.get("habla") if parsed.get("habla") in timeline.TEAM else "ceo"
        if not degraded:
            memoria.remember(self.db, project, parsed.get("acuerdos") or [], script.number)
        # Con todos los temas cubiertos, ADÁN propone el cierre y el fundador solo confirma
        closing = (not degraded and reply.strip() and discovery.next_topic(state, script) is None
                   and level.status != NivelStatus.COMPLETED)
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            agent_name=timeline.label(speaker),
            content=content,
            metadata_json={
                "propone_cierre": bool(closing),
                "opciones": [] if closing or degraded else _options(parsed),
                "logo_sugerido": getattr(self, "found_logo", None),
                # Trabajo en segundo plano que llega como mensaje aparte: recorrido con clics o revisión de código
                "trabajando": _work(parsed, getattr(self, "repo_url", None), degraded),
                "model": response.model,
                "tokens": response.prompt_tokens + response.completion_tokens,
                "duration_s": response.duration_s,
                "degraded": degraded,
                "discovery": state,
                "reaccion": parsed.get("reaccion") if isinstance(parsed.get("reaccion"), dict) else None,
                "agente": speaker,
                "escena": "oficina",
                "investigado": None,
                # La búsqueda en internet corre aparte (tarda); sus hallazgos llegan en el siguiente mensaje
                "investigando": {"consulta": pending} if pending else None,
            },
        )
        self.db.add(assistant_msg)
        self.db.commit()
        self.db.refresh(assistant_msg)
        # Un solo personaje por turno: ya no hay intervenciones de «mesa» después de la respuesta
        if not degraded:
            await self.refresh_summary(project, conversation)
        return assistant_msg, conversation

    async def refresh_summary(self, project: Project, conversation: Conversation) -> None:
        """Resume con la IA lo que ya no cabe en la ventana de mensajes (cada 8 mensajes nuevos), para la memoria."""
        history = [m for m in self._history(conversation) if not _is_mesa(m)]
        older = history[:-MAX_CONTEXT_MESSAGES]
        key = f"nivel{script_of(self.db, conversation).number}"
        prev = memoria.summary_of(self.db, project, key)
        if len(older) < 6 or len(older) - prev.get("mensajes", 0) < 8:
            return
        transcript = "\n".join(f"{'Fundador' if m.role == 'user' else (m.agent_name or 'ADÁN')}: {m.content[:700]}"
                               for m in older[prev.get("mensajes", 0):])
        try:
            resp = await self.llm.chat([
                LLMMessage(role="system", content=(
                    "Resume para la memoria del equipo lo esencial de esta conversación: qué dijo y decidió el fundador, "
                    "qué propuso el equipo y quedó aceptado, qué se descartó y qué quedó pendiente. Viñetas cortas, "
                    "español, máximo 250 palabras. Sin inventar nada.")),
                LLMMessage(role="user", content=(f"Resumen anterior:\n{prev.get('texto', '(ninguno)')}\n\n"
                                                 f"Conversación nueva:\n{transcript[:12000]}"))], max_tokens=900)
        except Exception:  # noqa: BLE001 - la memoria se intenta de nuevo en el siguiente turno
            return
        if (resp.content or "").strip() and not resp.metadata.get("degraded"):
            memoria.set_summary(self.db, project, key, resp.content.strip(), len(older))

    async def complete_research(self, conversation: Conversation, query: str) -> Message | None:
        """Investiga en internet lo que ADÁN anunció y responde con los hallazgos en un mensaje nuevo."""
        history = self._history(conversation)
        script = script_of(self.db, conversation)
        state = discovery.current_state(history, script)
        research = await self._research(query)
        if not research["text"]:
            return None
        messages = self.build_llm_messages(conversation, state) + [LLMMessage(role="user", content=(
            "[Investigación hecha por ADÁN en internet"
            + ("" if research["searched"] else ", SIN búsqueda verificada: márcalo como estimación")
            + f" sobre «{query}»]\n{research['text'][:6000]}\n\n"
            "Responde ahora al cliente con esos hallazgos, sin repetir lo que ya le dijiste. NO vuelques los datos: "
            "digiérelos y aterrízalos a SU empresa (qué significan para su negocio, qué decisión cambian, qué "
            "proponemos hacer). Máximo 3 cifras clave, solo las que tengan fuente con URL (o márcalas como "
            "estimación); descarta las que no cuadren con el sentido común. Fuentes al final. Luego tu pregunta. "
            "Deja `investigar` vacío."))]
        response = await self.llm.chat_json(messages, discovery.schema_for(script.topic_ids), temperature=0.3, max_tokens=3000)
        parsed = response.parsed if isinstance(response.parsed, dict) else {}
        reply = _without_name(parsed.get("respuesta") if isinstance(parsed.get("respuesta"), str) else "")
        if not reply.strip():
            return None
        state = discovery.merge(state, parsed)
        speaker = parsed.get("habla") if parsed.get("habla") in timeline.TEAM else "ceo"
        msg = Message(conversation_id=conversation.id, role="assistant", agent_name=timeline.label(speaker), content=reply.strip(),
                      metadata_json={"model": response.model, "duration_s": response.duration_s,
                                     "tokens": response.prompt_tokens + response.completion_tokens, "discovery": state,
                                     "reaccion": parsed.get("reaccion") if isinstance(parsed.get("reaccion"), dict) else None,
                                     "agente": speaker, "escena": "oficina",
                                     "investigado": {"consulta": query, "verificado": research["searched"]}})
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    async def _research(self, query: str) -> dict:
        """Búsqueda en internet (Kimi $web_search). Sin búsqueda disponible, responde con lo que sabe y lo marca."""
        search = getattr(self.llm, "chat_search", None)
        msgs = [LLMMessage(role="system", content=(
            "Eres el investigador de ADÁN. Busca en internet datos actuales y verificables para responder. Da cifras "
            "con año y la URL EXACTA de cada fuente; si no encuentras una fuente real, dilo: nunca inventes un número "
            "ni una fuente. Revisa que cada cifra tenga sentido común frente a la población y el mercado reales. Si "
            "hay estimaciones distintas, muestra el rango. Español, máximo 250 palabras.")),
            LLMMessage(role="user", content=query)]
        try:
            if search is None:
                resp = await self.llm.chat(msgs, max_tokens=2500)
                return {"query": query, "text": resp.content or "", "searched": False}
            resp = await search(msgs, max_tokens=2500)
            return {"query": query, "text": resp.content or "", "searched": bool(resp.metadata.get("searched", True))}
        except Exception:  # noqa: BLE001 - la conversación sigue aunque la búsqueda falle
            return {"query": query, "text": "", "searched": False}

    # --- Documentación del cliente ---

    async def learn_from_documents(self, project: Project, level: Level, docs: list[tuple[str, str]]) -> dict:
        """ADÁN lee la documentación cargada: actualiza el guion del dolor, propone evidencia verificable y
        deja escrito qué entendió, qué falta y qué riesgos ve. El resultado queda en la conversación
        (Registro Permanente) y en un Documento que el Board lee antes de votar."""
        card = self.get_or_create_level_card(project, level)
        conversation = self.get_or_create_conversation(card)
        state = discovery.current_state(self._history(conversation), script_of(self.db, conversation))
        context = ContextLayers(self.db).for_conversation(conversation)
        response = await doc_learning.learn(self.llm, state, docs, context)
        degraded = response.metadata.get("degraded")
        parsed = response.parsed if isinstance(response.parsed, dict) else {}
        names = ", ".join(name for name, _ in docs)
        reply = parsed.get("respuesta") if isinstance(parsed.get("respuesta"), str) else ""
        if reply.strip() and not degraded:
            state = discovery.merge(state, parsed)
            content = f"📎 Leí {len(docs)} documento(s): {names}.\n\n{reply.strip()}"
        else:
            content = (f"📎 Recibí {len(docs)} documento(s): {names}. Quedaron guardados en la memoria de tu empresa, "
                       "pero esta vez no pude analizarlos a fondo"
                       + (" (el modelo principal no respondió)." if degraded else ".")
                       + " Pídeme que los revise de nuevo en un momento.")
            parsed = {}
        digest = {k: parsed.get(k) for k in ("resumen", "etapa", "hechos", "vacios", "riesgos")} if parsed else {}
        self.db.add(Message(conversation_id=conversation.id, role="assistant", agent_name="ADÁN", content=content,
                            metadata_json={"model": response.model, "degraded": degraded, "discovery": state,
                                           "documents": [name for name, _ in docs], "learning": digest}))
        if digest.get("resumen"):
            lines = [f"Documentos: {names}", f"Etapa: {digest.get('etapa') or 'no_claro'}", f"Resumen: {digest['resumen']}"]
            lines += [f"Hecho ({h.get('base')}): {h.get('dato')} [{h.get('fuente')}]" for h in (digest.get("hechos") or [])[:15]
                      if isinstance(h, dict)]
            lines += [f"Vacío: {v}" for v in (digest.get("vacios") or [])[:10]]
            lines += [f"Riesgo: {r}" for r in (digest.get("riesgos") or [])[:10]]
            self.db.add(Document(project_id=project.id, title=f"Lo que ADÁN aprendió de: {names}"[:255],
                                 content="\n".join(lines), doc_type="client_docs_digest", origin="generated_by_adan"))
        self.db.commit()
        return {"reply": content, "degraded": degraded, "learning": digest}

    def _history(self, conversation: Conversation) -> list[Message]:
        return self.db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()

    def build_llm_messages(self, conversation: Conversation, state: dict | None = None,
                           structured: bool = True) -> list[LLMMessage]:
        """Contexto para el modelo: guion y estado, resumen de lo antiguo y los mensajes recientes completos.

        Evita desbordar la ventana de contexto en conversaciones largas (AD-CMP-04).
        """
        history = self._history(conversation)
        script = script_of(self.db, conversation)
        if state is None:
            state = discovery.current_state(history, script)
        # Las intervenciones viejas de «mesa» no ocupan la ventana: así caben más turnos reales
        talk = [m for m in history if not _is_mesa(m)]
        older, recent = talk[:-MAX_CONTEXT_MESSAGES], talk[-MAX_CONTEXT_MESSAGES:]
        if older:
            conversation.summary = self._summarize(older)
            self.db.commit()

        system_prompt = discovery.system_prompt(state, structured=structured, script=script)
        company = self.db.query(Company).join(Project, Project.company_id == Company.id) \
            .join(Card, Card.project_id == Project.id).filter(Card.id == conversation.card_id).first()
        if script.number > 1:
            # Lo que se construyó en los Niveles anteriores: el punto de partida de este
            project = self.db.query(Project).join(Card, Card.project_id == Project.id) \
                .filter(Card.id == conversation.card_id).first()
            before = self.levels_brief(project, script.number) if project is not None else ""
            if before:
                system_prompt += "\n\nLo acordado en los Niveles anteriores:\n" + before
        if company is not None and company.origin_stage == "existing":
            system_prompt += (
                "\n\nMODO REVISIÓN Y PIVOTE: esta empresa ya existe (puede tener producto, MVP o ventas, y quizá no le está "
                "yendo como esperaba). No empieces de cero: usa lo que ya hay (documentos, producto, cifras) para cubrir los "
                "temas rápido, encuentra dónde se rompe el negocio (el problema, el cliente, el canal, el precio o la "
                "ejecución) y propone con optimismo realista qué ajustar o pivotar, apoyándote en sus datos reales."
                + ("" if company.logo else
                   " Esta empresa ya tiene marca pero ADÁN aún no tiene su logo: en algún momento natural pídele el "
                   "enlace de su web (lo tomamos de ahí) o que lo suba en 🏷️ Marca → «Ya tengo logo»; no inventes uno."))
        if conversation.summary:
            system_prompt += f"\n\nResumen de lo que el cliente contó antes: {conversation.summary}"
        # La memoria del proyecto (acuerdos, resúmenes y fragmentos de la Biblioteca), la misma para todo el equipo
        project = self.db.query(Project).join(Card, Card.project_id == Project.id) \
            .filter(Card.id == conversation.card_id).first()
        if project is not None:
            last_user = next((m.content for m in reversed(talk) if m.role == "user"), "")
            memory = memoria.context(self.db, project, query=last_user, nivel=script.number)
            if memory:
                system_prompt += "\n\n" + memory
        # Capas Global, Proyecto, Nivel y Card (AD-CMP-04); la Conversación son los mensajes
        system_prompt += "\n\n" + ContextLayers(self.db).for_conversation(conversation)
        messages = [LLMMessage(role="system", content=system_prompt)]
        for msg in recent:
            messages.append(LLMMessage(role=msg.role, content=msg.content))
        return messages

    @staticmethod
    def _summarize(messages: list[Message]) -> str:
        """Resumen extractivo de lo que el usuario ya contó (sin llamar al modelo)."""
        summary = " | ".join(m.content[:200] for m in messages if m.role == "user")
        return summary[:MAX_SUMMARY_CHARS]

    # --- Step 3: Board Room ---

    async def run_board_room(self, project: Project, company: Company,
                             client_question: str = "", client_position: str = "", level_number: int = 1) -> BoardConsensus:
        """Board Room de 7 roles (AD-FUNC-02): el CEO preside y seis especialistas votan."""
        pain_description = self.board_brief(project, level_number)
        if not pain_description.strip():
            raise ValueError("No hay descripción del dolor. Inicia una conversación primero.")
        conversation_context = ""

        # El Board también ve lo que ya se sabe de la empresa (capa Proyecto, AD-CMP-04)
        conversation_context += "\n\nLo que ya se sabe de la empresa:\n" + ContextLayers(self.db).project_layer(project)
        # Y lo que el fundador le explicó al Board después de la sesión anterior
        conversation_context += board_dialogue.as_context(self.db, project)
        # Y la memoria del proyecto: el Board no vuelve a pedir lo que ya se acordó o se descartó
        memory = memoria.context(self.db, project, query=pain_description[:2000], nivel=level_number)
        if memory:
            conversation_context += "\n\n" + memory

        # Cuántas sesiones van: el abogado del diablo rota entre los especialistas
        sessions = self.db.query(Document).filter(Document.project_id == project.id,
                                                  Document.doc_type == "board_minutes").count()
        consensus = await self.board_room.run(pain_description, conversation_context,
                                              client_question=client_question, client_position=client_position,
                                              session_number=sessions)

        # Persist result in Gemelo Digital
        votes_data = [
            {
                "agent": v.agent,
                "vote": v.vote,
                "confidence": v.confidence,
                "justification": v.justification,
            }
            for v in consensus.votes
        ]

        self.gemelo.save_board_room_result(
            project,
            consensus.decision,
            consensus.score,
            consensus.summary,
            votes_data,
            consensus=consensus.to_dict(),
        )
        self.gemelo.save_board_minutes(project, consensus.minutes)
        # El voto del Board entra como inferencia sobre el problema: la evidencia más débil (AD-CMP-05)
        if scoring.record_board_inference(self.db, project, consensus) is not None:
            self.db.commit()

        return consensus

    def levels_brief(self, project: Project, upto: int) -> str:
        """Lo logrado en cada Nivel anterior a `upto`, tema por tema."""
        parts = []
        for n in range(1, upto):
            script = script_for(n)
            kind = "pain_discovery" if n == 1 else f"nivel{n}"
            card = self.db.query(Card).filter(Card.project_id == project.id, Card.card_type == kind).first()
            conv = self.db.query(Conversation).filter(Conversation.card_id == card.id).first() if card else None
            if conv is None:
                continue
            text = discovery.brief(discovery.current_state(self._history(conv), script), script)
            if text:
                parts.append(f"Nivel {n}, {script.name}:\n{text}")
        return "\n\n".join(parts)

    def board_brief(self, project: Project, level_number: int = 1) -> str:
        if level_number > 1:
            # Desde el Nivel 3 el Board evalúa lo construido en este Nivel sobre lo de los anteriores
            return self.levels_brief(project, level_number + 1)
        return self._level1_brief(project)

    def _level1_brief(self, project: Project) -> str:
        """Lo que el Board evalúa: lo que ADÁN entendió (guion), la evidencia registrada y las palabras
        del cliente. Las respuestas del modelo de respaldo y el resto de la charla no entran: antes el
        Board leía la conversación cruda, con ruido y respuestas sin sentido."""
        card = self.db.query(Card).filter(Card.project_id == project.id, Card.card_type == "pain_discovery").first()
        conversation = self.db.query(Conversation).filter(Conversation.card_id == card.id).first() if card else None
        history = self._history(conversation) if conversation else []
        state = discovery.current_state(history)
        parts = []
        understood = discovery.brief(state)
        if understood:
            parts.append("Lo que ADÁN entendió del dolor (guion del Nivel 1):\n" + understood)
        evidence = scoring.active_evidence(self.db, project, "problem")
        if evidence:
            labels = {"external": "fuente externa", "testimony": "testimonio de clientes", "inference": "inferencia"}
            parts.append("Evidencia registrada:\n" + "\n".join(
                f"- [{labels.get(e.kind, e.kind)}{', en contra' if e.polarity == 'contradicts' else ''}] {e.claim}"
                + (f" (fuente: {e.source})" if e.source else "") for e in evidence[:15]))
        else:
            parts.append("Evidencia registrada: ninguna.")
        digests = self.db.query(Document).filter(Document.project_id == project.id,
                                                 Document.doc_type == "client_docs_digest").order_by(
            Document.created_at.desc()).limit(3).all()
        if digests:
            parts.append("Lo que ADÁN aprendió de la documentación del cliente:\n"
                         + "\n\n".join((d.content or "")[:2500] for d in digests))
        words = [m.content.strip()[:800] for m in history if m.role == "user" and len(m.content.strip()) >= 10]
        if words:
            parts.append("Palabras del cliente (lo más reciente):\n" + "\n".join(f"- {w}" for w in words[-6:]))
        return "\n\n".join(parts) if (understood or words or digests) else ""

    def get_last_board_consensus(self, project: Project) -> BoardConsensus:
        """Último Board Room guardado: recomendaciones y Gate Review no lo vuelven a ejecutar."""
        data = self.gemelo.get_last_board_consensus(project)
        if data is None:
            raise ValueError("Ejecuta primero el Board Room o el diagnóstico.")
        return BoardConsensus.from_dict(data)

    # --- Step 4: Generate Diagnosis ---

    async def generate_diagnosis(
        self,
        project: Project,
        company: Company,
        board_consensus: BoardConsensus,
    ) -> Document:
        """Generate the formal diagnosis document."""

        # ALL data from board_consensus is already normalized via board_room.py
        # Use normalize_list/normalize_string as safety net
        board_summary = "\n\n".join([
            f"### Análisis {v.agent}\n"
            f"**Voto:** {v.vote} (confianza: {v.confidence:.0f}%)\n"
            f"**Justificación:** {normalize_string(v.justification)}\n"
            f"**Análisis:** {normalize_string(v.analysis)}\n"
            f"**Fortalezas:** {', '.join(normalize_list(v.key_strengths))}\n"
            f"**Preocupaciones:** {', '.join(normalize_list(v.key_concerns))}\n"
            f"**Preguntas pendientes:** {', '.join(normalize_list(v.questions))}"
            for v in board_consensus.votes
        ])

        prompt = (
            f"Genera un Diagnóstico del Dolor formal basado en:\n\n"
            f"## Decisión del Board Room\n"
            f"Decisión: {board_consensus.decision}\n"
            f"Score: {board_consensus.score:.0f}/100\n"
            f"Confianza: {board_consensus.confidence:.0f}%\n\n"
            f"## Análisis de cada Agente\n{board_summary}\n\n"
            f"## Preocupaciones del Board\n"
            f"Unánimes: {', '.join(board_consensus.concerns_unanimous) if board_consensus.concerns_unanimous else 'Ninguna'}\n"
            f"Mayoría: {', '.join(board_consensus.concerns_majority[:5]) if board_consensus.concerns_majority else 'Ninguna'}\n\n"
            f"El diagnóstico debe incluir:\n"
            f"1. Resumen ejecutivo del problema\n"
            f"2. Evidencia que respalda la existencia del problema\n"
            f"3. Análisis del Board Room (síntesis de los 4 agentes)\n"
            f"4. Evaluación de viabilidad\n"
            f"5. Recomendación final con nivel de confianza\n\n"
            f"Formato: Markdown profesional. Sé directo y honesto."
        )

        response = await self.llm.generate(
            prompt=prompt,
            system="Diagnóstico ADÁN. Profesional, honesto. Español.",
            temperature=0.5,
            max_tokens=1024,
        )

        # Save in Gemelo Digital
        doc = self.gemelo.save_diagnosis(project, "Diagnóstico del Dolor", response.content)

        return doc

    # --- Step 5: Generate Recommendations ---

    async def generate_recommendations(
        self,
        project: Project,
        diagnosis: str,
        board_consensus: BoardConsensus,
    ) -> Document:
        """Generate actionable recommendations."""
        prompt = (
            f"Basado en el siguiente diagnóstico y análisis del Board Room, "
            f"genera recomendaciones ACCIONABLES para el emprendedor:\n\n"
            f"## Diagnóstico\n{diagnosis}\n\n"
            f"## Decisión del Board: {board_consensus.decision}\n\n"
            f"## Preocupaciones a abordar\n"
            f"{chr(10).join(f'- {c}' for c in board_consensus.concerns_majority[:5])}\n\n"
            f"Las recomendaciones deben ser:\n"
            f"1. Específicas (no genéricas)\n"
            f"2. Accionables (el emprendedor puede hacerlas ahora)\n"
            f"3. Priorizadas (qué hacer primero)\n"
            f"4. Con evidencia del Board Room que las respalde\n\n"
            f"Formato: Markdown con lista numerada."
        )

        response = await self.llm.generate(
            prompt=prompt,
            system="Eres el asesor de recomendaciones de ADÁN. Genera recomendaciones específicas, accionables y priorizadas. Habla en español.",
            temperature=0.5,
            max_tokens=1536,
        )

        doc = self.gemelo.save_recommendation(project, "Recomendaciones del Nivel 1", response.content)

        return doc

    # --- Step 6: Calculate Scores ---

    async def calculate_scores(
        self,
        project: Project,
        board_consensus: BoardConsensus,
        diagnosis: str,
    ) -> list[Score]:
        """Problem Score sobre la evidencia registrada (AD-CMP-05), no sobre el texto del diagnóstico."""
        return [scoring.calculate_dimension(self.db, project, "problem")]

    # --- Step 7: Gate Review ---

    async def run_gate_review(self, project: Project) -> tuple[GateReviewResult, Decision | None]:
        """Gate del Nivel 1 sobre la evidencia registrada (WO-107).

        Si la evidencia alcanza, propone cerrar el Nivel; se completa solo cuando el cliente lo aprueba.
        """
        evaluation, _score = scoring.evaluate_gate(self.db, project, 1)
        result = build_result(1, evaluation)
        decision = None
        if result.approved:
            decision = self.gemelo.propose_level_completion(project, 1, result.overall_score, result.message)
        return result, decision

    async def run_gate_review_preview(self, project: Project) -> tuple[GateReviewResult, None]:
        """La misma evaluación, sin proponer nada ni guardar un Score nuevo."""
        rule = scoring.engine.GATE_RULES[1]
        rows = scoring.active_evidence(self.db, project, rule.score_type)
        return build_result(1, scoring.engine.evaluate_gate(1, scoring._items(rows))), None

    def advance_without_evidence(self, project: Project) -> Decision:
        """El cliente quiere avanzar sin evidencia suficiente (AD-CMP-01 §3).

        ADÁN no bloquea ni decide por él: propone la decisión recomendando seguir trabajando el
        Nivel. Elegir cerrarlo es decidir distinto a lo recomendado y exige los 6 campos.
        """
        evaluation, _score = scoring.evaluate_gate(self.db, project, 1)
        if evaluation.sufficient:
            raise ValueError("La evidencia ya alcanza: usa el Gate Review para proponer el cierre.")
        result = build_result(1, evaluation)
        return self.gemelo.propose_level_completion(project, 1, result.overall_score, result.message,
                                                    recommended="CONTINUE")
