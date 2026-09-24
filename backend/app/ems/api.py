"""
EMS API — Endpoints para el Enterprise Memory System.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, Company
from app.ems.memory import EnterpriseMemorySystem
from app.ems.store import embedding_provider, get_vector_store

router = APIRouter(prefix="/ems", tags=["ems"])


# ============================================================
# Schemas
# ============================================================

class IngestRequest(BaseModel):
    company_id: str
    text: str
    title: str
    source_type: str = "text"
    source_name: str | None = None
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
    query: str
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
    original_text: str
    corrected_text: str
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
    company = db.query(Company).filter(
        Company.id == request.company_id,
        Company.primary_user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

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
    company = db.query(Company).filter(
        Company.id == request.company_id,
        Company.primary_user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

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
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

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
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.primary_user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

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
    company = db.query(Company).filter(
        Company.id == request.company_id,
        Company.primary_user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

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
async def ems_health():
    """Health check del EMS."""
    return {
        "status": "healthy",
        "embedding_provider": "LocalEmbeddingProvider",
        "vector_store": "LocalVectorStoreProvider",
        "version": "0.1.0-wo004",
    }
