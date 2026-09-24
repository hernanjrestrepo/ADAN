"""
DKA API — Endpoint para Dynamic Knowledge Acquisition.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User, Company
from app.ems.memory import EnterpriseMemorySystem
from app.ems.store import embedding_provider, get_vector_store
from app.dka.pipeline import KnowledgeAcquisitionPipeline

router = APIRouter(prefix="/dka", tags=["dka"])


class AcquireRequest(BaseModel):
    query: str
    company_id: str
    urls: list[str] | None = None
    max_sources: int = 5


class AcquireResponse(BaseModel):
    query: str
    sources_scraped: int
    sources_succeeded: int
    sources_failed: int
    chunks_created: int
    avg_quality: float
    engine_used: str
    total_duration_ms: int
    documents: list[dict]
    errors: list[str]




@router.post("/acquire", response_model=AcquireResponse)
async def acquire_knowledge(
    request: AcquireRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Adquiere conocimiento desde Internet y lo almacena en EMS.
    
    Flujo: URL → Scrape → Normalize → Quality → EMS → Knowledge Graph
    """
    # Verificar empresa
    company = db.query(Company).filter(
        Company.id == request.company_id,
        Company.primary_user_id == current_user.id,
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    ems = EnterpriseMemorySystem(db, embedding_provider, get_vector_store(db))
    pipeline = KnowledgeAcquisitionPipeline(ems)

    result = await pipeline.acquire(
        query=request.query,
        company_id=request.company_id,
        urls=request.urls,
        max_sources=request.max_sources,
    )

    return AcquireResponse(
        query=result.query,
        sources_scraped=result.sources_scraped,
        sources_succeeded=result.sources_succeeded,
        sources_failed=result.sources_failed,
        chunks_created=result.chunks_created,
        avg_quality=result.avg_quality,
        engine_used=result.engine_used,
        total_duration_ms=result.total_duration_ms,
        documents=result.documents,
        errors=result.errors,
    )


@router.get("/health")
async def dka_health():
    return {
        "status": "healthy",
        "engines": ["crawl4ai", "scrapegraph", "firecrawl"],
        "version": "0.1.0-wo009",
    }
