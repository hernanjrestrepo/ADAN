# ADÁN — Arquitectura Maestra v1.0

**Fecha:** 2026-07-24  
**WO de Origen:** WO-002.3  
**Estado:** CONSTITUCIÓN TÉCNICA — Documento Oficial  
**Reemplaza:** Todos los documentos de arquitectura previos (BASELINE_NIVEL1, COGNITIVE_ARCHITECTURE, AGENT_ORCHESTRATION, KNOWLEDGE_GRAPH, MEMORY_LIFECYCLE, TOOL_ARCHITECTURE, DECISION_ENGINE, EVENT_BUS)

---

## Reglas de Este Documento

1. **Este es el Single Source of Truth.** Toda decisión futura debe alinearse con este documento.
2. **Ninguna Work Order posterior puede contradecirlo** sin una revisión formal de arquitectura.
3. **Las secciones marcadas como CONGELADAS** no pueden modificarse sin Work Order específica.
4. **Las secciones marcadas como DISEÑO** son especificaciones para implementación futura.
5. **Si hay conflicto con documentos anteriores,** este documento tiene prioridad.

---

# PARTE I: FILOSOFÍA

---

## 1. Filosofía de ADÁN

### 1.1 Propósito

ADÁN es un Sistema Operativo Empresarial con inteligencia artificial. Acompaña a una empresa desde una idea no validada hasta una organización madura, documentando cada decisión con evidencia, nunca con suposiciones.

**No es un chatbot.** No es un generador de MVPs. Es un "comité de ejecutivos permanentemente disponible" que nunca pierde contexto.

### 1.2 Principios

| # | Principio | Descripción |
|---|---|---|
| 1 | **Evidencia sobre suposición** | Cada afirmación debe respaldarse con datos verificables |
| 2 | **Memoria perpetua** | Nada se olvida. La información se archiva, nunca se destruye |
| 3 | **Trazabilidad total** | Toda decisión tiene un origen, una justificación y una consecuencia rastreable |
| 4 | **Transparencia radical** | El usuario puede inspeccionar cualquier razonamiento del sistema |
| 5 | **Determinismo en evaluación** | Las evaluaciones de calidad no dependen de LLMs (reproducibles) |
| 6 | **Consenso documentado** | Las decisiones importantes requieren múltiples perspectivas |
| 7 | **Degradación graciosa** | Si un componente falla, el sistema continúa con funcionalidad reducida |
| 8 | **Privacidad por diseño** | Los datos del usuario nunca se comparten con terceros sin consentimiento |

### 1.3 Restricciones

| Restricción | Descripción |
|---|---|
| **Sin GPU obligatoria** | El sistema debe funcionar en CPU (aunque sea más lento) |
| **Sin dependencias externas críticas** | Ollama es la única dependencia externa; sin conexión a internet |
| **Sin datos sintéticos** | Toda información proviene del usuario o de herramientas verificadas |
| **Sin alucinaciones toleradas** | Las respuestas no verificadas se marcan como "no verificadas" |
| **Sin modificación del Nivel 1** | Una vez congelado, el Nivel 1 no se modifica sin Work Order |

### 1.4 Objetivos

| Objetivo | Métrica | Target |
|---|---|---|
| **Usabilidad** | Tiempo para completar Nivel 1 | < 45 segundos |
| **Confiabilidad** | Tasa de éxito de operaciones | > 99% |
| **Calidad** | Score de Gate Review promedio | > 80/100 |
| **Memoria** | Retención de contexto entre sesiones | 100% |
| **Escalabilidad** | Empresas soportadas simultáneamente | > 100 |

### 1.5 Capacidades

| Capacidad | Estado |
|---|---|
| Registro y autenticación de usuarios | Implementado (WO-001) |
| Gestión de empresas y proyectos | Implementado (WO-001) |
| Chat con IA | Implementado (WO-001) |
| Board Room multi-agente (4 agentes) | Implementado (WO-001) |
| Generación de diagnósticos | Implementado (WO-001) |
| Gate Review determinístico | Implementado (WO-001) |
| Gemelo Digital con persistencia | Implementado (WO-001) |
| Memoria entre sesiones | Diseñada (WO-002.1) — Pendiente implementar |
| Knowledge Graph | Diseñada (WO-002.1) — Pendiente implementar |
| Sistema de herramientas | Diseñada (WO-002.1) — Pendiente implementar |
| Motor de decisiones | Diseñada (WO-002.1) — Pendiente implementar |
| Sistema de eventos completo | Diseñada (WO-002.1) — Pendiente implementar |

### 1.6 Límites

| Límite | Descripción |
|---|---|
| **Modelo pequeño** | Qwen 2.5:0.5b tiene calidad limitada para análisis complejos |
| **Sin GPU** | Tiempos de respuesta 5-10x más lentos que con GPU |
| **SQLite** | No escala a múltiples instancias o alto concurrencia |
| **Sin rate limiting** | Sin protección contra abuso de API |
| **Sin backup automático** | Sin estrategia de backup para la BD |
| **Sin CI/CD** | Sin pipeline de integración continua |

---

# PARTE II: ARQUITECTURA GENERAL

---

## 2. Arquitectura General

### 2.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ADÁN SYSTEM                                    │
│                                                                             │
│  ┌──────────────┐                                                           │
│  │   Frontend   │  React 18 + Vite + Tailwind                              │
│  │   :5174      │  4 páginas: Login, Register, Dashboard, Nivel1           │
│  └──────┬───────┘                                                           │
│         │                                                                   │
│  ┌──────▼───────┐                                                           │
│  │   API Layer  │  FastAPI /api/v1 — 17 endpoints congelados               │
│  │   :8050      │  JWT auth, CORS, rate limiting (futuro)                  │
│  └──────┬───────┘                                                           │
│         │                                                                   │
│  ┌──────▼───────────────────────────────────────────────────────────────┐   │
│  │                        ORCHESTRATOR                                  │   │
│  │                                                                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Planner  │  │ Executor │  │ Observer │  │ Critic   │            │   │
│  │  │(planea)  │  │(ejecuta) │  │(monitorea)│  │(evalúa)  │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  │                                                                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Reviewer │  │ Memory   │  │ Tool     │  │ Event    │            │   │
│  │  │(revisa)  │  │ Manager  │  │ Manager  │  │ Manager  │            │   │
│  │  │          │  │(memoria) │  │(herram.) │  │(eventos) │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └──────┬───────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│  ┌──────▼───────────────────────────────────────────────────────────────┐   │
│  │                     CAPAS DE NEGOCIO                                 │   │
│  │                                                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │ Board Room  │  │ Gate Review │  │ Gemelo      │                 │   │
│  │  │ (4 agentes) │  │ (determinist)│  │ Digital     │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  │                                                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │ Decision    │  │ Memory      │  │ Knowledge   │                 │   │
│  │  │ Engine      │  │ Engine      │  │ Engine      │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  │                                                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐                                   │   │
│  │  │ Tool Engine │  │ Event Bus   │                                   │   │
│  │  └─────────────┘  └─────────────┘                                   │   │
│  └──────┬───────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│  ┌──────▼───────────────────────────────────────────────────────────────┐   │
│  │                     CAPAS DE INFRAESTRUCTURA                         │   │
│  │                                                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │ AI Layer    │  │ Storage     │  │ Event Store │                 │   │
│  │  │ (Ollama)    │  │ (SQLite)    │  │ (append-only)│                │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Stack Tecnológico CONGELADO

| Capa | Tecnología | Versión | Estado |
|---|---|---|---|
| Backend | Python 3.12 + FastAPI | 0.115.0 | CONGELADO |
| Frontend | React 18 + Vite + Tailwind | 5.4.3 | CONGELADO |
| Base de Datos | SQLite (WAL mode) | — | CONGELADO |
| IA | Ollama + Qwen 2.5 | 0.5b (Q4_K_M) | CONGELADO |
| Autenticación | JWT + bcrypt | python-jose 3.3.0 | CONGELADO |
| ORM | SQLAlchemy | 2.0.35 | CONGELADO |
| Infraestructura | Docker Compose | 4 servicios | CONGELADO |

### 2.3 Capas del Sistema

| Capa | Responsabilidad | Estado |
|---|---|---|
| **Frontend** | Interfaz de usuario | CONGELADO (Nivel 1) |
| **API Layer** | Endpoints REST, auth, validación | CONGELADO (Nivel 1) |
| **Orchestrator** | Coordinación de agentes y flujos | DISEÑADO (WO-002.1) |
| **Capas de Negocio** | Board Room, Gate Review, Decision Engine, etc. | PARCIALMENTE IMPLEMENTADO |
| **Capas de Infraestructura** | AI, Storage, Event Store | PARCIALMENTE IMPLEMENTADO |

---

# PARTE III: ARQUITECTURA COGNITIVA

---

## 3. Arquitectura Cognitiva

### 3.1 Los 6 Tipos de Memoria CONGELADOS

| Tipo | Descripción | Capacidad | Ciclo de Vida |
|---|---|---|---|
| **Working Memory** | Contexto activo de una request | Limitada por contexto window (32K tokens) | Volátil — se destruye al final de request |
| **Short-Term Memory** | Contexto de una sesión completa | Persiste en BD | Se consolida al cerrar sesión |
| **Long-Term Memory** | Conocimiento acumulado de todas las sesiones | Creciente, comprimida | Nunca se elimina, se archiva |
| **Episodic Memory** | Recuerdos de eventos significativos | Se mantiene por relevancia | relevance_score decae exponencialmente |
| **Semantic Memory** | Conocimiento factual y relacional (Knowledge Graph) | Estructurada en grafo | Hechos se superseden (append-only) |
| **Procedural Memory** | Cómo hacer las cosas (procedimientos aprendidos) | Creciente | confidence < 0.3 → archivado |

### 3.2 Interacción entre Memorias

```
                    ┌─────────────────┐
                    │  Working Memory  │ ← Request HTTP
                    └────────┬────────┘
                             │
                    ┌────────┼────────┐
                    │        │        │
                    ▼        ▼        ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │ Short-   │ │ Semantic │ │ Episodic │
            │ Term     │ │ Memory   │ │ Memory   │
            └─────┬────┘ └────┬─────┘ └────┬─────┘
                  │           │             │
                  └─────┬─────┘             │
                        │                   │
                        ▼                   │
                ┌──────────────┐            │
                │  Long-Term   │◄───────────┘
                │  Memory      │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │  Procedural  │
                │  Memory      │
                └──────────────┘
```

### 3.3 Reglas de Interacción

| Origen | Destino | Trigger | Qué se transfiere |
|---|---|---|---|
| Working → Short-Term | Cada turno | Turno completado | Resumen del turno |
| Short-Term → Long-Term | Cierre de sesión | Sesión terminada | Resumen comprimido |
| Episodic → Long-Term | Consolidación | relevance > 0.7 | Episodios relevantes |
| Semantic → Knowledge Graph | Extracción | Hecho detectado | Hechos validados |
| Long-Term → Procedural | Aprendizaje | N ocurrencias (N=3) | Patrones validados |
| Long-Term → Working | Recuperación | Cada request | Contexto relevante |

### 3.4 Presupuesto de Atención CONGELADO

| Componente | Tokens Máximos | Prioridad |
|---|---|---|
| Mensajes de Working Memory | 8,000 | Alta |
| Resumen de sesión (Short-Term) | 2,000 | Alta |
| Hechos relevantes (Semantic) | 3,000 | Media |
| Episodios relevantes | 2,000 | Media |
| Procedimientos aplicables | 1,000 | Baja |
| Resumen consolidado (Long-Term) | 2,000 | Baja |
| **Total** | **18,000** | — |

El presupuesto restante (14,000 tokens) se reserva para el system prompt del agente y la respuesta.

### 3.5 Consolidación

| Tipo | Origen | Destino | Trigger |
|---|---|---|---|
| Turno → Sesión | Working Memory | Short-Term | Fin de turno significativo |
| Sesión → Largo Plazo | Short-Term | Long-Term | Cierre de sesión |
| Episodio → Largo Plazo | Episodic | Long-Term | relevance_score > 0.7 |
| Hecho → Grafo | Conversación | Semantic | Extracción de hecho |
| Patrón → Procedural | Long-Term | Procedural | 3+ ocurrencias del patrón |

### 3.6 Compresión CONGELADA

| Nivel | Algoritmo | Pérdida | Cuándo |
|---|---|---|---|
| 0 | Ninguna | 0% | Working Memory |
| 1 | Truncamiento | ~30% | Mensajes > 200 chars |
| 2 | Resumen por LLM | ~60% | Fin de turno → Short-Term |
| 3 | Síntesis semántica | ~80% | Fin de sesión → Long-Term |
| 4 | Fusión de resúmenes | ~90% | Compresión periódica de Long-Term |

**Calidad mínima de compresión:** > 0.8 (preservar 80% del significado)

### 3.7 Olvido Controlado CONGELADO

**Nada se destruye.** El olvido es de-priorización.

**Fórmula unificada de relevancia:**

```python
def calculate_relevance(entry: MemoryEntry, now: datetime) -> float:
    days_since_access = (now - entry.last_accessed).days
    days_since_creation = (now - entry.created_at).days
    
    # Factor de decaimiento temporal (lambda=0.01, ~70 días para reducir a la mitad)
    temporal_decay = math.exp(-0.01 * days_since_access)
    
    # Factor de frecuencia de acceso
    access_frequency = math.log(entry.access_count + 1)
    
    # Factor de importancia
    importance = entry.importance_score
    
    # Factor de recencia de creación
    recency_boost = 1.0 / (1.0 + days_since_creation / 30)
    
    # Score ponderado
    return (
        0.30 * temporal_decay +
        0.20 * access_frequency +
        0.30 * importance +
        0.20 * recency_boost
    )
```

**Niveles de olvido:**

| Nivel | Score | Acción |
|---|---|---|
| Activo | > 0.5 | Carga completa en consultas |
| De-priorizado | 0.3 - 0.5 | Carga solo si es relevante |
| Baja prioridad | 0.1 - 0.3 | Carga solo con búsqueda explícita |
| Archivado | < 0.1 | Solo accesible por ID directo |
| Cola de eliminación | < 0.05 por 90+ días | Se mantiene 120 días más |

### 3.8 Recuperación

**Pipeline de recuperación:**

```
Query del usuario
       │
       ▼
┌─────────────────┐
│ Extract Query    │  → Entidades, temas, intención
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ Semantic Lookup  │  → Hechos del Knowledge Graph
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ Episodic Search  │  → Recuerdos relevantes
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ Long-Term Search │  → Resúmenes consolidados
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ Rank by Attention│  → Fusionar, eliminar duplicados
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ Budget Filter    │  → Seleccionar top-N dentro de 18K tokens
└─────────────────┘
```

**Prioridad de recuperación:** Semantic > Episodic > Long-Term > Procedural > Short-Term

---

# PARTE IV: ARQUITECTURA DEL CONOCIMIENTO

---

## 4. Arquitectura del Conocimiento

### 4.1 Knowledge Graph CONGELADO

El Knowledge Graph es la representación estructurada de todo lo que ADÁN sabe.

**10 Tipos de Entidad:**

| Entidad | Descripción | Ejemplo |
|---|---|---|
| **Company** | Una organización empresarial | "Paradixe" |
| **Project** | Un proyecto dentro de una empresa | "ADÁN" |
| **Person** | Una persona relevante | "Hernán (fundador)" |
| **Objective** | Un objetivo del proyecto | "Lanzamiento Q1 2027" |
| **Decision** | Una decisión tomada o propuesta | "Entrar al mercado LATAM" |
| **Event** | Un evento registrado | "Nivel 1 completado" |
| **Document** | Un documento generado o recibido | "Diagnóstico de mercado" |
| **Conversation** | Una conversación con el usuario | "Sesión del 2026-07-24" |
| **Market** | Un mercado o segmento | "SaaS para PYMEs LATAM" |
| **Risk** | Un riesgo identificado | "Competidor entrando" |

**Relaciones principales:**

```
Company → OPERATES_IN → Market
Company → HAS_PROJECT → Project
Company → COMPETES_WITH → Company
Person → FOUNDS → Company
Project → AIMS_FOR → Objective
Objective → DEPENDS_ON → Objective
Decision → AFFECTS → Objective
Decision → RESOLVES → Risk
Document → MENTIONS → [cualquier nodo]
Event → AFFECTS → [cualquier nodo]
```

**Versionado:** Append-only. Cada nodo/edge tiene `version` e `history`.

**Persistencia (Nivel 2):** SQLite + adjacency list con JSON properties.  
**Persistencia (Nivel 3+):** Evaluar grafo nativo si > 10K nodos.

### 4.2 Extracción de Hechos

```
Mensaje del usuario
       │
       ▼
┌─────────────────┐
│ NER              │  → Entidades nombradas
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ Relation         │  → Relaciones entre entidades
│ Extraction       │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ Fact Validation  │  → Hechos con confianza
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ Graph Update     │  → Inserción en Knowledge Graph
└─────────────────┘
```

**Fuentes de extracción:** Conversaciones, Board Room, Gate Review, Herramientas, Documentos.

### 4.3 Taxonomía del Conocimiento

| Categoría | Tipos | Ejemplo |
|---|---|---|
| **Empresarial** | Company, Project, Market, CustomerSegment | "Paradixe es una empresa de tech" |
| **Personal** | Person, Role, Expertise | "Hernán es fundador y CTO" |
| **Estratégico** | Objective, Decision, Risk | "El objetivo es lanzar en Q1 2027" |
| **Operativo** | Document, Conversation, Event | "Se generó un diagnóstico de mercado" |
| **Procedimental** | Procedure, BestPractice, Rule | "Cuando preguntan por precios, primero revisar el mercado" |

### 4.4 Unidades de Conocimiento

Cada unidad de conocimiento tiene:

```python
class KnowledgeUnit:
    id: UUID
    type: str                          # company, project, person, etc.
    content: str                       # representación textual
    structured: dict                   # representación estructurada
    confidence: float                  # 0-1
    source: str                        # de dónde vino
    created_at: datetime
    last_validated: datetime
    version: int
    superseded_by: UUID | None
```

### 4.5 Razonamiento sobre Conocimiento

El sistema razona sobre el conocimiento usando:

1. **Consulta directa:** "¿Qué sabes de la empresa X?"
2. **Exploración de vecinos:** "¿Quiénes son los competidores de X?"
3. **Patrón de grafo:** "¿Qué empresas operan en el mismo mercado?"
4. **Inferencia:** "¿Este mercado es atractivo?" (usa LLM con contexto del grafo)

### 4.6 Calidad del Conocimiento

| Métrica | Descripción | Target |
|---|---|---|
| **Completitud** | % de entidades con todas sus propiedades | > 80% |
| **Consistencia** | % de hechos sin contradicciones | > 95% |
| **Actualidad** | % de hechos validados en los últimos 30 días | > 70% |
| **Precisión** | % de hechos verificados manualmente | > 60% |

### 4.7 Ingesta del Conocimiento

| Fuente | Tipo de Conocimiento | Frecuencia |
|---|---|---|
| Conversaciones del usuario | Preferencias, opiniones, datos | Cada turno |
| Board Room | Análisis de viabilidad | Cada ejecución |
| Gate Review | Evaluaciones de calidad | Cada ejecución |
| Herramientas | Datos externos | Cada ejecución |
| Documentos generados | Diagnósticos, recomendaciones | Cada generación |

---

# PARTE V: ARQUITECTURA DE AGENTES

---

## 5. Arquitectura de Agentes

### 5.1 Los 8 Agentes CONGELADOS

| Agente | Responsabilidad | Estado |
|---|---|---|
| **Planner** | Determinar qué hacer antes de hacerlo | DISEÑADO |
| **Executor** | Ejecutar los pasos del plan | DISEÑADO |
| **Observer** | Monitorear la ejecución y detectar problemas | DISEÑADO |
| **Critic** | Evaluar calidad de respuestas antes de entregarlas | DISEÑADO |
| **Reviewer** | Revisar decisiones estratégicas de alto impacto | DISEÑADO |
| **Memory Manager** | Gestionar el ciclo de vida de toda la memoria | DISEÑADO |
| **Tool Manager** | Gestionar registro, descubrimiento y ejecución de herramientas | DISEÑADO |
| **Event Manager** | Gestionar el sistema de eventos como backbone de comunicación | DISEÑADO |

### 5.2 Diagrama de Orquestación

```
                          ┌──────────────┐
                          │    USER      │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │   PLANNER    │
                          └──────┬───────┘
                                 │ plan
                          ┌──────▼───────┐
                          │   EXECUTOR   │
                          └──┬───┬───┬───┘
                             │   │   │
                ┌────────────┘   │   └────────────┐
                │                │                │
         ┌──────▼──────┐ ┌──────▼──────┐ ┌───────▼─────┐
         │  BOARD ROOM │ │ GATE REVIEW │ │   TOOLS     │
         └─────────────┘ └─────────────┘ └─────────────┘
                │                │                │
                └────────────────┼────────────────┘
                                 │
                          ┌──────▼───────┐
                          │   CRITIC     │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  OBSERVER    │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │   REVIEWER   │
                          └──────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
             ┌──────▼──────┐ ┌──▼───────┐ ┌──▼──────────┐
             │   MEMORY    │ │  EVENT   │ │ KNOWLEDGE   │
             │   MANAGER   │ │  MANAGER │ │ GRAPH       │
             └─────────────┘ └──────────┘ └─────────────┘
```

### 5.3 Reglas de Comunicación

| Regla | Descripción |
|---|---|
| **Sin comunicación directa** | Los agentes NO se comunican entre sí directamente |
| **Todo pasa por Event Manager** | Toda comunicación entre agentes pasa por el Event Bus |
| **Comando → resultado** | Cada interacción produce un resultado registado |
| **Trazabilidad** | Cada interacción tiene un trace_id |

### 5.4 Requisitos de Secuencialidad

| Secuencial | Razón |
|---|---|
| Planner → Executor | El plan debe existir antes de ejecutar |
| Executor → Critic | La respuesta debe existir antes de evaluarla |
| Critic → Entrega al usuario | La aprobación debe existir antes de entregar |

### 5.5 Concurrencia Permitida

| Paralela | Condiciones |
|---|---|
| Board Room (4 agentes) | Siempre (asyncio.gather) |
| Pasos sin dependencias en plan | Executor puede paralelizar |
| Recuperación de memoria (múltiples fuentes) | Memory Manager puede paralelizar |
| Ejecución de herramientas independientes | Tool Manager puede paralelizar |
| Observer + Critic | Son independientes |

### 5.6 Gestión de Errores por Agente

| Agente | Error Handling |
|---|---|
| Planner | Si no puede planificar: escala al usuario |
| Executor | Si un paso falla: retry 1 vez → fallback → reporta al Planner |
| Observer | Si detecta problema crítico: alerta inmediata al usuario |
| Critic | Si detecta issue crítico: bloquea entrega, solicita revisión |
| Reviewer | Si no puede decidir: escala al usuario |
| Memory Manager | Si falla la recuperación: usa Working Memory como fallback |
| Tool Manager | Si la herramienta falla: retry 1 vez → reporta al Executor |
| Event Manager | Si no puede entregar: dead letter queue → retry después |

---

# PARTE VI: ARQUITECTURA DE HERRAMIENTAS

---

## 6. Arquitectura de Herramientas

### 6.1 Componentes

| Componente | Responsabilidad |
|---|---|
| **Registry** | Catálogo de todas las herramientas disponibles |
| **Discovery** | Sugerir herramientas basándose en la necesidad del agente |
| **Executor** | Ejecutar herramientas con timeout, retry y fallback |
| **Permission Manager** | Verificar que el agente tiene permiso |
| **Versioning** | Mantener múltiples versiones (semver) |
| **Observer** | Registrar métricas, logs y alertas |

### 6.2 Estructura de Herramienta

```python
class Tool:
    id: str
    name: str
    description: str
    version: str                        # semver: MAJOR.MINOR.PATCH
    category: str                       # search, computation, document, memory, event, communication
    tags: list[str]
    parameters: list[ParameterDef]
    return_type: str
    timeout_seconds: int
    max_retries: int
    retry_delay_seconds: float
    fallback_tool_id: str | None
    required_permissions: list[str]
    scope: str                          # read, write, admin
    enabled: bool
    deprecated: bool
    handler: Callable
```

### 6.3 Pipeline de Ejecución

```
Solicitud → Validate Request → Check Permissions → Validate Parameters
    → Execute with Timeout → [Éxito] → Return Result
                           → [Fallo] → Retry → [Éxito] → Return Result
                                       → [Fallo] → Fallback → [Éxito] → Return Result
                                                             → [Fallo] → Report Error
```

### 6.4 Permisos CONGELADOS

| Permiso | Descripción |
|---|---|
| `read:*` | Lectura de cualquier fuente |
| `read:web` | Lectura de internet |
| `read:database` | Lectura de bases de datos |
| `read:files` | Lectura de archivos |
| `write:memory` | Escritura en memoria |
| `write:database` | Escritura en bases de datos |
| `write:files` | Escritura de archivos |
| `tool:execute` | Ejecución de herramientas |
| `tool:manage` | Gestión de herramientas |
| `event:publish` | Publicación de eventos |
| `event:subscribe` | Suscripción a eventos |
| `memory:read` | Lectura de memoria |
| `memory:write` | Escritura de memoria |
| `memory:consolidate` | Consolidación de memoria |
| `decision:propose` | Propuesta de decisiones |
| `metrics:write` | Escritura de métricas |

### 6.5 Permisos por Agente

| Agente | Permisos |
|---|---|
| Planner | `read:*` |
| Executor | `tool:execute`, `read:*`, `write:memory` |
| Observer | `read:*`, `metrics:write` |
| Critic | `read:*` |
| Reviewer | `read:*`, `decision:propose` |
| Memory Manager | `memory:read`, `memory:write`, `memory:consolidate` |
| Tool Manager | `tool:manage`, `tool:execute` |
| Event Manager | `event:publish`, `event:subscribe` |

### 6.6 Herramientas Iniciales

| ID | Nombre | Categoría | Timeout |
|---|---|---|---|
| `web_search` | Búsqueda Web | search | 30s |
| `calculator` | Calculadora | computation | 5s |
| `document_generate` | Generador de Documentos | document | 60s |
| `memory_search` | Búsqueda en Memoria | memory | 10s |
| `event_publish` | Publicador de Eventos | event | 5s |
| `ask_user` | Preguntar al Usuario | communication | 300s |

---

# PARTE VII: ARQUITECTURA EMPRESARIAL

---

## 7. Arquitectura Empresarial

### 7.1 Modelo Universal de Empresa CONGELADO

```python
class Company:
    id: UUID
    name: str
    description: str
    industry: str
    country: str
    maturity: float                     # 0-1
    status: EntityStatus                # active, archived
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: UUID                    # primary_user
    confidence_level: float
```

**Relaciones:** 1:N Projects, 1:1 FoundingNarrative, N:1 PrimaryUser

### 7.2 Modelo Universal de Proyecto CONGELADO

```python
class Project:
    id: UUID
    company_id: UUID
    name: str
    current_level: int                  # 1-7
    status: str                         # active, paused, completed, cancelled
    maturity_score: float               # 0-100
    version: int
    created_at: datetime
    updated_at: datetime
```

**Relaciones:** N:1 Company, 1:N Levels, 1:N Cards, 1:N Scores, 1:N Decisions, 1:N Documents, 1:N Events

### 7.3 Los 7 Niveles CONGELADOS

| # | Nombre | Nombre en Inglés |
|---|---|---|
| 1 | El Dolor | The Pain |
| 2 | Propuesta de Valor | Value Proposition |
| 3 | Plan de Negocios | Business Plan |
| 4 | MVP | MVP |
| 5 | Validación Simulada | Simulated Validation |
| 6 | Lanzamiento | Launch |
| 7 | Escalamiento | Scaling |

### 7.4 Modelo Universal de Cliente (Diseño)

```python
class Customer:
    id: UUID
    company_id: UUID
    name: str
    segment: str                        # enterprise, mid_market, smb, consumer
    industry: str
    size: str                           # micro, small, medium, large
    pain_points: list[str]
    willingness_to_pay: float           # 0-1
    acquisition_cost: float
    lifetime_value: float
    status: str                         # prospect, active, churned
```

### 7.5 Modelo Universal de Procesos (Diseño)

```python
class BusinessProcess:
    id: UUID
    company_id: UUID
    name: str
    category: str                       # sales, marketing, operations, finance, hr
    maturity_level: int                 # 1-5
    automation_level: float             # 0-1
    efficiency_score: float             # 0-100
    owner_id: UUID | None
    status: str                         # active, optimized, deprecated
```

---

# PARTE VIII: ARQUITECTURA DE EVENTOS

---

## 8. Arquitectura de Eventos

### 8.1 Estructura de Evento CONGELADA

```python
class Event:
    id: UUID
    type: str
    source: str                         # agente o componente que lo generó
    agent_id: str | None
    project_id: UUID
    company_id: UUID | None
    conversation_id: UUID | None
    payload: dict
    parent_event_id: UUID | None
    trace_id: str
    timestamp: datetime
    version: str
    metadata: dict
    processed: bool
    processed_at: datetime | None
    processing_error: str | None
```

### 8.2 Tipos de Evento por Categoría

| Categoría | Tipos |
|---|---|
| **Conversación** | `user_message`, `assistant_message`, `conversation_started`, `conversation_ended` |
| **Decisión** | `decision_proposed`, `decision_made`, `decision_executed`, `decision_reversed` |
| **Board Room** | `board_room_started`, `board_room_completed`, `agent_vote_cast` |
| **Gate Review** | `gate_review_started`, `gate_review_completed` |
| **Nivel** | `level_activated`, `level_completed`, `card_created`, `card_completed` |
| **Documento** | `diagnosis_generated`, `recommendation_generated`, `document_created` |
| **Score** | `score_calculated`, `score_updated` |
| **Herramienta** | `tool_executed`, `tool_failed`, `tool_timeout` |
| **Memoria** | `memory_consolidated`, `memory_compressed`, `memory_archived`, `memory_retrieved` |
| **Conocimiento** | `knowledge_extracted`, `knowledge_updated`, `knowledge_superseded` |
| **Ciclo de Vida** | `session_started`, `session_ended`, `plan_created`, `plan_executed` |
| **Calidad** | `quality_issue_detected`, `quality_issue_resolved` |
| **Sistema** | `error_occurred`, `system_health`, `agent_state_changed` |

### 8.3 Clasificación por Impacto

| Impacto | Tipos | Acción |
|---|---|---|
| **Crítico** | `error_occurred`, `decision_reversed` | Alerta inmediata al usuario |
| **Alto** | `decision_made`, `level_completed`, `gate_review_completed` | Notificación al usuario |
| **Medio** | `board_room_completed`, `diagnosis_generated`, `tool_executed` | Log y monitoreo |
| **Bajo** | `user_message`, `assistant_message`, `memory_consolidated` | Solo log |

### 8.4 Ciclo de Vida de un Evento

```
Publicación → Validación → Persistencia → Routing → Delivery → Procesamiento
     │                                                              │
     │              ┌───────────────────────────────────────────────┘
     │              │
     │          ┌───┴───┐
     │          │       │
     │       Éxito    Fallo
     │          │       │
     │          ▼       ▼
     │    ┌──────────┐ ┌──────────┐
     │    │ PROCESSED│ │ RETRY    │
     │    │          │ │ (3 veces)│
     │    └──────────┘ └────┬─────┘
     │                      │
     │                  ┌───┴───┐
     │                  │       │
     │               Éxito   Fallo
     │                  │       │
     │                  ▼       ▼
     │            ┌──────────┐ ┌──────────┐
     │            │ PROCESSED│ │ DEAD     │
     │            │          │ │ LETTER   │
     │            └──────────┘ └──────────┘
     │
     └──▶ Persistencia (append-only, siempre)
```

### 8.5 Trazabilidad con Trace ID

Cada secuencia de eventos relacionados comparte un `trace_id`:

```
trace_id: "abc-123"
  ├── user_message
  ├── plan_created
  ├── memory_retrieved
  ├── board_room_started
  ├── agent_vote_cast (CEO)
  ├── agent_vote_cast (CTO)
  ├── agent_vote_cast (CFO)
  ├── agent_vote_cast (CMO)
  ├── board_room_completed
  ├── tool_executed
  ├── diagnosis_generated
  ├── quality_issue_detected
  ├── quality_issue_resolved
  ├── assistant_message
  └── memory_consolidated
```

### 8.6 Persistencia CONGELADA

**Tabla `events` (extendida):**

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL,
    event_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    data JSON,                          -- payload (nombre actual)
    created_at TIMESTAMP NOT NULL,
    -- Extensiones para Nivel 2:
    source TEXT,
    agent_id TEXT,
    company_id UUID,
    conversation_id UUID,
    parent_event_id UUID,
    trace_id TEXT,
    version TEXT DEFAULT '1.0',
    metadata JSON,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    processing_error TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

**Regla:** Append-only. Nunca se actualiza ni se borra un registro.

---

# PARTE IX: ARQUITECTURA DE PERSISTENCIA

---

## 9. Arquitectura de Persistencia

### 9.1 Capas de Almacenamiento

| Capa | Almacenamiento | Contenido | Retención |
|---|---|---|---|
| **Working Memory** | Memoria (volátil) | Contexto de request actual | Destrucción al final de request |
| **Short-Term Memory** | SQLite (tabla conversations) | Resúmenes de sesión | Se consolida en Long-Term |
| **Long-Term Memory** | SQLite (tablas dedicadas) | Resúmenes consolidados | Permanente (archivado, nunca borrado) |
| **Episodic Memory** | SQLite (tabla events + tabla dedicada) | Episodios significativos | Permanente (relevance decae) |
| **Semantic Memory** | SQLite (tablas kg_nodes, kg_edges) | Knowledge Graph | Permanente (append-only) |
| **Procedural Memory** | SQLite (tabla dedicada) | Procedimientos aprendidos | Permanente (archivado si confidence < 0.3) |
| **Event Store** | SQLite (tabla events) | Todos los eventos | Permanente (append-only) |

### 9.2 Tablas Congeladas (Nivel 1)

| Tabla | Registros | Propósito |
|---|---|---|
| `users` | Usuarios registrados | Autenticación |
| `companies` | Empresas | Gestión empresarial |
| `founding_narratives` | Narrativas fundacionales | Contexto de empresa |
| `projects` | Proyectos (1:1 con company) | Gestión de proyecto |
| `levels` | 7 niveles por proyecto | Progreso |
| `cards` | Tarjetas de trabajo | Unidades de trabajo |
| `conversations` | Conversaciones | Historial de chat |
| `messages` | Mensajes | Contenido de chat |
| `scores` | Scores calculados | Evaluaciones |
| `decisions` | Decisiones | Decisiones tomadas/prouestas |
| `documents` | Documentos generados | Contenido producido |
| `events` | Eventos | Trazabilidad (append-only) |

### 9.3 Tablas Futuras (Nivel 2+)

| Tabla | Propósito |
|---|---|
| `kg_nodes` | Nodos del Knowledge Graph |
| `kg_edges` | Aristas del Knowledge Graph |
| `memory_summaries` | Resúmenes consolidados de memoria |
| `episodes` | Episodios significativos |
| `procedures` | Procedimientos aprendidos |
| `user_preferences` | Preferencias del usuario |
| `patterns` | Patrones detectados |
| `lessons` | Lecciones aprendidas |

### 9.4 Versionado de Datos

| Capa | Política |
|---|---|
| Working Memory | No se versiona (volátil) |
| Short-Term Memory | Se versiona al consolidar |
| Long-Term Memory | Se versiona con cada consolidación |
| Episodic Memory | No se versiona (inmutable) |
| Semantic Memory | Cada hecho tiene superseded_by (historial completo) |
| Procedural Memory | Se versiona cuando se modifica por fallo |
| Event Store | Nunca se versiona (append-only) |

### 9.5 Eliminación de Datos

**Regla fundamental: Nada se elimina. Se archiva o se de-prioriza.**

| Tipo | Política |
|---|---|
| Mensajes de chat crudos | Se comprimen en resúmenes después de 7 días |
| Episodios irrelevantes | relevance_score decrece 10% por semana sin acceso |
| Hechos superseded | Se mantienen con superseded_by |
| Procedimientos obsoletos | Se archivan si confidence < 0.3 por 30+ días |
| Resúmenes antiguos | Se reescriben cuando acumulan > 5000 chars |

---

# PARTE X: ARQUITECTURA DE IA

---

## 10. Arquitectura de IA

### 10.1 Modelo Actual CONGELADO

| Componente | Valor |
|---|---|
| Proveedor | Ollama (local) |
| Modelo | Qwen 2.5:0.5b |
| Cuantización | Q4_K_M |
| Tamaño | 379.4 MB |
| Parámetros | 494M |
| Contexto | 32K tokens |
| Ejecución | CPU only |

### 10.2 Capa de IA CONGELADA

```
LLMAdapter (ABC)
  ├── OllamaAdapter (actual)
  ├── OpenAIAdapter (planeado)
  └── AnthropicAdapter (planeado)
```

**Factory:** `get_llm_adapter()` lee `LLM_PROVIDER`, lazy-import el adaptador.

### 10.3 Roles del LLM

| Rol | Uso | Temperature | Max Tokens |
|---|---|---|---|
| **Chat** | Conversación con usuario | 0.7 | 512 |
| **Board Room Agent** | Análisis de viabilidad | 0.6 | 512 |
| **Diagnosis Generator** | Generación de diagnósticos | 0.5 | 1024 |
| **Recommendation Generator** | Generación de recomendaciones | 0.5 | 1536 |
| **Memory Summarizer** | Resúmenes de memoria | 0.3 | 512 |
| **Fact Extractor** | Extracción de hechos | 0.2 | 256 |

### 10.4 Especialización (Diseño)

En el futuro, diferentes modelos pueden usarse para diferentes roles:

| Rol | Modelo Actual | Modelo Ideal |
|---|---|---|
| Chat | Qwen 2.5:0.5b | Qwen 2.5:7B+ |
| Board Room | Qwen 2.5:0.5b | Claude Sonnet / GPT-4o |
| Gate Review | N/A (determinístico) | N/A (nunca usa LLM) |
| Memory Summarizer | Qwen 2.5:0.5b | Modelo pequeño optimizado |
| Fact Extractor | Qwen 2.5:0.5b | Modelo pequeño optimizado |

### 10.5 Cambio de Modelo (Diseño)

```python
# Configuración por rol
MODEL_CONFIG = {
    "chat": {"provider": "ollama", "model": "qwen2.5:0.5b"},
    "board_room": {"provider": "ollama", "model": "qwen2.5:0.5b"},
    "diagnosis": {"provider": "ollama", "model": "qwen2.5:0.5b"},
    "memory": {"provider": "ollama", "model": "qwen2.5:0.5b"},
}
```

### 10.6 Fallback de Modelo

Si el modelo primario falla:
1. Reintentar una vez
2. Usar modelo alternativo del mismo proveedor
3. Si no hay alternativa: reportar error al usuario

### 10.7 Costo

| Métrica | Descripción |
|---|---|
| **Costo por llamada** | $0 (Ollama local) |
| **Costo de infraestructura** | Solo electricidad + hardware |
| **Costo de GPU** | $0 actualmente (CPU only) |
| **Costo futuro con GPU** | Variable según proveedor |

### 10.8 Latencia

| Operación | Latencia Actual (CPU) | Latencia Esperada (GPU) |
|---|---|---|
| Chat | ~4s | ~0.5s |
| Board Room (4 agentes) | ~23s | ~3s |
| Diagnóstico | ~15s | ~2s |
| Gate Review | ~0.04s | ~0.04s (determinístico) |

---

# PARTE XI: SEGURIDAD

---

## 11. Seguridad

### 11.1 Autenticación CONGELADA

| Mecanismo | Implementación |
|---|---|
| **Password hashing** | bcrypt (passlib) |
| **Token** | JWT (python-jose, HS256) |
| **Expiración** | 24 horas (1440 minutos) |
| **Storage** | localStorage en frontend |

### 11.2 Autorización (Diseño)

| Nivel | Descripción |
|---|---|
| **Autenticado** | Token JWT válido |
| **Propietario** | Usuario es el primary_user de la empresa |
| **Agente** | Agente con permisos específicos |

### 11.3 Permisos CONGELADOS

Ver Sección 6.5 (Permisos por Agente).

### 11.4 Auditoría (Diseño)

| Evento Auditado | Descripción |
|---|---|
| Login/Logout | Intentos de autenticación |
| Decisiones | Toda decisión con justificación |
| Acciones de agentes | Toda acción de un agente |
| Acceso a datos | Lecturas/escrituras sensibles |
| Errores | Todos los errores del sistema |

### 11.5 Trazabilidad CONGELADA

| Mecanismo | Descripción |
|---|---|
| **Trace ID** | Cada operación tiene un ID único |
| **Event Store** | Todos los eventos se persisten |
| **Decision Justification** | Toda decisión tiene justificación |
| **Agent Attribution** | Cada acción tiene un agente responsable |

### 11.6 Protección de Datos (Diseño)

| Medida | Descripción |
|---|---|
| **Sin datos sintéticos** | Toda información proviene del usuario |
| **Sin sharing con terceros** | Los datos nunca se comparten sin consentimiento |
| **En tránsito** | HTTPS en producción |
| **En reposo** | Cifrado de BD en producción |
| **Backup** | Diario con retención de 7 días |

---

# PARTE XII: ROADMAP

---

## 12. Roadmap de Implementación

### 12.1 Work Orders Planeadas

| WO | Nombre | Objetivo | Dependencias |
|---|---|---|---|
| **WO-003** | Motor de Conversación Inteligente | Memoria conversacional, contexto persistente, RAG interno | WO-002.3 (este documento) |
| **WO-004** | Sistema de Herramientas | Tool Engine completo con registro, descubrimiento, ejecución | WO-003 |
| **WO-005** | Knowledge Graph | Grafo de conocimiento con 10 entidades y relaciones | WO-003 |
| **WO-006** | Motor de Decisiones | Decision Engine con 4 niveles y justificación | WO-003, WO-005 |
| **WO-007** | Sistema de Eventos Completo | Event Bus con routing, replay, dead letter | WO-003 |
| **WO-008** | Orquestador de Agentes | 8 agentes coordinados | WO-003, WO-004, WO-005, WO-006, WO-007 |
| **WO-009** | Nivel 2: Propuesta de Valor | Implementación del Nivel 2 completo | WO-008 |
| **WO-010** | Observabilidad | Métricas, tracing, dashboard | WO-008 |

### 12.2 Orden de Implementación

```
WO-002.3 (Arquitectura Maestra) ← ESTAMOS AQUÍ
       │
       ▼
WO-003 (Motor de Conversación)
       │
       ├──▶ WO-004 (Herramientas)
       ├──▶ WO-005 (Knowledge Graph)
       ├──▶ WO-006 (Decision Engine)
       └──▶ WO-007 (Eventos)
       │
       ▼
WO-008 (Orquestador de Agentes)
       │
       ▼
WO-009 (Nivel 2: Propuesta de Valor)
       │
       ▼
WO-010 (Observabilidad)
```

### 12.3 Dependencias Críticas

| WO | No puede empezar hasta que | Razón |
|---|---|---|
| WO-003 | WO-002.3 esté aprobada | Necesita arquitectura maestra |
| WO-004 | WO-003 esté completa | Necesita Memory Manager para persistir |
| WO-005 | WO-003 esté completa | Necesita Semantic Memory como base |
| WO-006 | WO-003 + WO-005 estén completas | Necesita memoria + conocimiento |
| WO-007 | WO-003 esté completa | Necesita eventos de memoria |
| WO-008 | WO-003, 004, 005, 006, 007 | Necesita todos los componentes |
| WO-009 | WO-008 esté completa | Necesita orquestador funcionando |

### 12.4 Estimación de Esfuerzo

| WO | Complejidad | Estimación |
|---|---|---|
| WO-003 | Alta | 3-5 días |
| WO-004 | Media | 2-3 días |
| WO-005 | Alta | 3-5 días |
| WO-006 | Media | 2-3 días |
| WO-007 | Media | 2-3 días |
| WO-008 | Muy Alta | 5-7 días |
| WO-009 | Alta | 3-5 días |
| WO-010 | Media | 2-3 días |

---

# APÉNDICES

---

## A. Glosario

| Término | Definición |
|---|---|
| **ADÁN** | Sistema Operativo Empresarial con IA |
| **Board Room** | Sistema de 4 agentes concurrentes (CEO, CTO, CFO, CMO) |
| **Gate Review** | Evaluación determinística de calidad (0 LLM calls) |
| **Gemelo Digital** | Persistencia completa del estado del proyecto |
| **Knowledge Graph** | Grafo de conocimiento semántico |
| **Working Memory** | Contexto activo de una request |
| **Consolidación** | Proceso de transformar memorias volátiles en persistentes |
| **Compresión** | Reducción de tamaño preservando significado |
| **Olvido Controlado** | De-priorización de información obsoleta (nunca eliminación) |
| **Trace ID** | ID único para串联 eventos relacionados |
| **Contrato Base** | Patrón base para todas las entidades (AD-006) |

## B. Referencias

| Documento | Ubicación | Estado |
|---|---|---|
| BASELINE_NIVEL1.md | `docs/BASELINE_NIVEL1.md` | Reemplazado por este documento |
| CHANGELOG_WO001.md | `docs/CHANGELOG_WO001.md` | Vigente (historial) |
| TECH_DEBT.md | `docs/TECH_DEBT.md` | Vigente |
| TEST_BASELINE.md | `docs/TEST_BASELINE.md` | Vigente |
| FROZEN_INTERFACES.md | `docs/FROZEN_INTERFACES.md` | Reemplazado por este documento |
| COGNITIVE_ARCHITECTURE.md | `docs/wo-002.1/` | Reemplazado por este documento |
| AGENT_ORCHESTRATION.md | `docs/wo-002.1/` | Reemplazado por este documento |
| KNOWLEDGE_GRAPH.md | `docs/wo-002.1/` | Reemplazado por este documento |
| MEMORY_LIFECYCLE.md | `docs/wo-002.1/` | Reemplazado por este documento |
| TOOL_ARCHITECTURE.md | `docs/wo-002.1/` | Reemplazado por este documento |
| DECISION_ENGINE.md | `docs/wo-002.1/` | Reemplazado por este documento |
| EVENT_BUS.md | `docs/wo-002.1/` | Reemplazado por este documento |

## C. Resolución de Contradicciones

| # | Contradicción | Resolución |
|---|---|---|
| 1 | Reviewer threshold: $10K vs $1K | Unificado a **$10K** (más conservador) |
| 2 | Fórmulas de relevance/forgetting | Unificada en **una sola fórmula** (Sección 3.7) |
| 3 | CMO max_tokens: 521 vs 512 | Corregido a **512** (typo) |
| 4 | Conteo de tablas: 11 vs 12 | Unificado a **12 tablas** (incluyendo events) |
| 5 | Event data vs payload | Unificado a **payload** (columna `data` renombrada) |

---

**ESTE DOCUMENTO ES LA CONSTITUCIÓN TÉCNICA DE ADÁN.**

**Toda Work Order futura deberá construirse sobre esta arquitectura y nunca podrá contradecirla sin una revisión formal.**

**Fecha de Congelación:** 2026-07-24  
**Próxima Revisión:** Cuando se complete WO-008 (Orquestador de Agentes)
