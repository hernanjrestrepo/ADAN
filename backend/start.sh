#!/bin/bash
# Wait for Ollama to be ready before starting the backend
echo "Waiting for Ollama at ${OLLAMA_BASE_URL:-http://ollama:11434}..."
until curl -sf "${OLLAMA_BASE_URL:-http://ollama:11434}/api/tags" > /dev/null 2>&1; do
    sleep 2
done
echo "Ollama is ready. Starting ADÁN backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
