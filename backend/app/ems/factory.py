"""Construcción única del EMS para todos los routers (WO-091).

Antes cada router (ems, agents, board, dka) creaba su propio vector store en
memoria: lo ingerido por un módulo no era visible para los demás y se perdía
al reiniciar. Ahora todos comparten el vector store persistente en BD.
"""
from __future__ import annotations

from functools import lru_cache

from sqlalchemy.orm import Session

from app.core.config import settings
from app.ems.memory import EnterpriseMemorySystem
from app.ems.providers import EmbeddingProvider, LocalEmbeddingProvider, OllamaEmbeddingProvider
from app.ems.vector_store import SQLVectorStoreProvider


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.EMBEDDING_PROVIDER.strip().lower()
    if provider == "local":
        return LocalEmbeddingProvider(dim=settings.EMBEDDING_DIM)
    if provider == "ollama":
        return OllamaEmbeddingProvider(settings.OLLAMA_BASE_URL, settings.EMBEDDING_MODEL)
    raise RuntimeError(f"EMBEDDING_PROVIDER={provider!r} unknown. Available: ['local', 'ollama']")


def build_ems(db: Session) -> EnterpriseMemorySystem:
    """EMS ligado a la sesión de la request, con vector store persistente."""
    return EnterpriseMemorySystem(db, get_embedding_provider(), SQLVectorStoreProvider(db))
