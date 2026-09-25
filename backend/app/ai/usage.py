"""Costo y uso de cada llamada al modelo (WO-099, AD-IA-03).

- Métricas Prometheus por proveedor, modelo y nivel: tokens y costo en USD.
- Dentro de `usage_scope(db, company_id, level)` cada llamada queda además registrada en
  `llm_usage`, para medir el costo por empresa (proyecto) y por Nivel.
"""
from __future__ import annotations

import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone

from prometheus_client import Counter
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String

from app.core.database import Base

LLM_TOKENS = Counter("adan_llm_tokens_total", "Tokens de las llamadas al LLM", ["provider", "model", "tier", "kind"])
LLM_COST = Counter("adan_llm_cost_usd_total", "Costo estimado de las llamadas al LLM (USD)", ["provider", "model", "tier"])
LLM_DEGRADED = Counter("adan_llm_degraded_total", "Llamadas que cayeron a Ollama por falta de Claude", ["tier"])


class LLMUsage(Base):
    __tablename__ = "llm_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    level_number = Column(Integer, nullable=True)
    operation = Column(String(50), nullable=False)
    tier = Column(String(20), nullable=False)
    provider = Column(String(20), nullable=False)
    model = Column(String(100), nullable=False)
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)
    degraded = Column(String(200), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (Index("idx_llm_usage_company_created", "company_id", "created_at"),)


_scope: ContextVar[dict | None] = ContextVar("llm_usage_scope", default=None)


def record_usage(response, tier: str, operation: str) -> None:
    provider = response.provider or "ollama"
    LLM_TOKENS.labels(provider, response.model, tier, "input").inc(response.prompt_tokens or 0)
    LLM_TOKENS.labels(provider, response.model, tier, "output").inc(response.completion_tokens or 0)
    LLM_COST.labels(provider, response.model, tier).inc(response.cost_usd or 0.0)
    degraded = response.metadata.get("degraded")
    if degraded:
        LLM_DEGRADED.labels(tier).inc()
    scope = _scope.get()
    if scope is not None:
        scope["records"].append(LLMUsage(
            company_id=scope["company_id"], level_number=scope["level"], operation=operation, tier=tier,
            provider=provider, model=response.model, input_tokens=response.prompt_tokens or 0,
            output_tokens=response.completion_tokens or 0, cost_usd=response.cost_usd or 0.0,
            degraded=degraded,
        ))


@contextmanager
def usage_scope(db, company_id: str, level: int | None = None):
    """Registra en `llm_usage` las llamadas hechas dentro del bloque (también si falla)."""
    scope = {"company_id": company_id, "level": level, "records": []}
    token = _scope.set(scope)
    try:
        yield scope
    finally:
        _scope.reset(token)
        if scope["records"]:
            db.add_all(scope["records"])
            db.commit()
