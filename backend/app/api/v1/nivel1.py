"""Nivel 1 endpoints — the complete Level 1 flow with real intelligence."""
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.ai.factory import get_llm_adapter
from app.core.auth import get_current_user
from app.core.authz import get_owned_company, get_owned_project
from app.core.ratelimit import llm_user
from app.core.database import get_db
from app.core.disclaimer import AI_DISCLAIMER
from app.models.models import (
    Card, Conversation, Decision, Document, Level, Message, Project, Score, User,
)
from app.nivel1.service import Nivel1Service
from app.services.gemelo_digital import GemeloDigitalService
from app.ai.router import for_tier
from app.ai.usage import usage_scope
from app.schemas.schemas import (
    BoardRoomRequest, ChatRequest, ChatResponse, CompanyResponse, DecisionAction, DecisionResponse,
    DocumentResponse, GateReviewResponse, LevelResponse, MessageResponse, ScoreResponse,
)

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
    }


@router.post("/{company_id}/chat", response_model=ChatResponse)
async def chat(
    company_id: str,
    body: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(llm_user),
    llm: LLMAdapter = Depends(get_llm),
    _usage: None = Depends(track_llm_usage),
):
    """Send a message in the Level 1 conversation."""
    get_owned_company(db, company_id, user)

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

    messages = service.build_llm_messages(conversation)

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


@router.post("/{company_id}/board-room")
async def run_board_room(
    company_id: str,
    body: BoardRoomRequest | None = None,
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
                                                 client_position=body.position if body else "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
            }
            for v in consensus.votes
        ],
        "concerns_unanimous": consensus.concerns_unanimous,
        "concerns_majority": consensus.concerns_majority,
        "strengths_unanimous": consensus.strengths_unanimous,
        "dissent": consensus.dissent,
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

    # Run Board Room first
    try:
        board_consensus = await service.run_board_room(project, company)
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
    _usage: None = Depends(track_llm_usage),
):
    """Run Gate Review with 80/100 minimum threshold."""
    get_owned_company(db, company_id, user)

    project = db.query(Project).filter(Project.company_id == company_id).first()
    diagnosis_doc = get_latest_diagnosis(db, project)

    # Get scores
    scores = db.query(Score).filter(Score.project_id == project.id).all()

    # Get deliverables
    documents = db.query(Document).filter(Document.project_id == project.id).all()
    deliverables = [d.title for d in documents]

    service = Nivel1Service(llm, db)

    # Evaluate the same Board Room that produced the diagnosis
    try:
        board_consensus = service.get_last_board_consensus(project)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Run Gate Review
    result, decision = await service.run_gate_review(
        project,
        diagnosis_doc.content,
        board_consensus,
        scores,
        deliverables,
    )

    # Get updated level
    level = db.query(Level).filter(
        Level.project_id == project.id, Level.number == 1
    ).first()

    return GateReviewResponse(
        approved=result.approved,
        scores=[ScoreResponse.model_validate(s) for s in scores],
        decisions=[DecisionResponse.model_validate(decision)] if decision else [],
        level_status=level.status.value if level else "unknown",
        message=result.message,
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
        decision = GemeloDigitalService(db).decide(project, decision, body.action == "approve", user.id)
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
