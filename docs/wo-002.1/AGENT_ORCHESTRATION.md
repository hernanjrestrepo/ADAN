# AGENT_ORCHESTRATION — Cómo se Orquestan los Agentes de ADÁN

**WO:** WO-002.1  
**Fecha:** 2026-07-24  
**Estado:** Diseño (sin implementar)  
**Prerequisito:** WO-001 cerrada, WO-002 baseline congelado

---

## 1. Visión General

ADÁN opera como una organización con roles especializados. Cada agente tiene una responsabilidad clara, entradas definidas, salidas específicas y estados posibles. No son chatbots independientes — son componentes de un sistema orquestado que trabaja en conjunto.

**Principio fundamental:** Ningún agente actúa solo sin que el orquestador lo autorice. Ningún agente modifica el estado del sistema directamente — todos los cambios pasan por el orquestador.

---

## 2. Los 8 Agentes

### 2.1 Planner (Planeador)

**Responsabilidad:** Determinar qué hacer antes de hacerlo.

**¿Qué es?**  
El Planner recibe la solicitud del usuario y produce un plan de ejecución: qué pasos son necesarios, en qué orden, qué herramientas se necesitan, y qué agentes deben participar.

**Entradas:**
- Mensaje del usuario (Working Memory)
- Contexto de la empresa (Semantic Memory)
- Historial reciente (Short-Term Memory)
- Estado actual del proyecto (Gemelo Digital)

**Salidas:**
```python
Plan:
    goal: str                          # objetivo claro de la solicitud
    steps: list[PlanStep]              # pasos numerados
    required_agents: list[AgentType]   # agentes que deben participar
    required_tools: list[ToolRef]      # herramientas necesarias
    estimated_iterations: int          # iteraciones estimadas
    fallback_strategy: str             # qué hacer si falla

PlanStep:
    order: int
    description: str
    agent: AgentType
    inputs: list[str]                  # qué datos necesita
    outputs: list[str]                 # qué datos produce
    depends_on: list[int]              # pasos de los que depende
    optional: bool                     # si se puede omitir
```

**Estados:**
```
 idle → planning → plan_ready → (esperando ejecución)
                    plan_ready → plan_revised → plan_ready
                    plan_ready → plan_approved → executing
```

**Comportamiento:**
- Analiza la intención del usuario
- Consulta la memoria semántica para contexto
- Decide si la solicitud es simple (respuesta directa) o compleja (requiere plan)
- Para solicitudes simples: produce un plan de 1 paso (responder directamente)
- Para solicitudes complejas: descompone en múltiples pasos
- Puede revisar el plan si la ejecución falla

**Interacción con otros agentes:**
- Recibe input de todos los agentes (para revisar el plan)
- Envía el plan al Executor para ejecución
- Consulta al Observer si hay dudas sobre el enfoque

---

### 2.2 Executor (Ejecutor)

**Responsabilidad:** Ejecutar los pasos del plan.

**¿Qué es?**  
El Executor toma cada paso del plan y lo ejecuta: llama a herramientas, invoca agentes especializados, procesa resultados.

**Entradas:**
- Plan aprobado (del Planner)
- Paso actual a ejecutar
- Resultados de pasos anteriores
- Working Memory actualizada

**Salidas:**
```python
StepResult:
    step_order: int
    status: success | failed | skipped
    output: Any                        # resultado del paso
    tool_calls: list[ToolCall]         # herramientas invocadas
    duration_ms: int
    error: str | None

ExecutionResult:
    plan_id: UUID
    steps_completed: int
    steps_total: int
    results: list[StepResult]
    status: completed | failed | partially_completed
    output: Any                        # resultado final consolidado
```

**Estados:**
```
 idle → executing → step_running → step_completed
                     step_running → step_failed → retry_or_skip
                     executing → completed
                     executing → failed
```

**Comportamiento:**
- Ejecuta pasos en orden (respetando dependencias)
- Para pasos paralelos (sin dependencias): ejecuta concurrentemente
- Si un paso falla: aplica fallback strategy del plan
- Si el fallback falla: reporta al Planner para revisión
- Registra cada paso执行ut en el sistema de eventos

**Interacción con otros agentes:**
- Ejuta llamadas a agentes especializados (Board Room, Gate Review, etc.)
- Invoca Tool Manager para ejecutar herramientas
- Reporta resultados al Observer

---

### 2.3 Observer (Observador)

**Responsabilidad:** Monitorear la ejecución y detectar problemas.

**¿Qué es?**  
El Observer vigila la ejecución del plan en tiempo real. Detecta anomalías, mide calidad, y alerta cuando algo sale mal.

**Entradas:**
- Stream de eventos de ejecución
- Resultados de cada paso
- Métricas de performance
- UMBRALQuality thresholds

**Salidas:**
```python
Observation:
    timestamp: datetime
    event_type: step_started | step_completed | step_failed | quality_issue | performance_degradation
    severity: info | warning | critical
    message: str
    metrics: dict                      # métricas relevantes
    recommendation: str | None         # acción sugerida

QualityReport:
    overall_score: float               # 0-1
    dimensions: dict[str, float]       # scoring por dimensión
    issues: list[Observation]
    passed: bool
```

**Estados:**
```
 idle → monitoring → monitoring
                     → anomaly_detected → alert_sent → monitoring
                     → quality_issue → issue_logged → monitoring
```

**Comportamiento:**
- Escucha eventos de ejecución sin bloquear
- Compara resultados contra umbrales de calidad
- Detecta patrones de fallo repetitivos
- Mide tiempos de ejecución y alerta si exceden umbrales
- Genera reportes de calidad al final de la ejecución

**Dimensiones de calidad monitoreadas:**
- Completitud: ¿Se ejecutaron todos los pasos?
- Consistencia: ¿Los resultados son coherentes entre sí?
- Performance: ¿Los tiempos son aceptables?
- Costo: ¿Se excedió el presupuesto de tokens?
- Confianza: ¿Los agentes están seguros de sus respuestas?

---

### 2.4 Critic (Crítico)

**Responsabilidad:** Evaluar la calidad de las respuestas antes de entregarlas al usuario.

**¿Qué es?**  
El Critic revisa las salidas del sistema y las evalúa contra criterios de calidad. Detecta alucinaciones, inconsistencias, información faltante, y respuestas incompletas.

**Entradas:**
- Respuesta propuesta
- Contexto de la empresa
- Pregunta original del usuario
- Criterios de calidad del dominio

**Salidas:**
```python
Critique:
    response_id: UUID
    overall_score: float               # 0-1
    dimensions: dict[str, float]       # scoring por dimensión
    issues: list[QualityIssue]
    suggestions: list[str]
    approved: bool                     # ¿Se entrega al usuario?
    revised_response: str | None       # Si no aprueba, versión revisada

QualityIssue:
    dimension: factual_accuracy | completeness | relevance | clarity | consistency
    severity: low | medium | high | critical
    description: str
    location: str                      # dónde en la respuesta
    suggestion: str
```

**Estados:**
```
 idle → reviewing → approved → delivered
                    → issues_found → revisions_requested → reviewing
                    → critical_issue → blocked → escalated
```

**Comportamiento:**
- Evalúa cada respuesta antes de entregarla al usuario
- Verifica coherencia con el knowledge graph
- Detecta contradicciones con información previa
- Mide completitud contra la pregunta del usuario
- Si aprueba: la respuesta se entrega
- Si rechaza: solicita revisión al agente que generó la respuesta
- Si hay issue crítico: escala al usuario

**Criterios de evaluación:**
| Criterio | Descripción | Peso |
|---|---|---|
| Exactitud factual | La información es correcta según el knowledge graph | 0.30 |
| Completitud | Responde todo lo que el usuario preguntó | 0.25 |
| Relevancia | La información es relevante para el contexto | 0.20 |
| Claridad | La respuesta es clara y comprensible | 0.15 |
| Consistencia | No contradice información previa | 0.10 |

---

### 2.5 Reviewer (Revisor)

**Responsabilidad:** Revisar decisiones estratégicas antes de que se ejecuten.

**¿Qué es?**  
El Reviewer evalúa decisiones de alto impacto (inversiones, cambios de dirección, contrataciones) antes de que se confirmen. No evalúa calidad técnica (eso es el Critic) — evalúa mérito estratégico.

**Entradas:**
- Decisión propuesta
- Contexto del mercado
- Historial de decisiones similares
- Estado financiero del proyecto

**Salidas:**
```python
ReviewDecision:
    decision_id: UUID
    recommendation: approve | reject | defer | request_more_info
    confidence: float                  # 0-1
    reasoning: str
    risks_identified: list[Risk]
    alternatives: list[str]
    conditions: list[str]              # condiciones para aprobar

Risk:
    description: str
    probability: float                 # 0-1
    impact: float                      # 0-1
    mitigation: str
```

**Estados:**
```
 idle → reviewing → approved → executed
                    → rejected → decision_revoked
                    → deferred → pending_info → reviewing
                    → escalated → user_decision_required
```

**Comportamiento:**
- Solo se activa para decisiones clasificadas como "alto impacto"
- Consulta la memoria episódica para decisiones similares pasadas
- Evalúa riesgos y alternativas
- Puede aprobar, rechazar, diferir o escalar al usuario
- No tiene poder de veto absoluto — el usuario puede aprobar de todas formas

**Criterios de activación del Reviewer:**
| Tipo de Decisión | Activa Reviewer |
|---|---|
| Inversión > $10,000 | Sí |
| Cambio de modelo de negocio | Sí |
| Contratación de personal | Sí |
| Cambio de mercado objetivo | Sí |
| Aprobación de presupuesto | Sí |
| Decisión operativa rutinaria | No |
| Respuesta a pregunta del usuario | No |

---

### 2.6 Memory Manager (Gestor de Memoria)

**Responsabilidad:** Gestionar el ciclo de vida de toda la memoria del sistema.

**¿Qué es?**  
El Memory Manager coordina la consolidación, compresión, archivado y recuperación de información entre los 6 tipos de memoria.

**Entradas:**
- Eventos de ejecución
- Solicitudes de recuperación de otros agentes
- Señales de consolidación (fin de sesión, umbral de tamaño)
- Señales de olvido (relevance_score bajo)

**Salidas:**
```python
MemoryOperation:
    operation: create | consolidate | compress | archive | forget | retrieve
    memory_type: working | short_term | long_term | episodic | semantic | procedural
    entity_id: UUID
    success: bool
    result: Any

RetrievalResult:
    query: str
    results: list[MemoryEntry]
    total_found: int
    within_budget: bool                # ¿cabe en el presupuesto de atención?
    budget_used: int                   # tokens gastados
    budget_remaining: int

ConsolidationResult:
    source_type: str
    target_type: str
    entries_processed: int
    entries_consolidated: int
    space_saved: int                   # tokens reducidos
    information_preserved: float       # 0-1, cuánto significado se preservó
```

**Estados:**
```
 idle → processing → idle
       → consolidating → consolidated → idle
       → compressing → compressed → idle
       → retrieving → results_ready → idle
       → archiving → archived → idle
```

**Comportamiento:**
- Ejecuta consolidación automática al final de cada sesión
- Ejecuta compresión periódica (diaria)
- Responde a solicitudes de recuperación de otros agentes
- Gestiona el presupuesto de atención
- Detecta y archiva información obsoleta
- Nunca borra información permanentemente

**Políticas de consolidación:**
| Origen | Destino | Trigger | Algoritmo |
|---|---|---|---|
| Working → Short-Term | Cada turno | Fin de turno | Resumen por LLM (3-5 oraciones) |
| Short-Term → Long-Term | Cierre de sesión | Sesión terminada | Síntesis por LLM (1 párrafo por tema) |
| Episodic → Long-Term | Consolidación | relevance > 0.7 | Integración en resumen existente |
| Semantic → Long-Term | Validación | Periódica | Actualización de hechos verificados |

---

### 2.7 Tool Manager (Gestor de Herramientas)

**Responsabilidad:** Gestionar el registro, descubrimiento y ejecución de herramientas.

**¿Qué es?**  
El Tool Manager mantiene el catálogo de herramientas disponibles, verifica permisos, ejecuta herramientas, y maneja errores y timeouts.

**Entradas:**
- Solicitud de ejecución de herramienta
- Parámetros de la herramienta
- Contexto del agente que solicita

**Salidas:**
```python
ToolExecutionResult:
    tool_id: str
    tool_version: str
    status: success | failed | timeout | permission_denied
    output: Any
    duration_ms: int
    error: str | None
    retry_count: int

ToolDiscoveryResult:
    query: str
    matching_tools: list[ToolInfo]
    recommended: ToolInfo | None       # la más relevante

ToolInfo:
    id: str
    name: str
    description: str
    version: str
    parameters: dict[str, ParameterDef]
    permissions_required: list[str]
    timeout_seconds: int
    category: str
    tags: list[str]
```

**Estados:**
```
 idle → discovering → results_ready → idle
       → executing → executed → idle
       → executing → timeout → retry → executing
       → executing → failed → error_logged → idle
```

**Comportamiento:**
- Registra herramientas al inicio del sistema
- Responde a descubrimiento de herramientas (el agente dice "necesito hacer X" y el Tool Manager sugiere la herramienta)
- Verifica permisos antes de ejecutar
- Ejecuta con timeout configurable
- Si falla: reintenta una vez, luego reporta error
- Registra todas las ejecuciones en eventos

---

### 2.8 Event Manager (Gestor de Eventos)

**Responsabilidad:** Gestionar el sistema de eventos completo.

**¿Qué es?**  
El Event Manager es el backbone de comunicación entre agentes. Publica eventos, suscribe agentes a eventos, y coordina el flujo de información.

**Entradas:**
- Eventos publicados por agentes
- Suscripciones de agentes a eventos
- Políticas de retención de eventos

**Salidas:**
```python
Event:
    id: UUID
    type: str                          # tipo de evento
    source: str                        # agente que lo publicó
    timestamp: datetime
    payload: dict                      # datos del evento
    metadata: dict                     # metadatos (trace_id, etc.)

EventSubscription:
    subscriber_id: str                 # agente suscrito
    event_types: list[str]             # tipos de evento que le interesan
    filter: dict                       # filtros adicionales
    callback: str                      # función a ejecutar

DeliveryResult:
    event_id: UUID
    subscriber_id: str
    delivered: bool
    processing_time_ms: int
    error: str | None
```

**Estados:**
```
 idle → event_received → routing → delivered → idle
                         → delivery_failed → retry → routing
                         → dead_letter → logged
```

**Comportamiento:**
- Recibe eventos de cualquier fuente
- Rutea eventos a los suscriptores correctos
- Garantiza delivery al menos una vez (at-least-once)
- Maneja eventos no procesados (dead letter queue)
- Registra métricas de delivery
- Soporta eventos síncronos y asíncronos

---

## 3. Diagrama de Orquestación

```
                          ┌──────────────┐
                          │    USER      │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │   PLANNER    │
                          │  (planifica) │
                          └──────┬───────┘
                                 │ plan
                          ┌──────▼───────┐
                          │   EXECUTOR   │
                          │  (ejecuta)   │
                          └──┬───┬───┬───┘
                             │   │   │
                ┌────────────┘   │   └────────────┐
                │                │                │
         ┌──────▼──────┐ ┌──────▼──────┐ ┌───────▼─────┐
         │  BOARD ROOM │ │ GATE REVIEW │ │   TOOLS     │
         │  (4 agentes)│ │ (determinist)│ │  (herramientas)│
         └─────────────┘ └─────────────┘ └─────────────┘
                │                │                │
                └────────────────┼────────────────┘
                                 │
                          ┌──────▼───────┐
                          │   CRITIC     │
                          │  (evalúa)    │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  OBSERVER    │
                          │  (monitorea) │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │   REVIEWER   │
                          │  (revisa     │
                          │   estratégico)│
                          └──────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
             ┌──────▼──────┐ ┌──▼───────┐ ┌──▼──────────┐
             │   MEMORY    │ │  EVENT   │ │ KNOWLEDGE   │
             │   MANAGER   │ │  MANAGER │ │ GRAPH       │
             └─────────────┘ └──────────┘ └─────────────┘
```

---

## 4. Flujo de Ejecución Completo

### 4.1 Ejemplo: Usuario pregunta "¿Cómo va mi empresa?"

```
1. USER: "¿Cómo va mi empresa?"

2. PLANNER:
   - Analiza la query
   - Detecta: el usuario quiere un resumen del estado
   - Plan: [Paso 1: Recuperar estado del proyecto, Paso 2: Generar resumen]
   - Agentes necesarios: Memory Manager, Executor

3. EXECUTOR - Paso 1:
   - Llama a Memory Manager: "recuperar estado del proyecto X"
   - Memory Manager consulta Semantic Memory (knowledge graph)
   - Memory Manager consulta Long-Term Memory (resúmenes)
   - Resultado: estado actual del proyecto

4. EXECUTOR - Paso 2:
   - Genera resumen con el LLM usando el contexto recuperado
   - Resultado: respuesta al usuario

5. CRITIC:
   - Evalúa la respuesta
   - Verifica que sea consistente con el knowledge graph
   - Aprueba: la respuesta es correcta y completa

6. OBSERVER:
   - Registra métricas: tiempo de ejecución, tokens usados
   - Calidad: OK

7. EVENT MANAGER:
   - Publica evento: user_query_resolved
   - Datos: query, response_quality, duration

8. MEMORY MANAGER:
   - Actualiza Short-Term Memory con esta interacción
   - Si es momento de consolidar: ejecuta consolidación

9. USER: recibe la respuesta
```

### 4.2 Ejemplo: Usuario pide "Analiza mi mercado"

```
1. USER: "Analiza mi mercado"

2. PLANNER:
   - Analiza: solicitud compleja, requiere análisis profundo
   - Plan: [
       Paso 1: Recuperar contexto de mercado (Memory Manager),
       Paso 2: Ejecutar Board Room (4 agentes analizan),
       Paso 3: Generar análisis de mercado (LLM),
       Paso 4: Evaluar calidad (Critic)
     ]
   - Agentes: Memory Manager, Board Room, Critic
   - Herramientas: LLM (chat)

3. EXECUTOR - Paso 1:
   - Memory Manager recupera: facts del mercado, episodios previos, resúmenes
   - Resultado: contexto completo de mercado

4. EXECUTOR - Paso 2:
   - Invoca Board Room con el contexto
   - 4 agentes analizan concurrentemente
   - Consenso: PROCEED con confianza 75%
   - Resultado: análisis del Board Room

5. EXECUTOR - Paso 3:
   - LLM genera análisis detallado de mercado
   - Usa contexto del Board Room + Memory Manager
   - Resultado: documento de análisis

6. CRITIC:
   - Evalúa el análisis contra el knowledge graph
   - Detecta: falta información de competidores
   - Rechaza: "información incompleta"
   - Solicita: agregar análisis competitivo

7. EXECUTOR (re-ejecuta Paso 3):
   - LLM re-genera análisis incluyendo competitivo
   - Resultado: análisis completo

8. CRITIC (re-evalúa):
   - Aprueba: la respuesta es completa y precisa

9. OBSERVER:
   - Registra: se necesitó 1 retry por issue de calidad
   - Métricas: tiempo total, tokens totales

10. EVENT MANAGER:
    - Publica: market_analysis_completed
    - Datos: quality_score, retry_count, agents_used

11. USER: recibe el análisis de mercado
```

---

## 5. Estados de los Agentes

### 5.1 Estados Globales

Todos los agentes comparten estos estados base:

```
 idle → busy → idle
       → error → idle
       → blocked → idle
```

### 5.2 Estados Específicos por Agente

| Agente | Estados Específicos |
|---|---|
| Planner | `planning`, `plan_ready`, `plan_revised`, `plan_approved` |
| Executor | `executing`, `step_running`, `step_completed`, `step_failed` |
| Observer | `monitoring`, `anomaly_detected`, `quality_issue` |
| Critic | `reviewing`, `approved`, `issues_found`, `critical_issue` |
| Reviewer | `reviewing`, `approved`, `rejected`, `deferred`, `escalated` |
| Memory Manager | `consolidating`, `compressing`, `retrieving`, `archiving` |
| Tool Manager | `discovering`, `executing`, `timeout`, `retry` |
| Event Manager | `routing`, `delivered`, `delivery_failed`, `dead_letter` |

---

## 6. Comunicación entre Agentes

### 6.1 Patron de Comunicación

Los agentes NO se comunican directamente. Toda comunicación pasa por el Event Manager:

```
Agente A → Event Manager → Agente B
```

Esto garantiza:
- Desacoplamiento entre agentes
- Trazabilidad de toda comunicación
- Posibilidad de replay
- Control de flujo

### 6.2 Tipos de Mensaje

| Tipo | Descripción | Ejemplo |
|---|---|---|
| Command | Solicitud de acción | "Ejecuta el Board Room" |
| Query | Solicitud de información | "¿Qué sabes del mercado X?" |
| Result | Respuesta a una solicitud | "Board Room completado: PROCEED" |
| Event | Notificación de cambio | "Nueva decisión registrada" |
| Alert | Notificación de problema | "Timeout en herramienta X" |

### 6.3 Protocolo de Cola de Mensajes

```
┌─────────┐     ┌──────────────┐     ┌─────────┐
│ Sender  │────▶│ Event Manager│────▶│Receiver │
│         │     │              │     │         │
│         │◀────│  - Route     │◀────│         │
│         │     │  - Filter    │     │         │
│         │     │  - Deliver   │     │         │
└─────────┘     └──────────────┘     └─────────┘
```

---

## 7. Gestión de Errores

### 7.1 Estrategia de Errores por Agente

| Agente | Error Handling |
|---|---|
| Planner | Si no puede planificar: escala al usuario con opciones |
| Executor | Si un paso falla: retry 1 vez, luego aplica fallback, luego reporta al Planner |
| Observer | Si detecta problema crítico: alerta inmediata al usuario |
| Critic | Si detecta issue crítico: bloquea entrega, solicita revisión |
| Reviewer | Si no puede decidir: escala al usuario |
| Memory Manager | Si falla la recuperación: usa Working Memory como fallback |
| Tool Manager | Si la herramienta falla: retry 1 vez, luego reporta al Executor |
| Event Manager | Si no puede entregar: dead letter queue, retry después |

### 7.2 Escalación al Usuario

El usuario es el fallback último. Se escala cuando:
- El Planner no puede generar un plan válido
- El Critic detecta un issue crítico que no puede resolver
- El Reviewer necesita una decisión estratégica que no puede tomar
- Todos los fallbacks agotados

---

## 8. Concurrencia y Paralelismo

### 8.1 Qué puede ejecutarse en paralelo

| Operación | Paralela | Condiciones |
|---|---|---|
| Board Room (4 agentes) | Sí | Siempre (ya implementado con asyncio.gather) |
| Pasos sin dependencias en el plan | Sí | Executor puede paralelizar |
| Recuperación de memoria (múltiples fuentes) | Sí | Memory Manager puede paralelizar |
| Ejecución de herramientas independientes | Sí | Tool Manager puede paralelizar |
| Evaluación del Critic + Monitoreo del Observer | Sí | Son independientes |

### 8.2 Qué debe ser secuencial

| Operación | Secuencial | Razón |
|---|---|---|
| Planner → Executor | Sí | El plan debe existir antes de ejecutar |
| Executor → Critic | Sí | La respuesta debe existir antes de evaluarla |
| Critic → Entrega al usuario | Sí | La aprobación debe existir antes de entregar |
| Consolidación de memoria | Sí | No se puede consolidar concurrentemente |

---

## 9. Métricas por Agente

| Agente | Métricas Clave |
|---|---|
| Planner | Tiempo de planificación, tasa de éxito del plan, número de revisiones |
| Executor | Tiempo de ejecución, tasa de éxito de pasos, número de retries |
| Observer | Anomalías detectadas, falsos positivos |
| Critic | Tasa de aprobación, issues por dimensión, tiempo de revisión |
| Reviewer | Decisiones revisadas, tasa de aprobación, tiempo de revisión |
| Memory Manager | Tiempo de recuperación, precisión de recuperación, espacio ahorrado |
| Tool Manager | Tiempo de ejecución, tasa de éxito, timeout rate |
| Event Manager | Latencia de delivery, tasa de entrega, dead letters |

---

**Este diseño está CONGELADO.**  
**Las implementaciones futuras deben adherirse a esta especificación.**  
**Los cambios de diseño requieren Work Order específica.**
