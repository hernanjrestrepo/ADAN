# EVENT_BUS — Sistema de Eventos de ADÁN

**WO:** WO-002.1  
**Fecha:** 2026-07-24  
**Estado:** Diseño (sin implementar)  
**Prerequisito:** WO-001 cerrada, WO-002 baseline congelado

---

## 1. Visión General

El Event Bus es el sistema nervioso de ADÁN. Todo lo que pasa en el sistema — cada acción, cada cambio, cada decisión — se publica como un evento. Los agentes se suscriben a los eventos que les interesan y reaccionan en consecuencia.

**Principio:** El sistema de eventos es el backbone de trazabilidad. Si algo pasó, hay un evento. Si algo se puede reconstruir, se reconstruye desde eventos.

---

## 2. Arquitectura

### 2.1 Diagrama

```
┌─────────────────────────────────────────────────────────────┐
│                        EVENT BUS                             │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Publisher   │    │    Router    │    │  Subscriber  │  │
│  │              │    │              │    │              │  │
│  │  Cualquier   │───▶│  Filtra y    │───▶│  Agentes     │  │
│  │  fuente      │    │  rutea       │    │  suscritos   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    Store     │    │   Replay     │    │  Dead Letter │  │
│  │              │    │              │    │              │  │
│  │  Persiste    │    │  Re-ejecuta  │    │  Eventos no  │  │
│  │  eventos     │    │  eventos     │    │  procesados  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes

| Componente | Responsabilidad |
|---|---|
| Publisher | Publica eventos desde cualquier fuente |
| Router | Filtra y rutea eventos a suscriptores correctos |
| Subscriber | Recibe y procesa eventos |
| Store | Persiste eventos en la BD (ya implementado en tabla `events`) |
| Replay | Permite re-ejecutar eventos desde un punto en el tiempo |
| Dead Letter | Maneja eventos que no pudieron procesarse |

---

## 3. Estructura de Evento

### 3.1 Evento Base

```python
class Event:
    # Identificación
    id: UUID
    type: str                          # "decision_made", "level_completed", etc.
    
    # Origen
    source: str                        # "planner", "executor", "board_room", etc.
    agent_id: str | None               # agente específico que generó el evento
    
    # Contexto
    project_id: UUID                   # proyecto afectado
    company_id: UUID | None            # empresa afectada (si aplica)
    conversation_id: UUID | None       # conversación afectada (si aplica)
    
    # Datos
    payload: dict                      # datos específicos del tipo de evento
    
    # Trazabilidad
    parent_event_id: UUID | None       # evento que causó este evento
    trace_id: str                      # ID de trazabilidad para串联 eventos
    
    # Metadatos
    timestamp: datetime
    version: str                       # versión del schema del evento
    metadata: dict                     # metadatos adicionales
    
    # Estado
    processed: bool                    # ¿fue procesado?
    processed_at: datetime | None
    processing_error: str | None
```

### 3.2 Payload por Tipo de Evento

| Tipo de Evento | Payload |
|---|---|
| `user_message` | `{ message_id, content, role }` |
| `assistant_message` | `{ message_id, content, agent, tokens, duration_ms }` |
| `decision_proposed` | `{ decision_id, title, proposed_by, options }` |
| `decision_made` | `{ decision_id, selected_option, confidence, reasoning }` |
| `decision_executed` | `{ decision_id, outcome, quality_score }` |
| `decision_reversed` | `{ decision_id, reason }` |
| `board_room_started` | `{ agents: [CEO, CTO, CFO, CMO] }` |
| `board_room_completed` | `{ consensus, votes, duration_ms }` |
| `gate_review_started` | `{ level_number }` |
| `gate_review_completed` | `{ approved, score, criteria }` |
| `level_activated` | `{ level_number, level_name }` |
| `level_completed` | `{ level_number, level_name }` |
| `diagnosis_generated` | `{ document_id, title, word_count }` |
| `recommendation_generated` | `{ document_id, title, word_count }` |
| `score_calculated` | `{ score_type, value, confidence }` |
| `tool_executed` | `{ tool_id, status, duration_ms, output_preview }` |
| `tool_failed` | `{ tool_id, error, retry_count }` |
| `memory_consolidated` | `{ source_type, target_type, entries_processed }` |
| `memory_archived` | `{ memory_type, entry_id, reason }` |
| `knowledge_extracted` | `{ entity_type, entity_id, facts }` |
| `knowledge_updated` | `{ entity_type, entity_id, changes }` |
| `user_consultation` | `{ question, options, deadline }` |
| `user_response` | `{ consultation_id, selected_option, additional_info }` |
| `quality_issue_detected` | `{ dimension, severity, description }` |
| `quality_issue_resolved` | `{ issue_id, resolution }` |
| `error_occurred` | `{ error_type, message, stack_trace, context }` |
| `system_health` | `{ cpu, memory, active_agents, queue_size }` |

---

## 4. Tipos de Evento

### 4.1 Clasificación por Categoría

| Categoría | Tipos de Evento | Descripción |
|---|---|---|
| **Conversación** | `user_message`, `assistant_message`, `conversation_started`, `conversation_ended` | Eventos de interacción con el usuario |
| **Decisión** | `decision_proposed`, `decision_made`, `decision_executed`, `decision_reversed` | Eventos de toma de decisiones |
| **Board Room** | `board_room_started`, `board_room_completed`, `agent_vote_cast` | Eventos del sistema multi-agente |
| **Gate Review** | `gate_review_started`, `gate_review_completed` | Eventos de evaluación |
| **Nivel** | `level_activated`, `level_completed`, `card_created`, `card_completed` | Eventos de progreso |
| **Documento** | `diagnosis_generated`, `recommendation_generated`, `document_created` | Eventos de generación de contenido |
| **Score** | `score_calculated`, `score_updated` | Eventos de scoring |
| **Herramienta** | `tool_executed`, `tool_failed`, `tool_timeout` | Eventos de ejecución de herramientas |
| **Memoria** | `memory_consolidated`, `memory_compressed`, `memory_archived`, `memory_retrieved` | Eventos del sistema de memoria |
| **Knowledge** | `knowledge_extracted`, `knowledge_updated`, `knowledge_superseded` | Eventos del knowledge graph |
| **Ciclo de Vida** | `session_started`, `session_ended`, `plan_created`, `plan_executed` | Eventos del ciclo de vida |
| **Calidad** | `quality_issue_detected`, `quality_issue_resolved` | Eventos de calidad |
| **Sistema** | `error_occurred`, `system_health`, `agent_state_changed` | Eventos del sistema |

### 4.2 Clasificación por Impacto

| Impacto | Tipos de Evento | Acción |
|---|---|---|
| **Crítico** | `error_occurred`, `decision_reversed` | Alerta inmediata al usuario |
| **Alto** | `decision_made`, `level_completed`, `gate_review_completed` | Notificación al usuario |
| **Medio** | `board_room_completed`, `diagnosis_generated`, `tool_executed` | Log y monitoreo |
| **Bajo** | `user_message`, `assistant_message`, `memory_consolidated` | Solo log |

---

## 5. Publicación de Eventos

### 5.1 API de Publicación

```python
class EventBus:
    def publish(self, event: Event) -> str:
        """
        Publica un evento en el bus.
        Retorna el event_id.
        """
        # 1. Validar evento
        self._validate_event(event)
        
        # 2. Persistir en BD (append-only)
        self._store(event)
        
        # 3. Router a suscriptores
        subscribers = self._route(event)
        
        # 4. Entregar a suscriptores
        for subscriber in subscribers:
            self._deliver(event, subscriber)
        
        # 5. Registrar métricas
        self._record_metrics(event)
        
        return event.id
```

### 5.2 Publicación Síncrona vs Asíncrona

| Tipo | Uso | Ejemplo |
|---|---|---|
| Síncrona | Eventos que requieren procesamiento inmediato | `decision_made`, `user_consultation` |
| Asíncrona | Eventos que pueden procesarse después | `memory_consolidated`, `tool_executed` |

```python
# Publicación síncrona (bloquea hasta que todos los suscriptores procesen)
event_bus.publish_sync(Event(type="user_consultation", ...))

# Publicación asíncrona (retorna inmediatamente)
event_bus.publish_async(Event(type="memory_consolidated", ...))
```

---

## 6. Suscripción de Eventos

### 6.1 API de Suscripción

```python
class EventBus:
    def subscribe(
        self,
        subscriber_id: str,
        event_types: list[str],
        handler: Callable[[Event], None],
        filter: dict | None = None
    ) -> str:
        """
        Suscribe un handler a tipos de evento específicos.
        Retorna subscription_id.
        """
        subscription = Subscription(
            id=generate_uuid(),
            subscriber_id=subscriber_id,
            event_types=event_types,
            handler=handler,
            filter=filter,
            created_at=datetime.now()
        )
        
        self._subscriptions.append(subscription)
        return subscription.id
```

### 6.2 Suscripciones por Agente

| Agente | Eventos que Escucha |
|---|---|
| Planner | `user_message`, `decision_executed`, `quality_issue_detected` |
| Executor | `plan_created`, `tool_executed`, `tool_failed` |
| Observer | `*` (todos los eventos — para monitoreo) |
| Critic | `assistant_message`, `diagnosis_generated`, `recommendation_generated` |
| Reviewer | `decision_proposed`, `board_room_completed` |
| Memory Manager | `session_ended`, `decision_made`, `knowledge_extracted` |
| Tool Manager | `tool_executed`, `tool_failed`, `tool_timeout` |
| Event Manager | `*` (todos los eventos — para métricas) |

### 6.3 Filtrado de Eventos

```python
# Suscribirse a eventos de un proyecto específico
event_bus.subscribe(
    subscriber_id="observer-1",
    event_types=["*"],
    filter={"project_id": "project-123"}
)

# Suscribirse a eventos de alta severidad
event_bus.subscribe(
    subscriber_id="alert-manager",
    event_types=["error_occurred", "quality_issue_detected"],
    filter={"severity": "critical"}
)

# Suscribirse a eventos de un agente específico
event_bus.subscribe(
    subscriber_id="executor-1",
    event_types=["tool_executed", "tool_failed"],
    filter={"source": "board_room"}
)
```

---

## 7. Routing de Eventos

### 7.1 Pipeline de Routing

```
Evento entrante
       │
       ▼
┌─────────────────┐
│ 1. VALIDATE      │  → ¿El evento es válido?
│    EVENT         │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 2. PERSIST       │  → Guardar en BD (tabla events)
│                  │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 3. FIND          │  → ¿Quién está suscrito a este tipo?
│    SUBSCRIBERS   │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 4. APPLY         │  → ¿El evento pasa los filtros?
│    FILTERS       │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 5. DELIVER       │  → Entregar a cada suscriptor
│    TO EACH       │
└──────────┬──────┘
           │
       ┌───┴───┐
       │       │
   Éxito    Fallo
       │       │
       ▼       ▼
┌──────────┐ ┌──────────┐
│ 6. MARK  │ │ 7. RETRY │
│ PROCESSED│ │    or    │
│          │ │ DEAD     │
└──────────┘ │ LETTER   │
             └──────────┘
```

### 7.2 Implementación del Router

```python
class EventRouter:
    def route(self, event: Event) -> list[DeliveryResult]:
        results = []
        
        # 1. Encontrar suscriptores que matchean el tipo
        matching = [
            s for s in self._subscriptions
            if event.type in s.event_types or "*" in s.event_types
        ]
        
        # 2. Aplicar filtros
        for subscription in matching:
            if self._matches_filter(event, subscription.filter):
                # 3. Entregar
                try:
                    subscription.handler(event)
                    results.append(DeliveryResult(
                        event_id=event.id,
                        subscriber_id=subscription.subscriber_id,
                        delivered=True
                    ))
                except Exception as e:
                    results.append(DeliveryResult(
                        event_id=event.id,
                        subscriber_id=subscription.subscriber_id,
                        delivered=False,
                        error=str(e)
                    ))
        
        return results
    
    def _matches_filter(self, event: Event, filter: dict | None) -> bool:
        if not filter:
            return True
        
        for key, value in filter.items():
            event_value = getattr(event, key, None) or event.payload.get(key)
            if event_value != value:
                return False
        
        return True
```

---

## 8. Persistencia

### 8.1 Tabla `events` (ya implementada)

La tabla `events` ya existe en el esquema actual:

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL,
    event_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    data JSON,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### 8.2 Extensión del Esquema

Para el sistema de eventos completo, se extiende la tabla:

```sql
ALTER TABLE events ADD COLUMN source TEXT;              -- agente/fuente
ALTER TABLE events ADD COLUMN agent_id TEXT;            -- agente específico
ALTER TABLE events ADD COLUMN company_id UUID;          -- empresa
ALTER TABLE events ADD COLUMN conversation_id UUID;     -- conversación
ALTER TABLE events ADD COLUMN parent_event_id UUID;     -- evento padre
ALTER TABLE events ADD COLUMN trace_id TEXT;            -- trazabilidad
ALTER TABLE events ADD COLUMN version TEXT DEFAULT '1.0'; -- versión del schema
ALTER TABLE events ADD COLUMN metadata JSON;            -- metadatos
ALTER TABLE events ADD COLUMN processed BOOLEAN DEFAULT FALSE;
ALTER TABLE events ADD COLUMN processed_at TIMESTAMP;
ALTER TABLE events ADD COLUMN processing_error TEXT;

-- Índices para queries comunes
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_source ON events(source);
CREATE INDEX idx_events_trace ON events(trace_id);
CREATE INDEX idx_events_project_type ON events(project_id, event_type);
CREATE INDEX idx_events_unprocessed ON events(processed) WHERE processed = FALSE;
```

### 8.3 Append-Only

La tabla `events` es **append-only**: nunca se actualiza ni se borra un registro. Esto garantiza:
- Trazabilidad completa
- Posibilidad de replay
- Auditoría
- Integridad de datos

---

## 9. Replay

### 9.1 ¿Qué es el Replay?

El replay permite re-ejecutar eventos desde un punto en el tiempo. Es útil para:
- Depurar problemas
- Reproducir comportamiento
- Auditar decisiones
- Entrenar agentes

### 9.2 API de Replay

```python
class EventReplay:
    def replay_from(
        self,
        start_time: datetime,
        end_time: datetime | None = None,
        event_types: list[str] | None = None,
        project_id: UUID | None = None
    ) -> ReplayResult:
        """
        Re-ejecuta eventos desde start_time hasta end_time.
        """
        # 1. Recuperar eventos del rango
        events = self._get_events(start_time, end_time, event_types, project_id)
        
        # 2. Re-ejecutar cada evento
        results = []
        for event in events:
            result = self._replay_event(event)
            results.append(result)
        
        return ReplayResult(
            events_replayed=len(results),
            success=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            results=results
        )
    
    def replay_trace(self, trace_id: str) -> ReplayResult:
        """
        Re-ejecuta todos los eventos de un trace_id específico.
        """
        events = self._get_events_by_trace(trace_id)
        return self._replay_events(events)
```

---

## 10. Dead Letter Queue

### 10.1 ¿Qué es?

Cuando un evento no puede ser procesado después de N reintentos, se envía a la Dead Letter Queue (DLQ). Los eventos en la DLQ se revisan manualmente o se procesan con una estrategia de fallback.

### 10.2 Política de DLQ

| Intentos | Acción |
|---|---|
| 1 | Reintentar inmediatamente |
| 2 | Reintentar con delay de 1s |
| 3 | Reintentar con delay de 5s |
| 4 | Enviar a DLQ |

### 10.3 Estructura de DLQ

```python
class DeadLetterEntry:
    event: Event
    subscriber_id: str
    attempts: int
    last_error: str
    entered_at: datetime
    status: pending | resolved | discarded
    resolved_at: datetime | None
    resolution: str | None
```

### 10.4 API de DLQ

```python
class DeadLetterQueue:
    def get_pending(self) -> list[DeadLetterEntry]:
        """Retorna eventos pendientes de revisión."""
        return [e for e in self._entries if e.status == "pending"]
    
    def resolve(self, entry_id: UUID, resolution: str):
        """Marca un evento como resuelto."""
        entry = self._get(entry_id)
        entry.status = "resolved"
        entry.resolved_at = datetime.now()
        entry.resolution = resolution
    
    def retry(self, entry_id: UUID):
        """Re-intenta procesar un evento de la DLQ."""
        entry = self._get(entry_id)
        self._reprocess(entry)
    
    def discard(self, entry_id: UUID, reason: str):
        """Descarta un evento de la DLQ."""
        entry = self._get(entry_id)
        entry.status = "discarded"
        entry.resolution = f"Discarded: {reason}"
```

---

## 11. Métricas

### 11.1 Métricas por Tipo de Evento

| Métrica | Descripción |
|---|---|
| `events_published_total` | Total de eventos publicados (por tipo) |
| `events_processed_total` | Total de eventos procesados |
| `events_failed_total` | Total de eventos fallidos |
| `events_dlq_total` | Total de eventos en DLQ |
| `event_processing_time_seconds` | Tiempo promedio de procesamiento |
| `event_delivery_latency_seconds` | Latencia promedio de delivery |
| `event_throughput_per_second` | Eventos publicados por segundo |

### 11.2 Métricas por Suscriptor

| Métrica | Descripción |
|---|---|
| `subscriber_events_received_total` | Eventos recibidos por suscriptor |
| `subscriber_events_processed_total` | Eventos procesados por suscriptor |
| `subscriber_events_failed_total` | Eventos fallidos por suscriptor |
| `subscriber_processing_time_seconds` | Tiempo promedio de procesamiento por suscriptor |

### 11.3 Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                   EVENT BUS DASHBOARD                        │
│                                                              │
│  Throughput: 12.5 events/sec                                │
│  Processed: 14,320 (last hour)                              │
│  Failed: 23 (0.16%)                                         │
│  DLQ: 3 pending                                             │
│                                                              │
│  Events by Type (last hour):                                │
│  ─────────────────────────────                              │
│  user_message         ████████████████████  4,230           │
│  assistant_message    ████████████████      3,120           │
│  tool_executed        ████████████          2,340           │
│  decision_made        ██████                1,230           │
│  memory_consolidated  ████                    890           │
│  quality_issue        █                       45           │
│                                                              │
│  Subscribers:                                                │
│  ─────────────────────────────                              │
│  planner        1,230 received  100% success                │
│  executor       3,450 received   99.8% success              │
│  observer       14,320 received 100% success                │
│  critic         2,340 received   99.5% success              │
│  memory_mgr     890 received    100% success                │
│                                                              │
│  Alerts:                                                     │
│  ⚠ critic: 0.5% failure rate (threshold: 1%)              │
│  ℹ DLQ: 3 events pending manual review                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 12. Trazabilidad

### 12.1 Trace ID

Cada secuencia de eventos relacionados comparte un `trace_id`. Esto permite reconstruir la cadena completa de eventos para una operación:

```
trace_id: "abc-123"
  │
  ├── Event: user_message (query: "analiza mi mercado")
  ├── Event: plan_created (steps: [recover, board_room, generate])
  ├── Event: memory_retrieved (facts: 5, episodes: 3)
  ├── Event: board_room_started (agents: CEO, CTO, CFO, CMO)
  ├── Event: agent_vote_cast (agent: CEO, vote: PROCEED)
  ├── Event: agent_vote_cast (agent: CTO, vote: PROCEED)
  ├── Event: agent_vote_cast (agent: CFO, vote: PIVOT)
  ├── Event: agent_vote_cast (agent: CMO, vote: PROCEED)
  ├── Event: board_room_completed (consensus: PROCEED, score: 75)
  ├── Event: tool_executed (tool: document_generate, status: success)
  ├── Event: diagnosis_generated (doc_id: xyz, words: 1200)
  ├── Event: quality_issue_detected (dimension: completeness, severity: medium)
  ├── Event: tool_executed (tool: document_generate, status: success)
  ├── Event: diagnosis_generated (doc_id: xyz-v2, words: 1500)
  ├── Event: quality_issue_resolved (issue_id: qi-1)
  ├── Event: assistant_message (content: "Aquí está tu análisis...")
  └── Event: memory_consolidated (short_term → long_term)
```

### 12.2 Búsqueda por Trace

```python
# Buscar todos los eventos de una operación
events = event_bus.search_by_trace("abc-123")

# Reconstruir la cadena de eventos
chain = event_bus.reconstruct_chain("abc-123")

# Buscar eventos fallidos en una cadena
failures = event_bus.find_failures_in_trace("abc-123")
```

---

## 13. Integración con el Sistema Actual

### 13.1 Lo que Ya Existe

| Componente | Estado | Uso Actual |
|---|---|---|
| Tabla `events` | Implementada | Gemelo Digital registra eventos |
| `_record_event()` | Implementada | Cada cambio en GemeloDigital genera evento |
| Event types | 7 tipos definidos | `level_activated`, `level_completed`, `diagnosis_saved`, etc. |

### 13.2 Lo que Falta

| Componente | Estado | Prioridad |
|---|---|---|
| Router | No implementado | Alta |
| Subscribers | No implementados | Alta |
| Replay | No implementado | Media |
| Dead Letter Queue | No implementado | Media |
| Métricas | No implementadas | Baja |
| Dashboard | No implementado | Baja |
| Trace ID | No implementado | Alta |

### 13.3 Migración

El sistema actual de eventos se extiende (no se reemplaza):
1. Se agregan columnas a la tabla `events`
2. Se mantiene compatibilidad con el esquema actual
3. Los eventos existentes siguen siendo válidos
4. Los nuevos campos son opcionales (default values)

---

**Este diseño está CONGELADO.**  
**Las implementaciones futuras deben adherirse a esta especificación.**  
**Los cambios de diseño requieren Work Order específica.**
