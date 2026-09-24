#!/bin/bash
# Pull the default model after Ollama is healthy
echo "Waiting for Ollama to be ready..."
until curl -sf http://ollama:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done
echo "Ollama is ready. Pulling model: ${DEFAULT_MODEL:-qwen2.5:0.5b}"
curl -sf http://ollama:11434/api/pull -d "{\"name\": \"${DEFAULT_MODEL:-qwen2.5:0.5b}\"}" --max-time 300
echo "Model pull complete."
