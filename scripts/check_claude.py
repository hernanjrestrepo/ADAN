#!/usr/bin/env python3
"""Verifica la conexión con Claude (WO-099) con la clave real, sin tocar la base de datos.

    ANTHROPIC_API_KEY=sk-ant-... python scripts/check_claude.py

Hace dos llamadas: una conversación (nivel "standard") y un voto del Board con salida
estructurada (nivel "complex"). Muestra el modelo que respondió, los tokens y el costo.
Sale con código 1 si algo falla o si la respuesta cae a Ollama.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ.setdefault("ADAN_ENV", "development")

from app.ai.base import LLMMessage  # noqa: E402
from app.ai.ollama_adapter import OllamaAdapter  # noqa: E402
from app.ai.router import ModelRouter  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.nivel1.board_room import AGENT_PROMPTS, VOTE_SCHEMA  # noqa: E402


async def main() -> int:
    if not settings.ANTHROPIC_API_KEY:
        print("✗ Falta ANTHROPIC_API_KEY")
        return 1
    router = ModelRouter(OllamaAdapter())
    ok = True
    chat = await router.for_tier("standard").chat(
        [LLMMessage("system", "Eres ADÁN. Responde en una frase."), LLMMessage("user", "¿Qué haces?")])
    ok &= _report("Conversación (standard)", chat)
    vote = await router.for_tier("complex").chat_json(
        [LLMMessage("system", AGENT_PROMPTS["CFO"]["system"]),
         LLMMessage("user", "Analiza: panaderías de barrio botan 15 % del pan cada día.")], VOTE_SCHEMA)
    ok &= _report("Voto del Board (complex, JSON)", vote)
    if vote.parsed:
        print(f"  voto: {vote.parsed.get('vote')} · confianza {vote.parsed.get('confidence')}")
    else:
        print("  ✗ el voto no llegó como JSON válido")
        ok = False
    return 0 if ok else 1


def _report(name, response) -> bool:
    degraded = response.metadata.get("degraded")
    mark = "✗" if degraded else "✓"
    print(f"{mark} {name}: {response.provider or 'ollama'}:{response.model} · "
          f"{response.prompt_tokens}+{response.completion_tokens} tokens · US$ {response.cost_usd:.4f}"
          + (f" · DEGRADADO: {degraded}" if degraded else ""))
    return not degraded


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
