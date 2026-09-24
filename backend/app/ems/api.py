"""
EMS API — Endpoints para el Enterprise Memory System.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.schemas.schemas import MAX_DOCUMENT_CHARS, MAX_MESSAGE_CHARS, MAX_TITLE_CHARS
from app.core.auth import get_current_user
from app.core.authz import get_owned_company
from app.models.models import User
from app.ems.memory import EnterpriseMemorySystem
from app.ems.store import describe_providers, embedding_provider, get_vector_store

router = APIRouter(prefix="/ems", tags=["ems"])


# ============================================================
# Schemas
# ============================================================

class IngestRequest(BaseModel):
    company_id: str
    text: str = Field(min_length=1, max_length=MAX_DOCUMENT_CHARS)
    title: str = Field(min_length=1, max_length=MAX_TITLE_CHARS)
    source_type: str = Field(default="text", max_length=50)
    source_name: str | None = Field(default=None, max_length=MAX_TITLE_CHARS)
    metadata: dict | None = None


class IngestResponse(BaseModel):
    document_id: str
    status: str
    chunks_created: int
    embeddings_generated: int
    vector_records_upserted: int
    duration_ms: int
    error: str | None = None


class RetrieveRequest(BaseModel):
    company_id: str
    query: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    top_k: int = 5


class RetrieveResponse(BaseModel):
    query: str
    chunks: list[dict]
    facts: list[dict]
    documents: list[dict]
    total_results: int
    sources: list[str]
    context_text: str


class DocumentResponse(BaseModel):
    id: str
    title: str
    source_type: str
    status: str
    version: int
    confidence: float
    chunks_count: int
    created_at: str | None


class StatsResponse(BaseModel):
    documents: int
    chunks: int
    facts: int
    corrections: int
    vector_store_size: int


class CorrectionRequest(BaseModel):
    company_id: str
    original_text: str = Field(max_length=MAX_MESSAGE_CHARS)
    corrected_text: str = Field(max_length=MAX_MESSAGE_CHARS)
    fact_id: str | None = None
    chunk_id: str | None = None
    reason: str | None = None


# ============================================================
# Dependency: EMS instance
# ============================================================

def get_ems(db: Session = Depends(get_db)) -> EnterpriseMemorySystem:
    return EnterpriseMemorySystem(db, embedding_provider, get_vector_store(db))


# ============================================================
# Endpoints
# ============================================================

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    current_user: User = Depends(get_current_user),
    ems: EnterpriseMemorySystem = Depends(get_ems),
):
    """Ingresa un documento al sistema de memoria empresarial."""
    # Verificar que la empresa pertenece al usuario
    db = ems.db
    get_owned_company(db, request.company_id, current_user)

    result = await ems.ingest(
        company_id=request.company_id,
        text=request.text,
        title=request.title,
        source_type=request.source_type,
        source_name=request.source_name,
        metadata=request.metadata,
    )

    return IngestResponse(
        document_id=result.document_id,
        status=result.status,
        chunks_created=result.chunks_created,
        embeddings_generated=result.embeddings_generated,
        vector_records_upserted=result.vector_records_upserted,
        duration_ms=result.duration_ms,
        error=result.error,
    )


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_knowledge(
    request: RetrieveRequest,
    current_user: User = Depends(get_current_user),
    ems: EnterpriseMemorySystem = Depends(get_ems),
):
    """Recupera conocimiento relevante para una query."""
    db = ems.db
    get_owned_company(db, request.company_id, current_user)

    result = await ems.retrieve(
        company_id=request.company_id,
        query=request.query,
        top_k=request.top_k,
    )

    return RetrieveResponse(
        query=result.query,
        chunks=result.chunks,
        facts=result.facts,
        documents=result.documents,
        total_results=result.total_results,
        sources=list(set(result.sources)),
        context_text=result.context_text,
    )


@router.get("/documents/{company_id}", response_model=list[DocumentResponse])
async def list_documents(
    company_id: str,
    current_user: User = Depends(get_current_user),
    ems: EnterpriseMemorySystem = Depends(get_ems),
):
    """Lista documentos de una empresa."""
    db = ems.db
    get_owned_company(db, company_id, current_user)

    docs = ems.list_documents(company_id)
    return [
        DocumentResponse(
            id=doc.id,
            title=doc.title,
            source_type=doc.source_type,
            status=doc.status,
            version=doc.version,
            confidence=doc.confidence,
            chunks_count=len(doc.chunks) if doc.chunks else 0,
            created_at=doc.created_at.isoformat() if doc.created_at else None,
        )
        for doc in docs
    ]


@router.get("/stats/{company_id}", response_model=StatsResponse)
async def get_stats(
    company_id: str,
    current_user: User = Depends(get_current_user),
    ems: EnterpriseMemorySystem = Depends(get_ems),
):
    """Obtiene estadísticas del EMS para una empresa."""
    db = ems.db
    get_owned_company(db, company_id, current_user)

    stats = ems.get_stats(company_id)
    return StatsResponse(**stats)


@router.post("/correct")
async def record_correction(
    request: CorrectionRequest,
    current_user: User = Depends(get_current_user),
    ems: EnterpriseMemorySystem = Depends(get_ems),
):
    """Registra una corrección del usuario al conocimiento."""
    db = ems.db
    get_owned_company(db, request.company_id, current_user)

    correction = ems.record_correction(
        company_id=request.company_id,
        original_text=request.original_text,
        corrected_text=request.corrected_text,
        fact_id=request.fact_id,
        chunk_id=request.chunk_id,
        reason=request.reason,
        created_by=str(current_user.id),
    )

    return {
        "correction_id": correction.id,
        "status": "recorded",
    }


@router.get("/health")
async def ems_health(db: Session = Depends(get_db)):
    """Health check del EMS: dice qué embeddings y qué índice vectorial están activos."""
    return {
        "status": "healthy",
        **describe_providers(db),
        "version": "0.2.0-wo091",
    }
