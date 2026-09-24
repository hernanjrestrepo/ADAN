"""Nivel 1 endpoints — the complete Level 1 flow with real intelligence."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter
from app.ai.factory import get_llm_adapter
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import (
    Card, Company, Conversation, Document, Level, Message, Project, Score, User,
)
from app.nivel1.service import Nivel1Service
from app.schemas.schemas import (
    ChatRequest, ChatResponse, CompanyResponse, DocumentResponse,
    GateReviewResponse, LevelResponse, MessageResponse, ScoreResponse,
)

router = APIRouter(prefix="/nivel1", tags=["nivel1"])


def get_llm() -> LLMAdapter:
    return get_llm_adapter()


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
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

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
    user: User = Depends(get_current_user),
    llm: LLMAdapter = Depends(get_llm),
):
    """Send a message in the Level 1 conversation."""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

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
    user: User = Depends(get_current_user),
    llm: LLMAdapter = Depends(get_llm),
):
    """Stream chat response token by token via SSE."""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

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
    from datetime import datetime, timezone
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    db.commit()

    # Build messages for streaming
    from app.ai.base import LLMMessage
    history = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()

    message_count = len([m for m in history if m.role == "user"])
    system_prompt = service._build_chat_system_prompt(message_count, conversation.summary)

    messages = [LLMMessage(role="system", content=system_prompt)]
    for msg in history:
        messages.append(LLMMessage(role=msg.role, content=msg.content))

    # Stream response
    async def generate():
        full_content = []
        async for token in llm.chat_stream(messages, temperature=0.7, max_tokens=512):
            full_content.append(token)
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

        # Save complete response
        complete_response = "".join(full_content)
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=complete_response,
            metadata_json={"model": llm._default_model, "streamed": True},
        )
        db.add(assistant_msg)
        db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/{company_id}/board-room")
async def run_board_room(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    llm: LLMAdapter = Depends(get_llm),
):
    """Run the real Board Room with 4 independent agents."""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    project = db.query(Project).filter(Project.company_id == company_id).first()

    service = Nivel1Service(llm, db)

    try:
        consensus = await service.run_board_room(project, company)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
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
    }


@router.post("/{company_id}/diagnosis", response_model=DocumentResponse)
async def generate_diagnosis(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    llm: LLMAdapter = Depends(get_llm),
):
    """Generate the Level 1 diagnosis document."""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

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
    user: User = Depends(get_current_user),
    llm: LLMAdapter = Depends(get_llm),
):
    """Generate recommendations based on diagnosis."""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    project = db.query(Project).filter(Project.company_id == company_id).first()

    # Get diagnosis
    diagnosis_doc = db.query(Document).filter(
        Document.project_id == project.id,
        Document.doc_type == "diagnosis",
    ).first()

    if not diagnosis_doc:
        raise HTTPException(status_code=400, detail="Generate diagnosis first")

    # Get board consensus (re-run for now, could cache)
    service = Nivel1Service(llm, db)
    try:
        board_consensus = await service.run_board_room(project, company)
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
    """Run Gate Review with 80/100 minimum threshold."""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    project = db.query(Project).filter(Project.company_id == company_id).first()

    # Get diagnosis
    diagnosis_doc = db.query(Document).filter(
        Document.project_id == project.id,
        Document.doc_type == "diagnosis",
    ).first()

    if not diagnosis_doc:
        raise HTTPException(status_code=400, detail="Generate diagnosis first")

    # Get scores
    scores = db.query(Score).filter(Score.project_id == project.id).all()

    # Get deliverables
    documents = db.query(Document).filter(Document.project_id == project.id).all()
    deliverables = [d.title for d in documents]

    service = Nivel1Service(llm, db)

    # Run Board Room
    try:
        board_consensus = await service.run_board_room(project, company)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Run Gate Review
    result = await service.run_gate_review(
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
        decisions=[],
        level_status=level.status.value if level else "unknown",
        message=result.message,
    )


@router.get("/{company_id}/scores", response_model=list[ScoreResponse])
def get_scores(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all scores for a company."""
    project = db.query(Project).join(Company).filter(
        Project.company_id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scores = db.query(Score).filter(Score.project_id == project.id).all()
    return [ScoreResponse.model_validate(s) for s in scores]


@router.get("/{company_id}/documents", response_model=list[DocumentResponse])
def get_documents(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all documents for a company."""
    project = db.query(Project).join(Company).filter(
        Project.company_id == company_id,
        Company.primary_user_id == user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    docs = db.query(Document).filter(Document.project_id == project.id).all()
    return [DocumentResponse.model_validate(d) for d in docs]
