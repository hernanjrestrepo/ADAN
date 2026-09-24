"""Funcional contra Ollama real (host) - BP-0001. Requiere Ollama corriendo en el host
con al menos 'llama3.2:1b' y 'nomic-embed-text' descargados."""

import pytest

from models.ollama_adapter import OllamaBackend

pytestmark = pytest.mark.functional


@pytest.fixture
def backend() -> OllamaBackend:
    return OllamaBackend()


def test_generate_real_inference(backend: OllamaBackend) -> None:
    result = backend.generate("Responde solo con la palabra: hola", timeout_s=30.0)
    assert isinstance(result.text, str)
    assert len(result.text) > 0
    assert result.call_record.provider == "ollama"
    assert result.call_record.model == "llama3.2:1b"
    assert result.call_record.attempt == 1
    assert result.call_record.error is None


def test_generate_stream_real_inference(backend: OllamaBackend) -> None:
    chunks = list(backend.generate_stream("Cuenta del 1 al 3", timeout_s=30.0))
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert len(full_text) > 0


def test_embed_real_inference(backend: OllamaBackend) -> None:
    vector = backend.embed("empresa de tecnologia")
    assert isinstance(vector, list)
    assert len(vector) > 0
    assert all(isinstance(v, float) for v in vector[:5])


def test_generate_structured_real_inference(backend: OllamaBackend) -> None:
    result = backend.generate_structured(
        "Extrae el nombre de esta empresa: 'Paradixe es una empresa de tecnologia'",
        schema_hint='{"nombre_empresa": "string"}',
        timeout_s=30.0,
    )
    assert isinstance(result.text, str)
    assert len(result.text) > 0
