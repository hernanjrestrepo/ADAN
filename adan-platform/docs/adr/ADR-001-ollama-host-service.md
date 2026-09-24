# ADR-001 — Reutilizar el Ollama del host en vez de contenerizarlo

**Estado:** RATIFICADO (protocolo de Enmienda 2: se elige la opción que maximiza reutilización y camino crítico, se marca RATIFICADO en el mismo sprint por no tener impacto reversible negativo)
**Fecha:** 2026-07-17 · **Célula:** A · **WO/Sprint:** WO-001 Sprint 2

## Contexto

El Plan Maestro (§4) especifica "Ollama self-hosted detrás de capa de abstracción de modelos", y el docker-compose de WO-001 Sprint 2 lista `ollama` como uno de los servicios a levantar. El entorno de desarrollo ya tiene Ollama 0.23.1 corriendo nativamente en el host, con 13 modelos descargados (varios GB: qwen2.5-coder:14b, deepseek-coder-v2:16b, llama3.1:8b, etc.).

## Decisión

El servicio `api` en `docker-compose.yml` se conecta al Ollama **del host** vía `http://host.docker.internal:11434`, en vez de levantar un contenedor `ollama` adicional. No se descarga ni duplica ningún modelo.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Contenedor `ollama` independiente con volumen propio | Duplicaría ~40GB de modelos ya descargados en el host; viola la regla de reutilización del Plan Maestro §7 ("reutilizar todo componente que reduzca tiempo, reduzca riesgo") |
| Contenedor `ollama` que monta el volumen de modelos del host | Ollama en Windows no expone su directorio de modelos en una ruta trivialmente montable desde WSL2/Docker Desktop sin configuración adicional frágil |

## Impacto

- `infra/docker-compose.yml`: no hay servicio `ollama`; `api` recibe `OLLAMA_BASE_URL=http://host.docker.internal:11434` por variable de entorno.
- La capa de abstracción de modelos (WO-002 Sprint 1) apunta a esa URL por configuración, nunca hardcodeada — si en producción se decide contenerizar Ollama, el cambio es de una variable de entorno, no de código.
- BP-0001 (AD-000, Motor del Ecosistema) — Ollama sigue siendo un proveedor reemplazable detrás de la capa de abstracción, coherente con la definición de AD-003.

## Reversibilidad

Totalmente reversible: agregar un servicio `ollama` al compose y cambiar la variable de entorno no requiere tocar código de aplicación, solo configuración.

## Ratificación

RATIFICADO por la Célula D en el mismo sprint — reduce tiempo, reduce riesgo, no compromete la arquitectura (Plan Maestro §7).
