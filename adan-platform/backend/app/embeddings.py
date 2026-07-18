"""Cliente minimo de embeddings - llama a Ollama directamente para /kg/query, sin
importar ai.models.ollama_adapter (Plan Maestro SS3.2). Duplica intencionalmente la
llamada HTTP minima (no toda la capa de abstraccion de /ai, que incluye generate/stream/
reintentos con fines de generacion de texto, no de embeddings). Si esta duplicacion crece,
es la senal para extraer un contrato compartido - no antes (Economia Conceptual)."""

import httpx

from app.config import get_settings


def embed_text(text: str, model: str = "nomic-embed-text", timeout_s: float = 30.0) -> list[float]:
    settings = get_settings()
    resp = httpx.post(
        f"{settings.ollama_base_url}/api/embed",
        json={"model": model, "input": text},
        timeout=timeout_s,
    )
    resp.raise_for_status()
    body = resp.json()
    embeddings = body.get("embeddings", [[]])
    return embeddings[0] if embeddings else []
