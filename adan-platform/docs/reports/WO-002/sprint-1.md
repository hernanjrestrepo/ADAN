# WO-002 Sprint 1 — Capa de abstracción de modelos

**Célula:** C · **Fecha:** 2026-07-18

## Resumen ejecutivo

Interfaz única `ModelBackend` (generate, generate_stream, embed, generate_structured) — ningún agente futuro llamará a Ollama directamente, todo pasa por esta capa (BP-0001, AD-003 "Motor (de Capacidad)": Ollama es reemplazable, nunca dependencia fija). Adaptador Ollama real con reintentos (backoff simple) y timeouts configurables. `ModelCallRecord` registra proveedor+modelo+tokens+intentos por llamada (AD-002 regla 1.7 aplicada a inferencia).

## Archivos creados

`ai/pyproject.toml`, `ai/config.py`, `ai/db.py`, `ai/models/base.py`, `ai/models/ollama_adapter.py`, `ai/tests/test_ollama_adapter_functional.py`.

## Bugs encontrados

Ninguno bloqueante — la configuración de `packages.find` requirió `py-modules` explícito para `config.py`/`db.py` (módulos sueltos en la raíz de `/ai`, no paquetes).

## Evidencias objetivas

- Entorno real Python 3.12.13 (venv propio de `/ai`, independiente del de `/backend`).
- `ruff check .`: **All checks passed!**
- `pytest -v` (marcado `functional`, contra Ollama real del host, modelo `llama3.2:1b`): **4 passed** en 20.20s — generación completa, streaming, embeddings (`nomic-embed-text`), y salida estructurada, los cuatro con inferencia real, no simulada.

## Tiempo real (Wall Clock)

~20 minutos.

## Estado del Sprint

COMPLETO
