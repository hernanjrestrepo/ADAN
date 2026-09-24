# ADR-001: Construcción del Vertical Nivel 1

**Fecha:** 2026-07-23
**Estado:** Aceptado
**Decisor:** Hernán / CTO

## Contexto

ADÁN tiene un blueprint conceptual completo (21 documentos congelados WO-000) pero cero código. El Board decide construir el primer vertical funcional (Nivel 1) antes de escribir más documentación de arquitectura, validando el blueprint contra la realidad.

## Decisión

Construir Nivel 1 como vertical completo y funcional con:

- **Backend:** Python 3.12 + FastAPI
- **Frontend:** React + Vite + Tailwind CSS
- **Base de datos:** SQLite (suficiente para fase local; abstracto para migrar a Postgres)
- **IA:** Ollama + Qwen via adaptador abstracto
- **Infraestructura:** Docker Compose (backend + frontend + ollama)
- **Auth:** JWT simple (bcrypt + python-jose)

## Patrón de Abstracción de Modelo

Reutilizado del patrón `TransportAdapter` de ollama-worker:

```
LLMAdapter (ABC)
  ├── OllamaAdapter (local, Qwen)
  ├── OpenAIAdapter (futuro)
  └── AnthropicAdapter (futuro)
```

Cambiar de modelo = cambiar adapter. Nunca acoplar a un proveedor.

## Modelo de Datos (Nivel 1)

Entidades del Gemelo Digital para Nivel 1:

| Entidad | Tabla | Fuente |
|---|---|---|
| Usuario | `users` | AD-006 §4 |
| Empresa | `companies` | AD-005 §2.1 |
| Proyecto | `projects` | AD-006 §4 |
| Nivel | `levels` | AD-006 §4 |
| Card | `cards` | AD-006 §4 |
| Conversación | `conversations` | AD-006 §4 |
| Mensaje | `messages` | AD-006 §4 |
| Score | `scores` | AD-006 §4 |
| Decisión | `decisions` | AD-006 §4 |
| Documento | `documents` | AD-005 §2.4 |
| Evento | `events` | AD-006 §4 |

## Flujo Nivel 1

```
Login → Crear Empresa → Onboarding → Dolor (Card) → Board Room → Diagnóstico → Gate Review → Score → Entregable → Gemelo Digital
```

## Consecuencias

- SQLite es suficiente para validación local; la migración a Postgres será un cambio de connection string
- El adaptador Ollama es el primer adaptador; OpenAI/Anthropic se agregan como hermanos
- Todo el estado del Gemelo Digital persiste en SQLite con versionado
- Docker Compose orquesta backend + frontend + ollama en un solo `docker compose up`
