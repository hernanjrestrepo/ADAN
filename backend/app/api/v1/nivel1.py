"""Nivel 1 endpoints — the complete Level 1 flow with real intelligence."""
import asyncio
import json
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.apples import service as apples
from app.ai.factory import get_llm_adapter
from app.arena.service import Arena
from app.nivel1 import board_dialogue, timeline
from app.documents import extract as doc_extract
from app.documents import media
from app.ems.memory import EnterpriseMemorySystem
from app.ems.store import embedding_provider, get_vector_store
from app.core.auth import get_current_user
from app.core.authz import get_owned_company, get_owned_project
from app.core.ratelimit import llm_user
from app.core.database import get_db
from app.core.disclaimer import AI_DISCLAIMER
from app.models.models import (
    Card, Conversation, Decision, Document, Level, Message, Project, Score, User,
)
from app.nivel1.service import Nivel1Service, discovery_progress, auto_register_evidence
from app.services.gemelo_digital import GemeloDigitalService
from app.ai.router import for_tier
from app.ai.usage import usage_scope
from app.schemas.schemas import (
    BoardRoomRequest, ChatRequest, ChatResponse, CompanyResponse, DecisionAction, DecisionResponse,
    DocumentResponse, GateReviewResponse, LevelResponse, MessageResponse, ScoreResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/nivel1", tags=["nivel1"])


def get_llm() -> LLMAdapter:
    return get_llm_adapter()


async def track_llm_usage(company_id: str, db: Session = Depends(get_db)):
    """Registra el costo de las llamadas al modelo de la petición en `llm_usage` (WO-099)."""
    with usage_scope(db, company_id, level=1):
        yield


def get_latest_diagnosis(db: Session, project: Project) -> Document:
    """El diagnóstico más reciente del proyecto."""
    diagnosis_doc = db.query(Document).filter(
        Document.project_id == project.id,
        Document.doc_type == "diagnosis",
    ).order_by(Document.created_at.desc()).first()
    if not diagnosis_doc:
        raise HTTPException(status_code=400, detail="Generate diagnosis first")
    return diagnosis_doc


def get_owned_conversation(db: Session, conversation_id: str, project: Project) -> Conversation:
    """Verifica que la conversación pertenece al proyecto de la empresa del usuario."""
    conversation = db.query(Conversation).join(Card, Conversation.card_id == Card.id).filter(
        Conversation.id == conversation_id,
        Card.project_id == project.id,
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/{company_id}/status")
def get_nivel1_status(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the complete Nivel 1 status including Gemelo Digital state."""
    company = get_owned_company(db, company_id, user)

    project = db.query(Project).filter(Project.company_id == company_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    level = db.query(Level).filter(
        Level.project_id == project.id,
        Level.number == 1,
    ).first()

    card = db.query(Card).filter(
        Card.project_id == project.id,
        Card.card_type == "pain_discovery",
    ).first()

    conversation = None
    messages = []
    if card:
        conversation = db.query(Conversation).filter(
            Conversation.card_id == card.id,
        ).first()
        if conversation:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation.id,
            ).order_by(Message.created_at).all()

    scores = db.query(Score).filter(Score.project_id == project.id).all()
    documents = db.query(Document).filter(Document.project_id == project.id).all()

    return {
        "company": company,
        "project": project,
        "level": level,
        "card": card,
        "conversation": conversation,
        "messages": messages,
        "scores": scores,
        "documents": documents,
        # Guion del descubrimiento: qué entendió ADÁN de cada tema y qué falta
        "discovery": discovery_progress(db, conversation, project),
    }


def require_level_paid(db: Session, company_id: str, level: int) -> None:
    """Con APPLES_REQUIRED encendido, el Nivel se trabaja después de pagarlo con @pples (402)."""
    if not apples.is_unlocked(db, company_id, level):
        raise HTTPException(status_code=402, detail=(
            f"El Nivel {level} se activa con @pples. Cárgalas en tu billetera y paga el Nivel para seguir."))


async def transcribe_later(bind, llm: LLMAdapter, company_id: str, user_id: str, files: list[tuple[str, bytes]]) -> None:
    """Transcribe las grabaciones en el servidor y ADÁN aprende de ellas como de cualquier documento."""
    import os
    import tempfile
    db = Session(bind=bind)
    try:
        user = db.get(User, user_id)
        project = db.query(Project).filter(Project.company_id == company_id).first()
        level = db.query(Level).filter(Level.project_id == project.id, Level.number == 1).first()
        docs = []
        for name, data in files:
            suffix = doc_extract.extension(name) or ".bin"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(data)
                path = tmp.name
            try:
                text = await asyncio.to_thread(media.transcribe, path)
            except Exception as exc:  # noqa: BLE001
                text = ""
                logger.warning("No se pudo transcribir %s: %s", name, exc)
            finally:
                os.unlink(path)
            if text.strip():
                title = f"Transcripción de {name}"
                db.add(Document(project_id=project.id, title=title[:255], content=text, doc_type="client_upload",
                                origin="received_from_client", updated_by=user.name))
                db.commit()
                docs.append((title, text))
        service = Nivel1Service(llm, db)
        if docs:
            with usage_scope(db, company_id, 1):
                await service.learn_from_documents(project, level, docs)
        else:
            conversation = service.get_or_create_conversation(service.get_or_create_pain_card(project, level))
            db.add(Message(conversation_id=conversation.id, role="assistant", agent_name="ADÁN",
                           content="No pude transcribir la grabación. ¿Me la envías en otro formato (MP3, M4A o MP4)?"))
            db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("La transcripción en segundo plano falló")
    finally:
        db.close()


def schedule_work(background: BackgroundTasks, db: Session, llm: LLMAdapter, company_id: str, msg, nivel: int) -> None:
    """Lanza en segundo plano el recorrido o la revisión de código que pidió el turno."""
    work = (msg.metadata_json or {}).get("trabajando")
    if not work:
        return
    from app.levels import herramientas  # aquí: herramientas importa este módulo

    if work["tipo"] == "repositorio":
        background.add_task(herramientas.review_later, db.get_bind(), llm, company_id, work["url"], work.get("objetivo", ""), nivel)
    elif work["tipo"] == "recorrido":
        background.add_task(herramientas.walk_later, db.get_bind(), llm, company_id, work["url"], work["objetivo"], nivel)


async def research_later(bind, llm: LLMAdapter, company_id: str, conversation_id: str, query: str, user_id: str) -> None:
    """Termina la investigación anunciada en un turno, con su propia sesión de base de datos."""
    db = Session(bind=bind)
    try:
        conversation = db.get(Conversation, conversation_id)
        user = db.get(User, user_id)
        project = db.query(Project).filter(Project.company_id == company_id).first()
        if not conversation or not user or not project:
            return
        with usage_scope(db, company_id, 1):
            msg = await Nivel1Service(llm, db).complete_research(conversation, query)
        if msg is not None:
            auto_register_evidence(db, project, user, msg)
    except Exception:  # noqa: BLE001 - una búsqueda fallida no debe tumbar nada; el cliente puede volver a pedirla
        logger.exception("La investigación en segundo plano falló")
    finally:
        db.close()


@router.post("/{company_id}/chat", response_model=ChatResponse)
async def chat(
    company_id: str,
    body: ChatRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(llm_user),
    llm: LLMAdapter = Depends(get_llm),
    _usage: None = Depends(track_llm_usage),
):
    """Send a message in the Level 1 conversation."""
    get_owned_company(db, company_id, user)
    require_level_paid(db, company_id, 1)

    project = db.query(Project).filter(Project.company_id == company_id).first()
    level = db.query(Level).filter(
        Level.project_id == project.id, Level.number == 1
    ).first()

    if level and level.status != "active":
        raise HTTPException(status_code=400, detail="Level 1 is not active")

    service = Nivel1Service(llm, db)
    conversation = None
    if body.conversation_id:
        conversation = get_owned_conversation(db, body.conversation_id, project)

    msg, conv = await service.chat(project, level, body.message, conversation)
    auto_register_evidence(db, project, user, msg)
    pending = (msg.metadata_json or {}).get("investigando")
    if pending:
        # La respuesta sale ya; la búsqueda en internet sigue aparte y llega como otro mensaje
        background.add_task(research_later, db.get_bind(), llm, company_id, conv.id, pending["consulta"], user.id)
    schedule_work(background, db, llm, company_id, msg, 1)

    return ChatResponse(
        message=MessageResponse.model_validate(msg),
        conversation_id=conv.id,
    )


@router.post("/{company_id}/chat-stream")
async def chat_stream(
    company_id: str,
    body: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(llm_user),
    llm: LLMAdapter = Depends(get_llm),
    _usage: None = Depends(track_llm_usage),
):
    """Stream chat response token by token via SSE."""
    get_owned_company(db, company_id, user)
    require_level_paid(db, company_id, 1)

    project = db.query(Project).filter(Project.company_id == company_id).first()
    level = db.query(Level).filter(
        Level.project_id == project.id, Level.number == 1
    ).first()

    if level and level.status != "active":
        raise HTTPException(status_code=400, detail="Level 1 is not active")

    service = Nivel1Service(llm, db)
    conversation = None
    if body.conversation_id:
        conversation = get_owned_conversation(db, body.conversation_id, project)

    card = service.get_or_create_pain_card(project, level)
    if conversation is None:
        conversation = service.get_or_create_conversation(card)

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    db.commit()

    messages = service.build_llm_messages(conversation, structured=False)

    # Stream response. Each event is JSON so tokens with line breaks don't break SSE framing.
    async def generate():
        full_content = []
        try:
            with usage_scope(db, company_id, level=1):
                async for token in for_tier(llm, "standard").chat_stream(messages, temperature=0.7,
                                                                         max_tokens=512):
                    full_content.append(token)
                    yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True, 'disclaimer': AI_DISCLAIMER}, ensure_ascii=False)}\n\n"
        finally:
            # Save what was generated, even if the client disconnected mid-stream
            if full_content:
                db.add(Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content="".join(full_content),
                    metadata_json={"streamed": True},
                ))
                db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")


MAX_UPLOAD_FILES = 10
MAX_EMS_CHARS = 80_000


@router.post("/{company_id}/documents/upload")
async def upload_documents(
    company_id: str,
    background: BackgroundTasks,
    nivel: int = 1,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(llm_user),
    llm: LLMAdapter = Depends(get_llm),
    _usage: None = Depends(track_llm_usage),
):
    """El cliente carga su documentación (idea o empresa existente): ADÁN extrae el texto, lo guarda en la
    memoria de la empresa y aprende de él (guion del dolor, evidencia verificable, vacíos y riesgos)."""
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    level = db.query(Level).filter(Level.project_id == project.id, Level.number == nivel).first() or \
        db.query(Level).filter(Level.project_id == project.id, Level.number == 1).first()
    if len(files) > MAX_UPLOAD_FILES:
        raise HTTPException(status_code=400, detail=f"Sube máximo {MAX_UPLOAD_FILES} archivos a la vez.")

    extracted, errors = [], []
    for f in files:
        data = await f.read(doc_extract.MAX_MEDIA_BYTES + 1)
        try:
            extracted.append(doc_extract.extract(f.filename or "documento", data))
        except doc_extract.ExtractionError as exc:
            errors.append(str(exc))
    if not extracted:
        raise HTTPException(status_code=400, detail=" ".join(errors) or "No se pudo leer ningún archivo.")

    service = Nivel1Service(llm, db)
    card = service.get_or_create_level_card(project, level)
    conversation = service.get_or_create_conversation(card)
    # Lo que el cliente adjuntó queda a la vista en la conversación
    icons = {"Imagen": "🖼️", "Audio": "🎙️", "Video": "🎬"}
    db.add(Message(conversation_id=conversation.id, role="user", content="📎 Adjunté: " + ", ".join(
        f"{icons.get(d.kind, '📄')} {d.filename}" for d in extracted), metadata_json={"adjuntos": [
        {"nombre": d.filename, "tipo": d.kind} for d in extracted]}))
    db.commit()

    # Imágenes y PDFs escaneados: OCR ya; audio y video: se transcriben aparte (tardan)
    to_transcribe = [d for d in extracted if d.pending == "transcribir"]
    for d in extracted:
        if d.pending != "ocr":
            continue
        try:
            if d.kind == "Imagen":
                d.text = await media.ocr_image(d.data, media.IMAGE_TYPES.get(doc_extract.extension(d.filename), "image/png"))
            else:
                text, read = await media.ocr_pdf(d.data)
                if text.strip():
                    d.text = text
                    if d.pages > read:
                        errors.append(f"{d.filename}: era un PDF escaneado; leí con OCR las primeras {read} de {d.pages} páginas.")
        except media.MediaError as exc:
            errors.append(f"{d.filename}: {exc}")
        if len(d.text.strip()) < 20:
            errors.append(f"{d.filename}: no encontré texto legible.")
    extracted = [d for d in extracted if d.pending != "transcribir" and len(d.text.strip()) >= 20]

    saved = []
    ems = EnterpriseMemorySystem(db, embedding_provider, get_vector_store(db))
    for doc in extracted:
        record = Document(project_id=project.id, title=doc.filename[:255], content=doc.text,
                          doc_type="client_upload", origin="received_from_client", updated_by=user.name)
        db.add(record)
        db.commit()
        db.refresh(record)
        try:  # la memoria no debe frenar la carga: si falla, el Documento queda igual
            await ems.ingest(company_id=company_id, text=doc.text[:MAX_EMS_CHARS], title=doc.filename,
                             source_type="client_upload", source_name=doc.filename,
                             metadata={"document_id": record.id, "kind": doc.kind})
        except Exception:  # noqa: BLE001
            errors.append(f"{doc.filename}: quedó guardado, pero no entró a la memoria semántica esta vez.")
        saved.append({"id": record.id, "title": doc.filename, "kind": doc.kind, "pages": doc.pages,
                      "chars": len(doc.text), "truncated": doc.truncated})

    if extracted:
        result = await service.learn_from_documents(project, level, [(d.filename, d.text) for d in extracted])
    else:
        result = {"reply": "", "degraded": None, "learning": {}}
    if to_transcribe:
        names = ", ".join(d.filename for d in to_transcribe)
        note = Message(conversation_id=conversation.id, role="assistant", agent_name="ADÁN",
                       content=f"🎙️ Recibí {names}. Lo estoy transcribiendo; cuando termine te cuento aquí lo que entendí.",
                       metadata_json={"investigando": {"consulta": f"transcripción de {names}"}})
        db.add(note)
        db.commit()
        result["reply"] = (result["reply"] + "\n\n" if result["reply"] else "") + note.content
        background.add_task(transcribe_later, db.get_bind(), llm, company_id, user.id,
                            [(d.filename, d.data) for d in to_transcribe])
    return {"documents": saved, "errors": errors, "reply": result["reply"], "degraded": result["degraded"],
            "learning": result["learning"], "conversation_id": conversation.id,
            "discovery": discovery_progress(db, conversation, project)}


class ArenaStart(BaseModel):
    pitch: str = Field("", max_length=8000)


class ArenaAnswers(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict)


@router.post("/{company_id}/arena/start")
async def arena_start(company_id: str, body: ArenaStart | None = None, nivel: int = 1, db: Session = Depends(get_db),
                      user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm),
                      _usage: None = Depends(track_llm_usage)):
    """La Arena: cuatro inversionistas simulados escuchan la empresa y hacen sus preguntas más difíciles."""
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    brief = await Nivel1Service(llm, db).arena_brief(project, nivel)
    pitch = body.pitch.strip() if body else ""
    if not brief.strip() and not pitch:
        raise HTTPException(status_code=400, detail="Cuéntale primero a ADÁN tu empresa, o escribe tu pitch.")
    session = await Arena(llm, db).start(project, brief, pitch)
    timeline.arena_questions(db, project, session, nivel=nivel)
    return session


@router.post("/{company_id}/arena/{session_id}/answer")
async def arena_answer(company_id: str, session_id: str, body: ArenaAnswers, nivel: int = 1, db: Session = Depends(get_db),
                       user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm),
                       _usage: None = Depends(track_llm_usage)):
    """El fundador responde y cada inversionista decide si invierte, con cuánto y con qué condiciones."""
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    arena = Arena(llm, db)
    session = arena.get(project, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Esa sesión de La Arena no existe")
    if session["phase"] != "questions":
        raise HTTPException(status_code=409, detail="Esa sesión ya terminó: entra de nuevo a La Arena")
    answers = {k: v[:4000] for k, v in body.answers.items() if k in {i["id"] for i in session["investors"]}}
    result = await arena.answer(project, session, answers)
    texts = list(dict.fromkeys(v.strip() for v in answers.values() if v.strip()))
    timeline.arena_verdicts(db, project, "\n\n".join(texts) or "(sin respuesta)", result, nivel=nivel)
    return result


@router.get("/{company_id}/arena/last")
def arena_last(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    session = Arena(llm=None, db=db).get(project)  # type: ignore[arg-type]
    if not session:
        raise HTTPException(status_code=404, detail="Todavía no has entrado a La Arena")
    return session


@router.post("/{company_id}/board-room")
async def run_board_room(
    company_id: str,
    body: BoardRoomRequest | None = None,
    nivel: int = 1,
    db: Session = Depends(get_db),
    user: User = Depends(llm_user),
    llm: LLMAdapter = Depends(get_llm),
    _usage: None = Depends(track_llm_usage),
):
    """Board Room de 7 roles: el CEO abre y cierra, seis especialistas votan (AD-FUNC-02)."""
    company = get_owned_company(db, company_id, user)

    project = db.query(Project).filter(Project.company_id == company_id).first()

    service = Nivel1Service(llm, db)

    try:
        consensus = await service.run_board_room(project, company, client_question=body.question if body else "",
                                                 client_position=body.position if body else "", level_number=nivel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    timeline.board_session(db, project, consensus, nivel=nivel)  # la sesión también se cuenta en la conversación
    return _board_out(consensus)


@router.get("/{company_id}/board-room/last")
def last_board_room(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """La última sesión del Board Room, para verla de nuevo sin volver a ejecutarla."""
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    try:
        return _board_out(Nivel1Service(llm=None, db=db).get_last_board_consensus(project))
    except ValueError:
        raise HTTPException(status_code=404, detail="Todavía no hay sesiones del Board Room")


class BoardDialogueBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    agent: str | None = Field(None, max_length=20)  # None: al Board en general


@router.get("/{company_id}/board-room/dialogo")
def board_dialogue_thread(company_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """El diálogo con el Board desde su última sesión y el voto vigente de cada especialista."""
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    try:
        consensus = Nivel1Service(llm=None, db=db).get_last_board_consensus(project)
    except ValueError:
        raise HTTPException(status_code=404, detail="Todavía no hay sesiones del Board Room")
    turns = board_dialogue.thread(db, project)
    return {"thread": turns, "tally": board_dialogue.tally(board_dialogue.current_votes(consensus, turns))}


@router.post("/{company_id}/board-room/dialogo")
async def board_dialogue_reply(company_id: str, body: BoardDialogueBody, nivel: int = 1, db: Session = Depends(get_db),
                               user: User = Depends(llm_user), llm: LLMAdapter = Depends(get_llm),
                               _usage: None = Depends(track_llm_usage)):
    """Hablarle al Board o responderle a un especialista: profundiza, aporta evidencia o llega a un consenso."""
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    service = Nivel1Service(llm, db)
    try:
        consensus = service.get_last_board_consensus(project)
    except ValueError:
        raise HTTPException(status_code=404, detail="Primero ejecuta una sesión del Board Room")
    try:
        result = await board_dialogue.reply(llm, db, project, consensus, service.board_brief(project, nivel),
                                            body.message.strip(), body.agent)
        timeline.board_turn(db, project, result["turn"], nivel=nivel)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


class ContinueBody(BaseModel):
    reason: str = Field(..., min_length=3, max_length=2000)


@router.post("/{company_id}/board-room/continuar")
def board_continue_anyway(company_id: str, body: ContinueBody, nivel: int = 1, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    """El fundador ordena continuar aunque el Board no aprobó: queda constancia y afecta la calificación."""
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    try:
        consensus = Nivel1Service(llm=None, db=db).get_last_board_consensus(project)
    except ValueError:
        raise HTTPException(status_code=404, detail="Primero ejecuta una sesión del Board Room")
    result = board_dialogue.continue_anyway(db, project, consensus, body.reason.strip())
    timeline.post(db, project, body.reason.strip(), role="user", scene="board", nivel=nivel)
    timeline.post(db, project, nivel=nivel, content=f"⚖️ Queda en el acta: decidiste continuar con {len(result['open_objections'])} objeción(es) "
                  "abiertas. Respeto tu decisión; esto baja la calificación de la empresa. Para cerrar el Nivel, ve a "
                  "«Avance y cierre».", agent="ceo", scene="board")
    db.commit()
    return result


def _board_out(consensus) -> dict:
    return {
        "objective": consensus.objective,
        "decision_at_stake": consensus.decision_at_stake,
        "synthesis": consensus.synthesis,
        "evidence_requests": consensus.evidence_requests,
        "next_steps": consensus.next_steps,
        "client_question": consensus.client_question,
        "client_position": consensus.client_position,
        "minutes": consensus.minutes,
        "decision": consensus.decision,
        "score": consensus.score,
        "confidence": consensus.confidence,
        "summary": consensus.summary,
        "votes": [
            {
                "agent": v.agent,
                "analysis": v.analysis,
                "justification": v.justification,
                "vote": v.vote,
                "confidence": v.confidence,
                "key_strengths": v.key_strengths,
                "key_concerns": v.key_concerns,
                "questions": v.questions,
                "model": v.model,
                "duration_s": v.duration_s,
                "failure_mode": v.failure_mode,
                "bulletproof": v.bulletproof,
                "devils_advocate": v.devils_advocate,
            }
            for v in consensus.votes
        ],
        "concerns_unanimous": consensus.concerns_unanimous,
        "concerns_majority": consensus.concerns_majority,
        "strengths_unanimous": consensus.strengths_unanimous,
        "dissent": consensus.dissent,
        "failure_modes": consensus.failure_modes,
        "bulletproof_gaps": consensus.bulletproof_gaps,
        "disclaimer": AI_DISCLAIMER,
    }


@router.post("/{company_id}/diagnosis", response_model=DocumentResponse)
async def generate_diagnosis(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(llm_user),
    llm: LLMAdapter = Depends(get_llm),
    _usage: None = Depends(track_llm_usage),
):
    """Generate the Level 1 diagnosis document."""
    company = get_owned_company(db, company_id, user)

    project = db.query(Project).filter(Project.company_id == company_id).first()

    service = Nivel1Service(llm, db)

    # El Board vigente: no se ejecuta otro si ya hay uno y el cliente no ha aportado nada nuevo
    try:
        board_consensus, _reused = await service.ensure_board_room(project, company)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate diagnosis
    doc = await service.generate_diagnosis(project, company, board_consensus)

    # Calculate scores
    scores = await service.calculate_scores(project, board_consensus, doc.content)

    return DocumentResponse.model_validate(doc)


@router.post("/{company_id}/recommendations", response_model=DocumentResponse)
async def generate_recommendations(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(llm_user),
    llm: LLMAdapter = Depends(get_llm),
    _usage: None = Depends(track_llm_usage),
):
    """Generate recommendations based on diagnosis."""
    get_owned_company(db, company_id, user)

    project = db.query(Project).filter(Project.company_id == company_id).first()
    diagnosis_doc = get_latest_diagnosis(db, project)

    # Reuse the Board Room behind the diagnosis instead of running a new, different one
    service = Nivel1Service(llm, db)
    try:
        board_consensus = service.get_last_board_consensus(project)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = await service.generate_recommendations(
        project, diagnosis_doc.content, board_consensus
    )

    return DocumentResponse.model_validate(doc)


@router.post("/{company_id}/gate-review", response_model=GateReviewResponse)
async def gate_review(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    llm: LLMAdapter = Depends(get_llm),
):
    """Gate Review del Nivel 1 sobre la evidencia registrada (AD-CMP-05, WO-107).

    Si alcanza, propone cerrar el Nivel; si no, dice exactamente qué falta.
    """
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    get_latest_diagnosis(db, project)  # el Diagnóstico del Dolor es el entregable del Nivel 1

    result, decision = await Nivel1Service(llm, db).run_gate_review(project)
    return _gate_response(db, project, result, [decision] if decision else [])


@router.post("/{company_id}/advance-anyway", response_model=GateReviewResponse)
async def advance_anyway(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    llm: LLMAdapter = Depends(get_llm),
):
    """El cliente quiere avanzar sin evidencia suficiente (AD-CMP-01 §3).

    Se propone la decisión recomendando seguir; cerrar el Nivel exige decidir distinto a lo
    recomendado, con los riesgos y la responsabilidad que asume.
    """
    get_owned_company(db, company_id, user)
    project = db.query(Project).filter(Project.company_id == company_id).first()
    service = Nivel1Service(llm, db)
    try:
        decision = service.advance_without_evidence(project)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    result, _ = await service.run_gate_review_preview(project)
    return _gate_response(db, project, result, [decision])


def _gate_response(db: Session, project: Project, result, decisions: list) -> GateReviewResponse:
    level = db.query(Level).filter(Level.project_id == project.id, Level.number == 1).first()
    scores = db.query(Score).filter(Score.project_id == project.id).all()
    return GateReviewResponse(
        approved=result.approved,
        scores=[ScoreResponse.model_validate(s) for s in scores],
        decisions=[DecisionResponse.model_validate(d) for d in decisions],
        level_status=level.status.value if level else "unknown",
        message=result.message,
        problem_score=result.overall_score,
        confidence=result.confidence,
        missing=result.missing,
        evidence_breakdown=result.breakdown,
    )


@router.get("/{company_id}/decisions", response_model=list[DecisionResponse])
def list_decisions(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Decisiones del proyecto, las más recientes primero."""
    project = get_owned_project(db, company_id, user)
    decisions = db.query(Decision).filter(
        Decision.project_id == project.id,
    ).order_by(Decision.created_at.desc()).all()
    return [DecisionResponse.model_validate(d) for d in decisions]


@router.post("/{company_id}/decisions/{decision_id}", response_model=DecisionResponse)
def decide(
    company_id: str,
    decision_id: str,
    body: DecisionAction,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """El cliente aprueba o rechaza una decisión propuesta (Patrón A).

    Aprobar el cierre de un Nivel lo completa y activa el siguiente.
    """
    project = get_owned_project(db, company_id, user)
    decision = db.query(Decision).filter(
        Decision.id == decision_id,
        Decision.project_id == project.id,
    ).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    try:
        decision = GemeloDigitalService(db).decide(
            project, decision, body.action == "approve", user.id,
            chosen_option=body.chosen_option, risks_assumed=body.risks_assumed,
            responsibility_statement=body.responsibility_statement,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return DecisionResponse.model_validate(decision)


@router.get("/{company_id}/scores", response_model=list[ScoreResponse])
def get_scores(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all scores for a company."""
    project = get_owned_project(db, company_id, user)

    scores = db.query(Score).filter(Score.project_id == project.id).all()
    return [ScoreResponse.model_validate(s) for s in scores]


@router.get("/{company_id}/documents", response_model=list[DocumentResponse])
def get_documents(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all documents for a company."""
    project = get_owned_project(db, company_id, user)

    docs = db.query(Document).filter(Document.project_id == project.id).all()
    return [DocumentResponse.model_validate(d) for d in docs]
