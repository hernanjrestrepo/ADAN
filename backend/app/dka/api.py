"""
DKA API — Endpoint para Dynamic Knowledge Acquisition.
"""

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.schemas.schemas import MAX_MESSAGE_CHARS
from app.core.authz import get_owned_company
from app.core.ratelimit import llm_user
from app.models.models import User
from app.ems.memory import EnterpriseMemorySystem
from app.ems.store import embedding_provider, get_vector_store
from app.dka.pipeline import KnowledgeAcquisitionPipeline

router = APIRouter(prefix="/dka", tags=["dka"])


class AcquireRequest(BaseModel):
    query: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    company_id: str
    urls: list[str] | None = Field(default=None, max_length=20)
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
    current_user: User = Depends(llm_user),
    db: Session = Depends(get_db),
):
    """
    Adquiere conocimiento desde Internet y lo almacena en EMS.
    
    Flujo: URL → Scrape → Normalize → Quality → EMS → Knowledge Graph
    """
    # Verificar empresa
    get_owned_company(db, request.company_id, current_user)

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
