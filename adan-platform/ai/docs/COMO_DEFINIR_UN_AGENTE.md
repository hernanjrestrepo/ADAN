# Cómo definir un Agente nuevo

Un Agente (AD-003: "la unidad interna de especialización de ADÁN, ej. rol de CEO, CTO, CFO") se define en 4 pasos. Usa `ai/agents/diagnostico.py` como referencia completa.

## 1. Crear el archivo de definición

`ai/agents/<nombre>.py`:

```python
from agents.base import AgentDefinition

MI_AGENTE_ID = "mi-agente-id"  # unico, en minusculas con guiones

_INSTRUCCIONES = """\
Tus instrucciones aqui - ancladas en un documento del blueprint (AD-FUNC-XX),
nunca inventadas libremente. Cita la seccion exacta en un comentario arriba.
"""

def build_mi_agente() -> AgentDefinition:
    return AgentDefinition(
        agent_id=MI_AGENTE_ID,
        rol="CTO",  # o el rol que corresponda - ver AD-003 "Agente"
        instrucciones=_INSTRUCCIONES,
        max_steps=1,   # esta version del runtime ejecuta un solo paso (Sprint 2)
        max_tokens=1000,
    )
```

**Antes de escribir las instrucciones:** verifica contra el Principio de Emergencia (¿ya existe un Agente que cubra esto?) y contra el Criterio de Existencia (AD-004 §3.1) — ¿modifica el Gemelo Digital, mejora el conocimiento del cliente, o produce evidencia útil? Si no, no se construye.

## 2. Registrarlo en el worker

En `ai/worker.py`, dentro de `bootstrap_agents()`:

```python
from agents.mi_agente import build_mi_agente

def bootstrap_agents() -> None:
    register_agent(build_diagnostico_agent())
    register_agent(build_mi_agente())  # nueva linea
```

## 3. Declararlo en el backend

En `backend/app/routers/agents.py`, agregar el `agent_id` a `KNOWN_AGENT_IDS`:

```python
KNOWN_AGENT_IDS = {"diagnostico-nivel-1", "mi-agente-id"}
```

Esta duplicación es deliberada — `/backend` y `/ai` no se importan mutuamente (Plan Maestro §3.2). Si el `agent_id` no está en esta lista, `POST /agents/run` devuelve 404 antes de llegar a la cola.

## 4. Reiniciar el worker

`docker compose exec` no aplica hot-reload de código Python — reinicia el proceso del worker (o reconstruye el contenedor `api`/`web` si tocaste `/backend` o `/frontend`) para que el nuevo Agente quede disponible. Ver deuda técnica registrada en `docs/reports/WO-002/sprint-4.md` (falta bind-mount + `--reload` en desarrollo).

## Herramientas y memoria (opcional, todavía mínimo)

`AgentDefinition.tools` y `AgentRuntime.memory_hook` existen desde Sprint 2 pero con implementación mínima — el runtime actual no hace tool-calling en loop (un solo paso de inferencia por ejecución) ni tiene memoria semántica real (eso llega en WO-003, Knowledge Graph). No construyas herramientas reales todavía sin un caso de uso concreto que las necesite — Economía Conceptual.
