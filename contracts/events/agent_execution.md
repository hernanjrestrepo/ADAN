# Contrato de eventos — Ejecución de Agentes

Frontera entre `/backend` (productor de tareas) y `/ai` (consumidor/worker), vía Redis. Ninguna de las dos células importa código Python de la otra — este documento, más el esquema de la tabla `ejecuciones_agente`, es el contrato real.

## Cola de tareas

**Clave Redis:** `adan:agent_runs:queue` (lista, `LPUSH`/`BRPOP`).

**Mensaje (JSON):**

```json
{
  "execution_id": "uuid-v4",
  "agent_id": "diagnostico-nivel-1",
  "user_input": "texto libre del usuario",
  "proyecto_id": "uuid-v4 | null"
}
```

`execution_id` lo genera el productor (`/backend`) antes de encolar, para poder consultar el estado en Postgres inmediatamente sin esperar a que el worker lo procese.

## Canal de eventos de progreso

**Clave Redis:** `adan:agent_runs:{execution_id}:events` (pub/sub).

**Mensajes (JSON):**

```json
{"type": "started", "payload": {"agent_id": "..."}}
{"type": "completed", "payload": {"final_output": "...", "error": null}}
{"type": "failed", "payload": {"final_output": null, "error": "mensaje"}}
{"type": "cancelled", "payload": {"final_output": null, "error": null}}
```

## Tabla `ejecuciones_agente` (Postgres, esquema compartido)

Propiedad de `/ai` (define y migra la tabla), leída por `/backend` para servir el historial al frontend. Ninguna célula importa el modelo ORM de la otra — cada una mapea la tabla con su propio `Base`.

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID | = `execution_id` del mensaje de cola |
| `agent_id` | string(100) | |
| `proyecto_id` | UUID, nullable | FK real a `proyectos.id` |
| `status` | string(20) | pending\|running\|completed\|failed\|cancelled |
| `user_input` | text | |
| `final_output` | text, nullable | |
| `transcript` | jsonb, nullable | lista de pasos `{step_number, prompt, output}` |
| `prompt_tokens`, `completion_tokens` | int, nullable | del último paso |
| `error` | text, nullable | |
| `created_at`, `finished_at` | timestamptz | |

Cualquier cambio a este esquema requiere actualizar este documento en el mismo commit.
