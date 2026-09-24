# MEMORY_LIFECYCLE — Ciclo de Vida de la Memoria en ADÁN

**WO:** WO-002.1  
**Fecha:** 2026-07-24  
**Estado:** Diseño (sin implementar)  
**Prerequisito:** WO-001 cerrada, WO-002 baseline congelado

---

## 1. Visión General

La memoria de ADÁN no es estática — vive, crece, se comprime, se archiva y eventualmente se de-prioriza. Este documento define el ciclo de vida completo de cada tipo de memoria.

**Principio:** La información nunca se destruye. Se transforma, se comprime, se archiva, pero siempre es recuperable.

---

## 2. Ciclo de Vida por Tipo de Memoria

### 2.1 Working Memory (Memoria de Trabajo)

```
Creación → Uso → Actualización → Persistencia → Destrucción
   │         │         │              │              │
   │         │         │              │              │
Request   Turnos    Cada turno    Al final de    Volátil
HTTP      activos   de convers.   la request     (no persiste)
entrante
```

**Fases detalladas:**

| Fase | Trigger | Acción | Datos |
|---|---|---|---|
| Creación | Request HTTP entrante | Inicializar con ventana de mensajes + contexto | Conversación actual, últimos 20 mensajes, resumen |
| Uso | Cada turno | Agregar mensaje del usuario + respuesta del asistente | Mensajes nuevos, resultados de herramientas |
| Actualización | Fin de turno | Agregar resultados de agentes, actualizar atención | Nuevos datos de Board Room, diagnóstico, etc. |
| Persistencia | Fin de request | Extraer datos significativos para otras memorias | Resumen del turno → Short-Term Memory |
| Destrucción | GC del sistema | Eliminar de memoria | Ningún dato se pierde (ya persistió) |

**Política de ventana deslizante:**
- Mantener últimos 20 mensajes en Working Memory
- Cuando se exceden 20: comprimir mensajes 1-15 en un resumen
- El resumen se agrega al inicio de la ventana
- Resultado: resumen + últimos 5 mensajes = contexto completo

**Ejemplo de compresión:**
```
ANTES (25 mensajes):
[Resumen sesión] [M1] [M2] [M3] ... [M25]

DESPUÉS (compresión):
[Resumen sesión + Resumen M1-M15] [M16] [M17] ... [M25]
```

### 2.2 Short-Term Memory (Memoria a Corto Plazo)

```
Creación → Actualización → Consolidación → Migración → Destrucción
   │            │              │              │             │
   │            │              │              │             │
Login del    Cada turno     Fin de sesión  Piezas        Resumen
usuario      significativo                  relevantes    comprimido
(nueva       (resumen                        van a        se almacena
sesión)      del turno)                      Long-Term    en Long-Term
```

**Fases detalladas:**

| Fase | Trigger | Acción | Datos |
|---|---|---|---|
| Creación | Login del usuario | Inicializar空 Short-Term Memory | session_id, user_id, company_id |
| Actualización | Cada turno significativo | Agregar resumen del turno | TurnSummary con decisiones, descubrimientos |
| Consolidación | Fin de sesión | Comprimir toda la sesión en un resumen | Resumen semántico generado por LLM |
| Migración | Post-consolidación | Extraer piezas relevantes para Long-Term | Decisiones, lecciones, patrones |
| Destrucción | Post-migración | Eliminar datos crudos, conservar resumen | Resumen comprimido persiste en BD |

**Criterio de "turno significativo":**
Un turno es significativo si:
- Se tomó una decisión
- Se descubrió información nueva
- El usuario expresó una preferencia
- Hubo un cambio de topic
- Se completó un paso del plan

**Formato del resumen de sesión:**
```
Sesión del 2026-07-24 con [Usuario] sobre [Empresa].

Temas principales:
1. [Tema 1]: [resumen en 1-2 oraciones]
2. [Tema 2]: [resumen en 1-2 oraciones]

Decisiones tomadas:
- [Decisión 1] → [resultado]
- [Decisión 2] → [resultado]

Descubrimientos clave:
- [Descubrimiento 1]
- [Descubrimiento 2]

Preguntas pendientes:
- [Pregunta 1]
```

### 2.3 Long-Term Memory (Memoria a Largo Plazo)

```
Creación → Crecimiento → Compresión → Archivado → Olvido Controlado
   │           │             │            │              │
   │           │             │            │              │
Consoli-    Acumula       Re-escribe   Información    relevance_score
dación de   información   resúmenes    obsoleta se    < 0.1 → archivado
sesión      de sesiones   con más      marca como
            previas       contexto     archived
```

**Fases detalladas:**

| Fase | Trigger | Acción | Datos |
|---|---|---|---|
| Creación | Primera consolidación de sesión | Crear resumen inicial | Resumen de primera sesión |
| Crecimiento | Cada consolidación | Agregar nuevo resumen | Resúmenes de sesiones posteriores |
| Compresión | Diaria (job background) | Re-escribir resúmenes acumulados | Resúmenes antiguos se combinan |
| Archivado | relevance_score < 0.1 | Marcar como archived | No se carga en consultas rutinarias |
| Olvido Controlado | Mensual | Re-evaluar archived, posiblemente re-activar | Información que vuelve a ser relevante |

**Formato del resumen consolidado:**
```python
ConsolidatedSummary:
    company_id: UUID
    version: int
    overview: str                      # resumen general de la empresa
    decision_history: list[DecisionSummary]  # todas las decisiones (resumidas)
    key_learnings: list[str]           # lecciones aprendidas
    user_preferences: dict             # preferencias del usuario
    market_knowledge: dict             # conocimiento del mercado
    risk_register: list[RiskSummary]   # riesgos identificados
    last_consolidated: datetime
    total_sessions: int
    total_messages: int
```

### 2.4 Episodic Memory (Memoria Episódica)

```
Detección → Creación → Consolidación → Re-evaluación → Olvido
   │            │            │               │             │
   │            │            │               │             │
Momento      Se guarda    Fin de sesión   Relevance     relevance
significativo  el episodio  se integra     score se      score < 0.1
detectado    (si cumple   a Long-Term     recalcula     → archivado
             criterios)   Memory          periódicamente
```

**Criterios de detección de momento significativo:**

| Criterio | Peso | Ejemplo |
|---|---|---|
| Se tomó una decisión | 0.35 | "Decidimos entrar al mercado X" |
| Se descubrió información nueva | 0.25 | "Resulta que el mercado vale $50M" |
| Hubo desacuerdo entre agentes | 0.15 | CEO dice PROCEED, CTO dice STOP |
| Emoción fuerte del usuario | 0.15 | "¡Exacto! Eso es lo que necesitaba oír" |
| Se completó un hito | 0.10 | "Nivel 1 aprobado con 84/100" |

**Puntuación de significancia:**
```
significance_score = Σ(criterio × peso × intensidad)

intensidad: 0.0 - 1.0 (qué tan fuerte fue el momento)

Si significance_score > 0.5 → crear episodio
Si significance_score > 0.8 → crear episodio de alta prioridad
```

**Cálculo de relevance_score (decae con el tiempo):**
```python
def calculate_relevance(episode: EpisodicMemory, now: datetime) -> float:
    days_since = (now - episode.last_accessed).days
    decay = math.exp(-0.01 * days_since)  # ~70 días para reducir a la mitad
    access_boost = math.log(episode.access_count + 1)
    
    return episode.initial_relevance * decay * (1 + access_boost)
```

### 2.5 Semantic Memory (Memoria Semántica)

```
Extracción → Validación → Inserción → Actualización → Supersede
   │             │            │            │              │
   │             │            │            │              │
Hecho         Se verifica  Se agrega    Se modifica    Hecho nuevo
detectado     si es nuevo  al grafo     si cambió     reemplaza al
              o contradice             (nueva         anterior
              existente                versión)       (historial
                                                      preservado)
```

**Fases detalladas:**

| Fase | Trigger | Acción | Datos |
|---|---|---|---|
| Extracción | Mensaje del usuario o agente | NER + Relation Extraction | Hecho crudo con confianza |
| Validación | Hecho extraído | Verificar contra grafo existente | ¿Es nuevo? ¿Contradice? ¿Duplicado? |
| Inserción | Hecho validado como nuevo | Agregar nodo o arista al grafo | Entidad con propiedades y confianza |
| Actualización | Hecho que modifica existente | Crear nueva versión | Nueva versión con cambio |
| Supersede | Hecho que contradice existente | Marcar anterior como superseded | superseded_by apunta a nuevo |

**Reglas de validación:**
| Escenario | Acción |
|---|---|
| Hecho nuevo, no contradice nada | Insertar directamente |
| Hecho contradice existente | Crear nueva versión, anterior → superseded |
| Hecho es duplicado exacto | Incrementar confianza del existente |
| Hecho es más específico que existente | Crear nueva versión con más detalle |
| Hecho es menos específico que existente | Ignorar (el existente es mejor) |

### 2.6 Procedural Memory (Memoria Procedimental)

```
Detección → Validación → Inserción → Uso → Actualización → Archivado
   │            │            │         │         │              │
   │            │            │         │         │              │
Patrón       Requiere N   Se agrega  Se usa    Se actualiza   confidence
exitoso      ocurrencias  como       en nueva  success/       < 0.3 →
detectado    (N=3)        procedim.  situación failure        archivado
```

**Detección de patrones:**
```python
def detect_pattern(interactions: list[Interaction]) -> Pattern | None:
    # Buscar secuencias de acciones que se repiten
    # con resultados similares
    for sequence in find_repeated_sequences(interactions, min_count=3):
        if all(r.outcome == "success" for r in sequence.results):
            return Pattern(
                trigger=sequence[0].context,
                steps=[i.action for i in sequence],
                success_rate=1.0,
                confidence=len(sequence) / 10  # más ocurrencias = más confianza
            )
    return None
```

**Ciclo de vida de confianza:**
```
confidence = success_count / (success_count + failure_count)

Si confidence > 0.8 → "procedimiento confiable"
Si confidence 0.5-0.8 → "procedimiento experimental"
Si confidence < 0.5 → "procedimiento cuestionable"
Si confidence < 0.3 por 30+ días → "procedimiento obsoleto" → archivado
```

---

## 3. Consolidación

### 3.1 ¿Cuándo se Consolida?

| Evento | Tipo de Consolidación |
|---|---|
| Fin de turno | Working → Short-Term |
| Fin de sesión | Short-Term → Long-Term |
| Detección de momento significativo | Conversación → Episodic |
| Extracción de hecho | Conversación → Semantic |
| N ocurrencias de patrón | Long-Term → Procedural |

### 3.2 ¿Cómo se Consolida?

**Consolidación Working → Short-Term:**
```python
def consolidate_working_to_shortterm(working: WorkingMemory, shortterm: ShortTermMemory):
    # 1. Generar resumen del turno por LLM
    summary = llm.generate(
        prompt=f"Resume este turno en 2-3 oraciones: {working.messages}",
        system="Eres un asistente que genera resúmenes concisos."
    )
    
    # 2. Extraer decisiones
    decisions = extract_decisions(working.messages)
    
    # 3. Extraer descubrimientos
    discoveries = extract_discoveries(working.messages)
    
    # 4. Agregar a Short-Term Memory
    shortterm.turns.append(TurnSummary(
        summary=summary,
        decisions=decisions,
        discoveries=discoveries,
        timestamp=datetime.now()
    ))
```

**Consolidación Short-Term → Long-Term:**
```python
def consolidate_shortterm_to_longterm(shortterm: ShortTermMemory, longterm: LongTermMemory):
    # 1. Generar resumen de sesión por LLM
    session_summary = llm.generate(
        prompt=f"Resume esta sesión completa en 1 párrafo: {shortterm.turns}",
        system="Eres un asistente que genera resúmenes de sesión empresarial."
    )
    
    # 2. Extraer lecciones aprendidas
    lessons = extract_lessons(shortterm)
    
    # 3. Extraer preferencias del usuario
    preferences = extract_preferences(shortterm)
    
    # 4. Agregar a Long-Term Memory
    longterm.project_snapshots.append(ProjectSnapshot(
        summary=session_summary,
        lessons=lessons,
        preferences=preferences,
        timestamp=datetime.now()
    ))
    
    # 5. Comprimir resúmenes antiguos si es necesario
    if len(longterm.project_snapshots) > 50:
        compress_old_summaries(longterm)
```

### 3.3 Compresión de Resúmenes

Cuando los resúmenes acumulados son demasiado grandes, se reescriben:

```python
def compress_summaries(summaries: list[ProjectSnapshot]) -> str:
    # Tomar los 10 resúmenes más recientes
    recent = summaries[-10:]
    
    # Generar un resumen unificado por LLM
    compressed = llm.generate(
        prompt=f"Combina estos resúmenes en uno coherente: {[s.summary for s in recent]}",
        system="Eres un asistente que genera resúmenes ejecutivos."
    )
    
    return compressed
```

---

## 4. Compresión

### 4.1 Niveles de Compresión

| Nivel | Algoritmo | Pérdida | Cuándo |
|---|---|---|---|
| 0 | Ninguna (datos crudos) | 0% | Working Memory |
| 1 | Truncamiento | ~30% | Mensajes > 200 chars |
| 2 | Resumen por LLM | ~60% | Fin de turno → Short-Term |
| 3 | Síntesis semántica | ~80% | Fin de sesión → Long-Term |
| 4 | Fusión de resúmenes | ~90% | Compresión periódica de Long-Term |

### 4.2 Política de Compresión

```python
COMPRESSION_POLICIES = {
    "working_to_shortterm": {
        "level": 2,
        "target_size": "10% del input original",
        "quality_threshold": 0.7  # mantener 70% del significado
    },
    "shortterm_to_longterm": {
        "level": 3,
        "target_size": "5% del input original",
        "quality_threshold": 0.8
    },
    "longterm_periodic": {
        "level": 4,
        "target_size": "20% del total acumulado",
        "quality_threshold": 0.9
    }
}
```

### 4.3 Medición de Calidad de Compresión

```python
def measure_compression_quality(original: str, compressed: str) -> float:
    # 1. Similitud semántica (embeddings)
    similarity = cosine_similarity(
        embed(original),
        embed(compressed)
    )
    
    # 2. Cobertura de entidades
    original_entities = extract_entities(original)
    compressed_entities = extract_entities(compressed)
    coverage = len(compressed_entities) / max(len(original_entities), 1)
    
    # 3. Cobertura de hechos
    original_facts = extract_facts(original)
    compressed_facts = extract_facts(compressed)
    fact_coverage = len(compressed_facts) / max(len(original_facts), 1)
    
    # Score ponderado
    return 0.4 * similarity + 0.3 * coverage + 0.3 * fact_coverage
```

---

## 5. Archivado

### 5.1 ¿Qué se Archiva?

| Tipo | Condición de Archivado |
|---|---|
| Working Memory | Nunca se archiva (es volátil) |
| Short-Term Memory | Se archiva al consolidar en Long-Term |
| Long-Term Memory | Nunca se archiva (se comprime) |
| Episodic Memory | relevance_score < 0.1 |
| Semantic Memory | Hechos con superseded_by activo |
| Procedural Memory | confidence < 0.3 por 30+ días |

### 5.2 ¿Cómo se Archiva?

```python
def archive_memory(memory_type: str, entry_id: UUID):
    # 1. Marcar como archived
    entry = get_entry(memory_type, entry_id)
    entry.status = "archived"
    entry.archived_at = datetime.now()
    
    # 2. Registrar evento
    event_manager.publish(Event(
        type="memory_archived",
        payload={
            "memory_type": memory_type,
            "entry_id": str(entry_id),
            "reason": "low_relevance"  # o "superseded", "obsolete", etc.
        }
    ))
    
    # 3. No eliminar — solo marcar
    # El registro sigue accesible por ID directo
```

### 5.3 Recuperación de Archivos

Los archivos marcados como archived NO se cargan en consultas rutinarias, pero son accesibles:
- Por ID directo
- Por búsqueda explícita del usuario ("¿qué pasó con X?")
- Por el sistema de eventos (para auditoría)

---

## 6. Olvido Controlado

### 6.1 Principio

**Nada se destruye.** El olvido es un mecanismo de de-priorización que evita que información obsoleta consuma recursos de atención.

### 6.2 Algoritmo de Olvido

```python
def calculate_forgetting_score(entry: MemoryEntry, now: datetime) -> float:
    days_since_access = (now - entry.last_accessed).days
    days_since_creation = (now - entry.created_at).days
    
    # Factor de decaimiento temporal
    temporal_decay = math.exp(-0.01 * days_since_access)
    
    # Factor de frecuencia de acceso
    access_frequency = math.log(entry.access_count + 1)
    
    # Factor de importancia
    importance = entry.importance_score
    
    # Factor de recencia de creación (cosas nuevas se olvidan más lento)
    recency_boost = 1.0 / (1.0 + days_since_creation / 30)
    
    forgetting_score = (
        0.3 * temporal_decay +
        0.2 * access_frequency +
        0.3 * importance +
        0.2 * recency_boost
    )
    
    return forgetting_score
```

### 6.3 Acciones por Nivel de Olvido

| Nivel | Score | Acción |
|---|---|---|
| Activo | > 0.5 | Carga completa en consultas |
| De-priorizado | 0.3 - 0.5 | Carga solo si es relevante para la query |
| Baja prioridad | 0.1 - 0.3 | Carga solo con búsqueda explícita |
| Archivado | < 0.1 | Solo accesible por ID directo |
| En cola de eliminación | < 0.05 por 90+ días | Se mueve a cola de eliminación (no se borra aún) |

### 6.4 Cola de Eliminación

Los entries en cola de eliminación no se borran inmediatamente. Se mantienen 30 días adicionales como "última oportunidad" de ser referenciados. Si nadie los referencia en 30 días, se marca como `pending_deletion`. El `pending_deletion` se mantiene 90 días más antes de ser eliminado físicamente.

**Total de retención mínima:** ~120 días desde que se marcó para eliminación.

---

## 7. Recuperación

### 7.1 Pipeline de Recuperación

```
Query del usuario
       │
       ▼
┌─────────────────────┐
│ 1. EXTRAER ENTIDADES │  → ¿De qué habla la query?
│    Y TEMAS           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. BUSCAR EN         │  → ¿Qué hay en el grafo?
│    KNOWLEDGE GRAPH   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. BUSCAR EN         │  → ¿Hay episodios relevantes?
│    EPISODIC MEMORY   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. BUSCAR EN         │  → ¿Hay resúmenes relevantes?
│    LONG-TERM MEMORY  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. BUSCAR EN         │  → ¿Hay procedimientos aplicables?
│    PROCEDURAL MEMORY │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. RANKING POR       │  → ¿Qué es más relevante?
│    ATENCIÓN          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 7. FILTRO POR        │  → ¿Cabe en el presupuesto?
│    PRESUPUESTO       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 8. CARGAR EN         │  → ¿Listo para usar?
│    WORKING MEMORY    │
└─────────────────────┘
```

### 7.2 Scoring de Relevancia

```python
def score_relevance(query: str, entry: MemoryEntry, context: ConversationContext) -> float:
    # 1. Similitud semántica con la query
    query_embedding = embed(query)
    entry_embedding = embed(entry.summary)
    semantic_score = cosine_similarity(query_embedding, entry_embedding)
    
    # 2. Match de entidades
    query_entities = extract_entities(query)
    entry_entities = extract_entities(entry)
    entity_match = len(query_entities & entry_entities) / max(len(query_entities), 1)
    
    # 3. Recencia
    recency = 1.0 / (1.0 + (datetime.now() - entry.created_at).days / 7)
    
    # 4. Frecuencia de acceso
    frequency = math.log(entry.access_count + 1)
    
    # 5. Confianza
    confidence = entry.confidence
    
    # Score ponderado
    score = (
        0.35 * semantic_score +
        0.25 * entity_match +
        0.15 * recency +
        0.10 * frequency +
        0.15 * confidence
    )
    
    return score
```

### 7.3 Presupuesto de Recuperación

| Capa | Tokens Máximos | Prioridad |
|---|---|---|
| Mensajes de Working Memory | 8,000 | Alta |
| Resumen de sesión (Short-Term) | 2,000 | Alta |
| Hechos relevantes (Semantic) | 3,000 | Media |
| Episodios relevantes | 2,000 | Media |
| Procedimientos aplicables | 1,000 | Baja |
| Resumen consolidado (Long-Term) | 2,000 | Baja |
| **Total** | **18,000** | — |

---

## 8. Consolidación en Background

### 8.1 Jobs de Consolidación

| Job | Frecuencia | Descripción |
|---|---|---|
| `consolidate_turn` | Cada turno (inmediato) | Working → Short-Term |
| `consolidate_session` | Fin de sesión | Short-Term → Long-Term |
| `compress_longterm` | Diaria (03:00 UTC) | Re-escribir resúmenes antiguos |
| `re_evaluate_episodes` | Semanal (domingos 04:00 UTC) | Recalcular relevance_score |
| `archive_obsolete` | Mensual (1er domingo 05:00 UTC) | Archivar entries obsoletos |
| `reconcile_semantic` | Mensual (1er domingo 06:00 UTC) | Reconciliar hechos contradictorios |

### 8.2 Ejecución

Los jobs de consolidación se ejecutan como tareas background del sistema de eventos:

```python
# Registro de jobs
event_manager.schedule_recurring(
    job_id="compress_longterm",
    cron="0 3 * * *",
    handler=compress_longterm_handler
)
```

---

## 9. Métricas del Ciclo de Vida

| Métrica | Descripción | Target |
|---|---|---|
| Tamaño de Working Memory | Tokens en contexto activo | < 18,000 |
| Tasa de consolidación | % de sesiones que se consolidan | > 95% |
| Calidad de compresión | Score de preservación de significado | > 0.8 |
| Tasa de recuperación | % de queries que encuentran información relevante | > 80% |
| Latencia de recuperación | Tiempo promedio para recuperar información | < 200ms |
| Tamaño de Long-Term Memory | Resúmenes totales (tokens) | < 50,000 |
| Tasa de archivado | % de entries archivados vs totales | < 20% |

---

**Este diseño está CONGELADO.**  
**Las implementaciones futuras deben adherirse a esta especificación.**  
**Los cambios de diseño requieren Work Order específica.**
