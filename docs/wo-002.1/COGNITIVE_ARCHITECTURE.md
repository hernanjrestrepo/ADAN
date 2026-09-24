# COGNITIVE_ARCHITECTURE — Cómo Piensa ADÁN

**WO:** WO-002.1  
**Fecha:** 2026-07-24  
**Estado:** Diseño (sin implementar)  
**Prerequisito:** WO-001 cerrada, WO-002 baseline congelado

---

## 1. Visión General

ADÁN no es un chatbot que responde preguntas. Es un sistema cognitivo que:

1. **Recuerda** lo que el usuario dijo, decidió y descartó.
2. **Comprende** el contexto de la empresa en cada momento.
3. **Planifica** qué información necesita antes de actuar.
4. **Decide** cuándo preguntar, cuándo inferir y cuándo actuar.
5. **Aprende** de cada interacción para mejorar futuras respuestas.
6. **Justifica** cada decisión con evidencia rastreable.

La arquitectura cognitiva se modela inspirada en los sistemas de memoria humana, con capas que van desde lo inmediato (working memory) hasta lo permanente (long-term memory), conectadas por procesos de consolidación, compresión y olvido controlado.

---

## 2. Los Seis Tipos de Memoria

### 2.1 Working Memory (Memoria de Trabajo)

**Qué es:** El contexto activo de una sola interacción. Lo que ADÁN "está pensando ahora".

**Contenido:**
- Mensaje actual del usuario
- Últimos N mensajes de la conversación (ventana deslizante)
- Resultados de herramientas ejecutadas recientemente
- Estado del plan actual (pasos completados, pendientes)
- Hipótesis activas (cosas que ADÁN está considerando)
- Atención activa (qué entidades del knowledge graph están en foco)

**Capacidad:** Limitada por el contexto window del LLM (32K tokens para Qwen 2.5). Se gestiona con:
- Ventana deslizante de mensajes (últimos 20 mensajes)
- Resumen de mensajes anteriores (cuando se excede la ventana)
- Priorización por relevancia (mensajes recientes > antiguos)

**Ciclo de vida:**
- **Creación:** Al inicio de cada request HTTP
- **Actualización:** En cada turno de conversación
- **Destrucción:** Al finalizar la request (se persiste lo necesario en otras memorias)

**Formato interno:**
```python
WorkingMemory:
    conversation_id: UUID
    messages: list[Message]          # ventana deslizante
    summary: str                     # resumen de mensajes fuera de ventana
    active_plan: Plan | None         # plan actual si hay uno activo
    active_hypotheses: list[str]     # hipótesis que se están evaluando
    attention_focus: list[EntityRef] # entidades del knowledge graph en foco
    tool_results: list[ToolResult]   # resultados recientes de herramientas
    turn_count: int                  # número de turno en esta conversación
```

### 2.2 Short-Term Memory (Memoria a Corto Plazo)

**Qué es:** El contexto de una sesión completa (una visita del usuario al sistema).

**Contenido:**
- Resumen de la sesión actual (generado por LLM al final de cada turno significativo)
- Decisiones tomadas en esta sesión
- Información clave descubierta
- Preguntas pendientes que el usuario hizo pero no se respondieron completamente
- Estado emocional detectado del usuario (frustrado, entusiasmado, confundido)

**Capacidad:** Ilimitada en almacenamiento (persiste en BD), pero se comprime al final de cada sesión.

**Ciclo de vida:**
- **Creación:** Al iniciar una nueva sesión (login del usuario)
- **Actualización:** En cada turno significativo
- **Consolidación:** Al cerrar la sesión → se comprime en un resumen semántico
- **Migración:** Piezas relevantes migran a Long-Term Memory

**Formato interno:**
```python
ShortTermMemory:
    session_id: UUID
    user_id: UUID
    company_id: UUID
    started_at: datetime
    turns: list[TurnSummary]         # resumen de cada turno
    decisions_made: list[Decision]   # decisiones tomadas en la sesión
    key_discoveries: list[str]       # información importante descubierta
    open_questions: list[str]        # preguntas pendientes
    sentiment: SentimentState        # estado emocional detectado
    compressed_summary: str | None   # resumen final al cerrar sesión
```

### 2.3 Long-Term Memory (Memoria a Largo Plazo)

**Qué es:** El conocimiento acumulado de todas las sesiones de una empresa. La "memoria institucional".

**Contenido:**
- Historial de todas las conversaciones (resumidas, no textos crudos)
- Decisiones aprobadas y rechazadas (con justificación)
- Evolución del proyecto a lo largo del tiempo
- Preferencias y estilo del usuario
- Errores cometidos y cómo se corrigieron
- Patrones detectados (ej: "este usuario siempre prefiere datos cuantitativos")

**Capacidad:** Creciente. Se gestiona con compresión periódica y olvido controlado.

**Ciclo de vida:**
- **Creación:** Al consolidar Short-Term Memory después de cada sesión
- **Crecimiento:** Acumulativa (se agrega, no se reemplaza)
- **Compresión:** Periódica (resúmenes se re-escriben con más contexto)
- **Archivado:** Información obsoleta se marca como archivada (nunca se borra)
- **Olvido:** Controlado (información irrelevante se de-prioriza, no se elimina)

**Formato interno:**
```python
LongTermMemory:
    company_id: UUID
    project_snapshots: list[ProjectSnapshot]  # evolución del proyecto
    decision_history: list[DecisionRecord]    # todas las decisiones
    user_preferences: UserPreferences         # preferencias del usuario
    pattern_library: list[Pattern]            # patrones detectados
    lesson_library: list[Lesson]              # lecciones aprendidas
    error_history: list[ErrorRecord]          # errores y correcciones
    version: int                              # versión del resumen consolidado
```

### 2.4 Episodic Memory (Memoria Episódica)

**Qué es:** Recuerdos de eventos específicos. "Lo que pasó el martes pasado cuando hablamos de precios".

**Contenido:**
- Conversaciones significativas (no todas, solo las relevantes)
- Momentos clave (decisiones tomadas, problemas resueltos, descubrimientos)
- Contexto emocional de esos momentos
- Resultados de esas interacciones

**Capacidad:** Se mantiene por relevancia. Los episodios más relevantes se preservan; los rutinarios se comprimen en resúmenes.

**Ciclo de vida:**
- **Creación:** Automática al detectar un momento significativo (decisión, descubrimiento, conflicto)
- **Consolidación:** Al final de la sesión, los episodios se evalúan y los relevantes migran a Long-Term
- **Olvido:** Los episodios irrelevantes se comprimen en resúmenes genéricos después de N días

**Criterios de significancia:**
- Se tomó una decisión
- Se descubrió información nueva
- El usuario expresó emoción fuerte
- Hubo desacuerdo entre agentes
- Se resolvió un problema
- Se completó un hito

**Formato interno:**
```python
EpisodicMemory:
    episode_id: UUID
    timestamp: datetime
    summary: str                        # qué pasó
    context: str                        # contexto de la conversación
    entities_involved: list[EntityRef]  # empresas, personas, proyectos
    decisions: list[Decision]           # decisiones tomadas
    outcome: str                        # resultado
    emotional_valence: float            # -1 (negativo) a +1 (positivo)
    relevance_score: float              # 0-1, se recalcula periódicamente
    access_count: int                   # cuántas veces se ha recuperado
    last_accessed: datetime
```

### 2.5 Semantic Memory (Memoria Semántica)

**Qué es:** Conhecimiento factual y relacional. "La empresa X está en el mercado Y", "El usuario Z prefiere reports cortos".

**Contenido:**
- Hechos sobre la empresa (industria, tamaño, mercado)
- Hechos sobre el proyecto (estado actual, objetivos, restricciones)
- Hechos sobre el usuario (preferencias, estilo, historial)
- Relaciones entre entidades (empresa → mercado, proyecto → objetivo)
- Definiciones y conceptos del dominio

**Capacidad:** Estructurada en el Knowledge Graph (ver KNOWLEDGE_GRAPH.md).

**Ciclo de vida:**
- **Creación:** Al extraer hechos de conversaciones o documentos
- **Actualización:** Cuando un hecho se contradice con información nueva
- **Versionado:** Cada cambio crea una nueva versión (append-only)
- **Confianza:** Cada hecho tiene un nivel de confianza que decrece con el tiempo

**Formato interno:**
```python
SemanticMemory:
    entity_id: UUID
    entity_type: str                    # company, project, person, market, etc.
    facts: list[Fact]                   # hechos conocidos
    relations: list[Relation]           # relaciones con otras entidades
    confidence: float                   # confianza general
    last_validated: datetime            # última vez que se verificó
    source: str                         # de dónde vino la información

class Fact:
    subject: str
    predicate: str
    object: str
    confidence: float
    source: str
    created_at: datetime
    superseded_by: UUID | None          # si fue reemplazado por otro hecho
```

### 2.6 Procedural Memory (Memoria Procedimental)

**Qué es:** Cómo hacer las cosas. Procedimientos, flujos, mejores prácticas.

**Contenido:**
- Flujos de trabajo conocidos (ej: "cuando el usuario pregunta sobre precios, primero revisar el mercado")
- Mejores prácticas acumuladas
- Errores a evitar (procedimientos que fallaron)
- Optimizaciones descubiertas
- Reglas de negocio específicas de la empresa

**Capacidad:** Creciente. Se enriquece con cada interacción exitosa.

**Ciclo de vida:**
- **Creación:** Al detectar un patrón exitoso en múltiples interacciones
- **Validación:** Requiere N ocurrencias para ser considerado un procedimiento
- **Actualización:** Cuando un procedimiento falla, se revisa
- **Olvido:** Procedimientos obsoletos se archivan

**Formato interno:**
```python
ProceduralMemory:
    procedure_id: UUID
    trigger: str                        # cuándo activar este procedimiento
    steps: list[str]                    # pasos del procedimiento
    success_count: int
    failure_count: int
    confidence: float                   # success / (success + failure)
    last_used: datetime
    avg_quality: float                  # calificación promedio del resultado
    source: str                         # de dónde se aprendió
```

---

## 3. Interacción entre Memorias

### 3.1 Flujo de Datos

```
                        ┌─────────────────┐
                        │  Working Memory  │ ← Request HTTP
                        │  (contexto       │
                        │   activo)        │
                        └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │  Short-   │ │ Semantic │ │ Episodic │
            │  Term     │ │ Memory   │ │ Memory   │
            │  Memory   │ │          │ │          │
            └─────┬────┘ └────┬─────┘ └────┬─────┘
                  │           │             │
                  └─────┬─────┘             │
                        │                   │
                        ▼                   │
                ┌──────────────┐            │
                │  Long-Term   │◄───────────┘
                │  Memory      │  (consolidación)
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │  Procedural  │  (aprendizaje)
                │  Memory      │
                └──────────────┘
```

### 3.2 Reglas de Interacción

| Origen | Destino | Cuándo | Qué se transfiere |
|---|---|---|---|
| Working → Short-Term | Cada turno | Turno completado | Resumen del turno, decisiones, descubrimientos |
| Short-Term → Long-Term | Cierre de sesión | Sesión terminada | Resumen comprimido, decisiones, lecciones |
| Episodic → Long-Term | Consolidación | Post-sesión | Episodios con relevance_score > 0.7 |
| Semantic → Long-Term | Validación | Periódica | Hechos verificados actualizados |
| Long-Term → Procedural | Aprendizaje | Tras N éxitos | Patrones validados por repetición |
| Long-Term → Working | Recuperación | Cada request | Contexto relevante para la query actual |
| Episodic → Working | Recuperación | Query específica | Episodios que matchean la consulta |

### 3.3 Prioridad de Recuperación

Cuando Working Memory necesita información de otras memorias, se recupera en este orden:

1. **Semantic Memory** (hechos actuales y verificados)
2. **Episodic Memory** (recuerdos relevantes de la query)
3. **Long-Term Memory** (resúmenes consolidados)
4. **Procedural Memory** (procedimientos aplicables)
5. **Short-Term Memory** (contexto de sesión actual)

---

## 4. Cuándo se Crean

| Tipo de Memoria | Trigger de Creación |
|---|---|
| Working Memory | Request HTTP entrante |
| Short-Term Memory | Login del usuario (nueva sesión) |
| Long-Term Memory | Consolidación post-sesión |
| Episodic Memory | Detección de momento significativo |
| Semantic Memory | Extracción de hechos de conversación |
| Procedural Memory | Validación de patrón exitoso (N ocurrencias) |

---

## 5. Cuándo se Eliminan

**Regla fundamental: Nada se elimina. Se archiva o se de-prioriza.**

| Tipo | Acción | Mecanismo |
|---|---|---|
| Working Memory | Se destruye al final de request | Volátil (en memoria, no persiste) |
| Short-Term Memory | Se consolida en Long-Term | Resumen comprimido |
| Long-Term Memory | Nunca se elimina | Información obsoleta se marca como archivada |
| Episodic Memory | Se de-prioriza con el tiempo | relevance_score decrece exponencialmente |
| Semantic Memory | Hechos se superseden | Nuevo hecho reemplaza al anterior (con historia) |
| Procedural Memory | Se archiva si confidence < umbral | Procedimiento marcado como obsoleto |

---

## 6. Cuándo se Versionan

| Tipo | Política de Versionado |
|---|---|
| Working Memory | No se versiona (es volátil) |
| Short-Term Memory | Se versiona al consolidar (cada resumen es una versión) |
| Long-Term Memory | Se versiona con cada consolidación significativa |
| Episodic Memory | No se versiona (es inmutable una vez creado) |
| Semantic Memory | Cada hecho tiene superseded_by (historial completo) |
| Procedural Memory | Se versiona cuando se modifica por fallo |

---

## 7. Gestión de la Atención

### 7.1 ¿Qué es la Atención?

La atención es el mecanismo que determina qué información de las memorias se carga en Working Memory. No todo el conocimiento disponible se carga en cada request — solo lo relevante.

### 7.2 Señales de Atención

| Señal | Peso | Descripción |
|---|---|---|
| Recencia | 0.3 | Información más reciente tiene mayor peso |
| Relevancia temática | 0.3 | Match con el topic actual de la conversación |
| Frecuencia de acceso | 0.2 | Información consultada frecuentemente es más relevante |
| Confianza | 0.1 | Hechos con mayor confianza tienen prioridad |
| Novedad | 0.1 | Información nueva no vista previamente |

### 7.3 Presupuesto de Atención

Cada request tiene un "presupuesto de atención" — un límite de tokens que se puede gastar en contexto de memoria:

| Componente | Tokens Máximos | Prioridad |
|---|---|---|
| Mensajes de Working Memory | 8,000 | Alta |
| Resumen de sesión (Short-Term) | 2,000 | Alta |
| Hechos relevantes (Semantic) | 3,000 | Media |
| Episodios relevantes | 2,000 | Media |
| Procedimientos aplicables | 1,000 | Baja |
| Resumen consolidado (Long-Term) | 2,000 | Baja |
| **Total** | **18,000** | — |

El presupuesto restante (14,000 tokens para Qwen 2.5:0.5b con 32K context) se reserva para el system prompt del agente y la respuesta.

---

## 8. Consolidación

### 8.1 ¿Qué es la Consolidación?

La consolidación es el proceso de transformar memorias volátiles en memorias persistentes, y de comprimir información detallada en resúmenes concisos.

### 8.2 Tipos de Consolidación

| Tipo | Origen | Destino | Trigger |
|---|---|---|---|
| Turno → Sesión | Working Memory | Short-Term | Fin de turno significativo |
| Sesión → Largo Plazo | Short-Term | Long-Term | Cierre de sesión |
| Episodio → Largo Plazo | Episodic | Long-Term | relevance_score > 0.7 |
| Hecho → Grafo | Conversación | Semantic | Extracción de hecho |
| Patrón → Procedural | Long-Term | Procedural | N ocurrencias del patrón |

### 8.3 Compresión

La compresión reduce el tamaño de la información sin perder significado:

**Nivel 1 — Truncamiento:**
- Mensajes largos se truncan a 200 chars (ya implementado en MemoryService)
- Listas se reducen a los 5 elementos más relevantes

**Nivel 2 — Resumen por LLM:**
- Sesiones completas se resumen en 3-5 oraciones
- Episodios se comprimen en un párrafo

**Nivel 3 — Síntesis Semántica:**
- Múltiples resúmenes se combinan en uno coherente
- Hechos contradictorios se reconcilian
- Patrones se abstraen en reglas

### 8.4 Frecuencia de Consolidación

| Proceso | Frecuencia |
|---|---|
| Turno → Sesión | Cada turno (inmediato) |
| Sesión → Largo Plazo | Al cerrar sesión |
| Compresión de Long-Term | Diaria (job background) |
| Re-evaluación de Episodios | Semanal |
| Reconciliación de Semantic | Mensual |

---

## 9. Olvido Controlado

### 9.1 ¿Qué se Olvida?

**Nada se borra permanentemente.** El olvido es un mecanismo de de-priorización:

| Tipo de Información | Política de Olvido |
|---|---|
| Mensajes de chat crudos | Se comprimen en resúmenes después de 7 días |
| Episodios irrelevantes | relevance_score decrece 10% por semana sin acceso |
| Hechos superseded | Se mantienen con superseded_by (historial) |
| Procedimientos obsoletos | Se archivan si confidence < 0.3 después de 30 días |
| Resúmenes antiguos | Se reescriben cuando acumulan más de 5000 chars |

### 9.2 Cálculo de Relevancia para Olvido

```
relevance_score(t) = relevance_score(t-1) × decay_factor × access_frequency_factor

decay_factor = e^(-λ × days_since_last_access)
access_frequency_factor = 1 + log(access_count + 1)
```

Donde:
- `λ = 0.01` (constante de decaimiento — ~70 días para reducir a la mitad)
- `access_count` amortigua el decaimiento (cosas consultadas frecuentemente se olvidan más lento)

### 9.3 Umbral de Archivado

Cuando `relevance_score < 0.1`, la entrada se marca como `archived`:
- No se carga en Working Memory
- No se incluye en búsquedas rutinarias
- Sigue siendo consultable por ID directo
- Puede ser re-activada si se referencia explícitamente

---

## 10. Recuperación

### 10.1 Tipos de Recuperación

| Tipo | Mecanismo | Cuándo |
|---|---|---|
| Recuperación por recencia | Ordenar por timestamp | Cuando el usuario dice "lo que hablamos antes" |
| Recuperación por relevancia | BM25 + semantic similarity | Cuando el usuario pregunta sobre un tema |
| Recuperación por entidad | Lookup en Knowledge Graph | Cuando se menciona una empresa/proyecto/persona |
| Recuperación por episodio | Match por contexto emocional | Cuando el usuario recuerda un momento específico |
| Recuperación por procedimiento | Match por trigger | Cuando ADÁN necesita saber "cómo hacer X" |

### 10.2 Pipeline de Recuperación

```
Query del usuario
       │
       ▼
┌─────────────┐
│  Extract     │  → Entidades, temas, intención
│  Query       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Semantic    │  → Hechos relevantes del Knowledge Graph
│  Lookup      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Episodic    │  → Recuerdos que matchean el contexto
│  Search      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Long-Term   │  → Resúmenes consolidados relevantes
│  Search      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Rank by     │  → Fusionar resultados, eliminar duplicados
│  Attention   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Budget      │  → Seleccionar top-N dentro del presupuesto
│  Filter      │
└─────────────┘
```

---

## 11. Diagrama de Arquitectura Cognitiva

```
┌─────────────────────────────────────────────────────────────┐
│                     WORKING MEMORY                           │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │Messages │ │Active    │ │Attention │ │Tool Results    │  │
│  │(window) │ │Plan      │ │Focus     │ │(recent)        │  │
│  └─────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  SHORT-TERM      │ │  SEMANTIC    │ │  EPISODIC        │
│  MEMORY          │ │  MEMORY      │ │  MEMORY          │
│  ┌────────────┐  │ │  ┌────────┐  │ │  ┌────────────┐  │
│  │Session     │  │ │  │Facts   │  │ │  │Episodes    │  │
│  │Summary     │  │ │  │Graph   │  │ │  │(ranked by  │  │
│  │Decisions   │  │ │  │Relations│  │ │  │relevance)  │  │
│  │Discoveries │  │ │  └────────┘  │ │  └────────────┘  │
│  └────────────┘  │ │              │ │                    │
└────────┬─────────┘ └──────┬───────┘ └────────┬───────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                    ┌───────▼───────┐
                    │  LONG-TERM    │
                    │  MEMORY       │
                    │  ┌──────────┐ │
                    │  │Consolidated│ │
                    │  │Summaries  │ │
                    │  │Decision   │ │
                    │  │History    │ │
                    │  │Patterns   │ │
                    │  │Lessons    │ │
                    │  └──────────┘ │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │  PROCEDURAL   │
                    │  MEMORY       │
                    │  ┌──────────┐ │
                    │  │Workflows │ │
                    │  │Best      │ │
                    │  │Practices │ │
                    │  │Rules     │ │
                    │  └──────────┘ │
                    └───────────────┘
```

---

## 12. Relación con el Sistema Actual

### 12.1 Lo que Ya Existe

| Capa Actual | Equivalente Cognitivo | Estado |
|---|---|---|
| `MemoryService` (conversation summary) | Short-Term Memory (básico) | Implementado, simplificado |
| `GemeloDigitalService` (event sourcing) | Semantic Memory (parcial) | Implementado |
| `messages.metadata_json` | Working Memory (metadatos) | Implementado |
| Tabla `events` | Episodic Memory (parcial) | Implementado |
| Tabla `decisions` | Long-Term Memory (parcial) | Implementado |

### 12.2 Lo que Falta Implementar

| Capa Cognitiva | Estado | Prioridad |
|---|---|---|
| Working Memory (gestión de contexto) | No implementada | Alta |
| Short-Term Memory (consolidación de sesión) | Básica (concatenación) | Alta |
| Long-Term Memory (consolidación) | No implementada | Alta |
| Episodic Memory (detección de momentos) | No implementada | Media |
| Semantic Memory (knowledge graph) | No implementada | Alta |
| Procedural Memory (aprendizaje) | No implementada | Baja |
| Gestión de Atención | No implementada | Alta |
| Pipeline de Recuperación | No implementada | Alta |
| Consolidación Automática | No implementada | Media |
| Olvido Controlado | No implementada | Baja |

---

## 13. Decisiones de Diseño

### 13.1 ¿Por qué 6 tipos de memoria?

Porque cada tipo resuelve un problema diferente:
- **Working:** "¿Qué estoy pensando ahora?"
- **Short-Term:** "¿Qué pasó en esta sesión?"
- **Long-Term:** "¿Qué sé sobre esta empresa?"
- **Episodic:** "¿Cuándo pasó algo similar antes?"
- **Semantic:** "¿Qué hechos conozco?"
- **Procedural:** "¿Cómo se hace esto?"

### 13.2 ¿Por qué no se borra nada?

Porque en un contexto empresarial, la información "obsoleta" puede ser relevante más tarde. Un mercado que parecía muerto puede revivir. Una decisión rechazada puede ser correcta en otro contexto. El costo de almacenar es bajo; el costo de perder información es alto.

### 13.3 ¿Por qué la consolidación es por LLM?

Porque la compresión inteligente requiere comprensión. Un resumen generado por LLM preserva el significado mientras reduce el tamaño. Un resumen por truncamiento pierde contexto.

### 13.4 ¿Por qué hay presupuesto de atención?

Porque el contexto window es limitado (32K tokens). No se puede cargar toda la memoria en cada request. La atención selecciona lo más relevante dentro de un presupuesto fijo.

---

**Este diseño está CONGELADO.**  
**Las implementaciones futuras deben adherirse a esta especificación.**  
**Los cambios de diseño requieren Work Order específica.**
