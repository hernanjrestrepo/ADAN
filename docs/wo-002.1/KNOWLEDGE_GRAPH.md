# KNOWLEDGE_GRAPH — Grafo de Conocimiento de ADÁN

**WO:** WO-002.1  
**Fecha:** 2026-07-24  
**Estado:** Diseño (sin implementar)  
**Prerequisito:** WO-001 cerrada, WO-002 baseline congelado

---

## 1. Visión General

El Knowledge Graph es la representación estructurada de todo lo que ADÁN sabe. No es una base de datos relacional — es un grafo donde las entidades son nodos y las relaciones son aristas. Cada nodo y cada arista tienen propiedades, versiones, niveles de confianza y fuentes.

**Principio:** El Knowledge Graph es la fuente de verdad semántica. Cuando un agente pregunta "¿qué sabe ADÁN sobre la empresa X?", la respuesta viene del grafo.

---

## 2. Entidades del Grafo

### 2.1 Empresa (Company)

**Descripción:** Una organización empresarial registrada en ADÁN.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `name` | str | Nombre de la empresa |
| `industry` | str | Industria principal |
| `country` | str | País de operación |
| `maturity` | float | Madurez (0-1) |
| `founded_date` | date | Fecha de fundación (si se conoce) |
| `size` | enum | micro/small/medium/large/enterprise |
| `status` | enum | active/archived |
| `created_at` | datetime | Primera vez que se registró |
| `updated_at` | datetime | Última actualización |

**Relaciones salientes:**
```
Company → OPERATES_IN → Market
Company → HAS_PROJECT → Project
Company → HAS_FOUNDER → Person
Company → COMPETES_WITH → Company
Company → USES_TECHNOLOGY → Technology
Company → SERVES_SEGMENT → CustomerSegment
```

### 2.2 Proyecto (Project)

**Descripción:** Un proyecto dentro de una empresa. 1:1 con Company en Nivel 1, pero el grafo soporta múltiples proyectos.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `name` | str | Nombre del proyecto |
| `current_level` | int | Nivel actual (1-7) |
| `status` | enum | active/paused/completed/cancelled |
| `started_at` | datetime | Cuándo comenzó |
| `maturity_score` | float | Score de madurez (0-100) |

**Relaciones salientes:**
```
Project → BELONGS_TO → Company
Project → AIMS_FOR → Objective
Project → HAS_LEVEL → Level
Project → PRODUCED → Decision
Project → PRODUCED → Document
Project → PRODUCED → Score
Project → TARGETS → Market
Project → REQUIRES → Resource
```

### 2.3 Persona (Person)

**Descripción:** Una persona relevante para la empresa (fundador, inversor, cliente, competidor).

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `name` | str | Nombre completo |
| `role` | str | Rol en la empresa o relación |
| `email` | str | Email (si se conoce) |
| `expertise` | list[str] | Áreas de experiencia |
| `influence_score` | float | Nivel de influencia (0-1) |

**Relaciones salientes:**
```
Person → FOUNDS → Company
Person → WORKS_AT → Company
Person → INVESTS_IN → Project
Person → ADVISES → Project
Person → IS_CUSTOMER_OF → Company
Person → IS_COMPETITOR_OF → Company
```

### 2.4 Objetivo (Objective)

**Descripción:** Un objetivo específico del proyecto.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `title` | str | Título del objetivo |
| `description` | str | Descripción detallada |
| `type` | enum | revenue/growth/impact/technical/personal |
| `target_value` | float | Valor objetivo (si es cuantificable) |
| `current_value` | float | Valor actual |
| `deadline` | date | Fecha límite (si aplica) |
| `priority` | enum | critical/high/medium/low |
| `status` | enum | active/achieved/abandoned/revised |

**Relaciones salientes:**
```
Objective → BELONGS_TO → Project
Objective → DEPENDS_ON → Objective
Objective → MEASURED_BY → Metric
Objective → BLOCKED_BY → Risk
```

### 2.5 Decisión (Decision)

**Descripción:** Una decisión tomada o propuesta para el proyecto.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `title` | str | Título de la decisión |
| `description` | str | Descripción detallada |
| `status` | enum | proposed/approved/rejected/executed/reversed |
| `proposed_by` | str | Quién la propuso |
| `approved_by` | str | Quién la aprobó |
| `reasoning` | str | Justificación |
| `confidence` | float | Nivel de confianza (0-100) |
| `impact_score` | float | Impacto estimado (0-100) |
| `reversible` | bool | ¿Se puede revertir? |
| `decided_at` | datetime | Cuándo se decidió |
| `executed_at` | datetime | Cuándo se ejecutó |
| `reversed_at` | datetime | Cuándo se revirtió (si aplica) |

**Relaciones salientes:**
```
Decision → MADE_FOR → Project
Decision → AFFECTS → Objective
Decision → RESOLVES → Risk
Decision → REVERSES → Decision
Decision → BASED_ON → Evidence
Decision → OPPOSED_BY → Decision (dissent)
Decision → LEADS_TO → Event
```

### 2.6 Evento (Event)

**Descripción:** Un evento registrado en el sistema.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `type` | str | Tipo de evento |
| `entity_type` | str | Tipo de entidad afectada |
| `entity_id` | UUID | Entidad afectada |
| `data` | dict | Datos del evento |
| `source` | str | Quién generó el evento |
| `timestamp` | datetime | Cuándo ocurrió |
| `importance` | float | Importancia (0-1) |

**Relaciones salientes:**
```
Event → AFFECTS → [cualquier nodo]
Event → CAUSED_BY → Decision
Event → TRIGGERED_BY → Event
```

### 2.7 Documento (Document)

**Descripción:** Un documento generado o recibido.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `title` | str | Título |
| `content` | str | Contenido |
| `doc_type` | str | Tipo (diagnosis, recommendation, report, etc.) |
| `origin` | enum | generated_by_adan/received_from_client |
| `language` | str | Idioma |
| `word_count` | int | Número de palabras |
| `created_at` | datetime | Fecha de creación |

**Relaciones salientes:**
```
Document → PRODUCED_BY → Project
Document → MENTIONS → [cualquier nodo]
Document → DERIVED_FROM → Document
Document → SUPPORTS → Decision
```

### 2.8 Conversación (Conversation)

**Descripción:** Una conversación entre el usuario y ADÁN.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `title` | str | Título/resumen |
| `summary` | str | Resumen generado |
| `message_count` | int | Número de mensajes |
| `duration_minutes` | float | Duración en minutos |
| `sentiment` | float | Sentimiento promedio (-1 a +1) |
| `started_at` | datetime | Cuándo comenzó |
| `ended_at` | datetime | Cuándo terminó |

**Relaciones salientes:**
```
Conversation → ABOUT → Project
Conversation → INVOLVES → Person
Conversation → PRODUCED → Decision
Conversation → MENTIONS → [cualquier nodo]
Conversation → CONTAINS → Message
```

### 2.9 Mercado (Market)

**Descripción:** Un mercado o segmento de mercado relevante.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `name` | str | Nombre del mercado |
| `description` | str | Descripción |
| `size_estimate` | str | Estimación de tamaño |
| `growth_rate` | float | Tasa de crecimiento estimada |
| `competition_level` | enum | low/medium/high/saturated |
| `trends` | list[str] | Tendencias identificadas |

**Relaciones salientes:**
```
Market → SERVED_BY → Company
Market → CONTAINS_SEGMENT → CustomerSegment
Market → HAS_COMPETITOR → Company
Market → HAS_TREND → Trend
```

### 2.10 Riesgo (Risk)

**Descripción:** Un riesgo identificado para el proyecto.

**Propiedades:**
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único |
| `title` | str | Título del riesgo |
| `description` | str | Descripción |
| `probability` | float | Probabilidad (0-1) |
| `impact` | float | Impacto (0-1) |
| `severity` | float | probability × impact |
| `status` | enum | identified/monitoring/mitigated/realized/accepted |
| `mitigation` | str | Estrategia de mitigación |
| `identified_at` | datetime | Cuándo se identificó |

**Relaciones salientes:**
```
Risk → AFFECTS → Project
Risk → AFFECTS → Objective
Risk → MITIGATED_BY → Decision
Risk → RELATED_TO → Risk
```

---

## 3. Grafo Completo de Relaciones

```
                        ┌──────────┐
                        │  PERSON  │
                        └────┬─────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         FOUNDS          WORKS_AT       ADVISES
              │              │              │
              ▼              ▼              ▼
         ┌─────────┐   ┌─────────┐   ┌─────────┐
         │ COMPANY │◄──│ COMPANY │   │ PROJECT │
         └────┬────┘   └────┬────┘   └────┬────┘
              │              │              │
    ┌─────────┼─────────┐   │     ┌────────┼────────┐
    │         │         │   │     │        │        │
OPERATES   COMPETES   SERVES │  AIMS_FOR  HAS    PRODUCED
    │         │         │   │     │     LEVEL     │
    ▼         ▼         ▼   │     ▼        │     ▼
┌────────┐ ┌────────┐ ┌───▼───┐ ┌────────┐ │  ┌──────────┐
│ MARKET │ │ MARKET │ │CUSTOMER│ │OBJECTIVE│ │  │DECISION  │
└────┬───┘ └────────┘ │SEGMENT│ └────┬───┘ │  └────┬─────┘
     │                └───────┘      │     │       │
     │                               │     │   AFFECTS
     │              ┌────────────────┘     │       │
     │              │                      │       ▼
     │              ▼                      │  ┌─────────┐
     │         ┌─────────┐                │  │ OBJECTIVE│
     │         │  METRIC │                │  └─────────┘
     │         └─────────┘                │
     │                                    │
     │              ┌─────────────────────┘
     │              │
     │              ▼
     │         ┌─────────┐     ┌──────────┐
     └────────▶│  EVENT  │◄────│ DOCUMENT │
               └─────────┘     └──────────┘
                    │
                    ▼
               ┌─────────┐
               │CONVERSATION│
               └─────────┘
```

---

## 4. Propiedades de las Relaciones

Cada relación tiene propiedades propias:

### 4.1 Relaciones entre Entidades

| Relación | Origen → Destino | Propiedades |
|---|---|---|
| `OPERATES_IN` | Company → Market | `since: date`, `market_share: float` |
| `COMPETES_WITH` | Company → Company | `since: date`, `intensity: enum`, `overlap_areas: list[str]` |
| `SERVES_SEGMENT` | Company → CustomerSegment | `since: date`, `products: list[str]` |
| `HAS_PROJECT` | Company → Project | `role: owner/sponsor` |
| `AIMS_FOR` | Project → Objective | `importance: float`, `progress: float` |
| `DEPENDS_ON` | Objective → Objective | `dependency_type: blocker/enabler` |
| `RESOLVES` | Decision → Risk | `effectiveness: float` |
| `BASED_ON` | Decision → Evidence | `strength: float` |
| `MENTIONS` | Document → [nodo] | `context: str`, `relevance: float` |
| `PRODUCED_BY` | [nodo] → Project | `timestamp: datetime` |

### 4.2 Relaciones Temporales

| Relación | Descripción |
|---|---|
| `PRECEDED_BY` | Evento A ocurrió antes que Evento B |
| `CAUSED_BY` | Evento A fue causado por Evento B |
| `TRIGGERED_BY` | Evento A activó Evento B |
| `SUPERSEDES` | Hecho nuevo reemplaza hecha anterior |

### 4.3 Relaciones de Confianza

| Propiedad | Tipo | Descripción |
|---|---|---|
| `confidence` | float (0-1) | Qué tan seguro está ADÁN de esta relación |
| `source` | str | De dónde vino la información |
| `verified` | bool | ¿Ha sido verificada manualmente? |
| `last_validated` | datetime | Última vez que se verificó |
| `decay_rate` | float | Qué tan rápido pierde confianza |

---

## 5. Versionado del Grafo

### 5.1 Principio

El grafo es append-only. Los cambios no sobreescriben — crean nuevas versiones.

### 5.2 Mecanismo

Cada nodo y cada arista tienen un campo `version` que se incrementa en cada cambio:

```python
class GraphNode:
    id: UUID
    type: str
    version: int                    # se incrementa en cada cambio
    properties: dict                # propiedades actuales
    history: list[VersionEntry]     # historial completo
    confidence: float
    created_at: datetime
    updated_at: datetime

class VersionEntry:
    version: int
    properties: dict                # snapshot en esa versión
    changed_by: str                 # qué agente hizo el cambio
    change_reason: str              # por qué se cambió
    timestamp: datetime
```

### 5.3 Consulta por Versión

```python
# Obtener estado actual
graph.get_node("company-123")

# Obtener estado en un momento específico
graph.get_node("company-123", version=5)

# Obtener historial completo
graph.get_history("company-123")

# Obtener cambios recientes
graph.get_recent_changes(since=datetime(2026, 7, 1))
```

---

## 6. Extracción de Hechos

### 6.1 Fuentes de Extracción

| Fuente | Tipo de Hecho | Ejemplo |
|---|---|---|
| Conversación del usuario | Preferencias, opiniones | "Prefiero datos cuantitativos" |
| Board Room | Análisis de viabilidad | "Mercado tiene CAGR del 15%" |
| Documentos generados | Diagnósticos, recomendaciones | "El dolor principal es X" |
| Gate Review | Evaluaciones | "Score: 84/100" |
| Herramientas | Datos externos | "Competidor X facturó $1M en 2025" |

### 6.2 Pipeline de Extracción

```
Mensaje del usuario
       │
       ▼
┌─────────────┐
│  NER         │  → Entidades nombradas (personas, empresas, mercados)
│  (Named      │
│  Entity      │
│  Recognition)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Relation    │  → Relaciones entre entidades
│  Extraction  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Fact        │  → Hechos extraídos con confianza
│  Validation  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Graph       │  → Inserción en el Knowledge Graph
│  Update      │
└─────────────┘
```

### 6.3 Resolución de Entidades

Cuando el usuario dice "mi empresa" o "el proyecto", el sistema debe resolver a qué entidad se refiere:

```python
def resolve_entity(mention: str, context: ConversationContext) -> EntityRef:
    # 1. Buscar en Working Memory (¿se mencionó recientemente?)
    # 2. Buscar en Short-Term Memory (¿se mencionó en esta sesión?)
    # 3. Buscar en Semantic Memory (¿es la empresa principal del usuario?)
    # 4. Pedir clarificación al usuario
```

---

## 7. Consultas al Grafo

### 7.1 Tipos de Consulta

| Tipo | Ejemplo | Mecanismo |
|---|---|---|
| Lookup directo | "¿Qué sabes de la empresa X?" | Búsqueda por ID o nombre |
| Exploración de vecinos | "¿Quiénes son los competidores de X?" | Traversal de aristas |
| Patrón de grafo | "¿Qué empresas operan en el mismo mercado que X?" | Pattern matching |
| Agregación | "¿Cuántas decisiones se tomaron este mes?" | Conteo sobre subgrafo |
| Razonamiento | "¿Este mercado es atractivo?" | Inferencia sobre hechos |

### 7.2 Lenguaje de Consulta

```python
# Lookup
graph.query().node("Company").where(name="Mi Empresa").first()

# Exploración
graph.query().node("Company", id="x").neighbors("COMPETES_WITH").all()

# Patrón
graph.query() \
    .node("Company").where(industry="tech") \
    .edge("OPERATES_IN") \
    .node("Market").where(competition_level="medium") \
    .all()

# Agregación
graph.query() \
    .node("Decision").where(project_id="x", status="approved") \
    .count()

# Razonamiento (usa LLM para inferir)
graph.reason("¿Este mercado es atractivo?", context={
    "market_facts": [...],
    "competition": [...],
    "trends": [...]
})
```

---

## 8. Persistencia del Grafo

### 8.1 Opciones de Implementación

| Opción | Ventajas | Desventajas |
|---|---|---|
| SQLite + tablas | Ya existe, simple | No es un grafo real, queries complejas lentas |
| SQLAlchemy + adjacency list | Integrado con el sistema actual | Queries de traversals son lentas |
| Neo4j | Grafo nativo, Cypher | Dependencia externa, complejidad |
| NetworkX (in-memory) | Rápido, flexible | No persiste, pierde datos al reiniciar |
| SQLite + JSON grafo | Simple, persiste | No索引索引, queries lentas a escala |

### 8.2 Recomendación

**Fase 1 (Nivel 2):** SQLite + adjacency list con JSON properties.
- Compatível con el sistema actual
- Persiste en la misma BD
- Queries de traversals con CTEs recursivas
- Suficiente para 1 empresa con 1 proyecto

**Fase 2 (Nivel 3+):** Evaluar migración a grafo nativo si:
- El grafo supera 10,000 nodos
- Las queries de traversals son lentas
- Se necesita consultas de patrón complejas

### 8.3 Esquema de Persistencia

```sql
-- Tabla de nodos
CREATE TABLE kg_nodes (
    id UUID PRIMARY KEY,
    type TEXT NOT NULL,              -- Company, Project, Person, etc.
    properties JSON NOT NULL,
    version INTEGER DEFAULT 1,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tabla de aristas
CREATE TABLE kg_edges (
    id UUID PRIMARY KEY,
    source_id UUID NOT NULL,
    target_id UUID NOT NULL,
    relation_type TEXT NOT NULL,     -- OPERATES_IN, COMPETES_WITH, etc.
    properties JSON NOT NULL,
    version INTEGER DEFAULT 1,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES kg_nodes(id),
    FOREIGN KEY (target_id) REFERENCES kg_nodes(id)
);

-- Índices
CREATE INDEX idx_nodes_type ON kg_nodes(type);
CREATE INDEX idx_edges_source ON kg_edges(source_id);
CREATE INDEX idx_edges_target ON kg_edges(target_id);
CREATE INDEX idx_edges_type ON kg_edges(relation_type);
CREATE INDEX idx_edges_source_type ON kg_edges(source_id, relation_type);
```

---

## 9. Alimentación del Grafo

### 9.1 Quién Alimenta

| Agente | Tipo de Hecho | Frecuencia |
|---|---|---|
| Memory Manager | Hechos de conversación | Cada turno |
| Board Room | Análisis de viabilidad | Cada ejecución |
| Gate Review | Evaluaciones de calidad | Cada ejecución |
| Tool Manager | Datos externos | Cada ejecución de herramienta |
| Critic | Correcciones de hechos | Cada revisión |

### 9.2 Flujo de Alimentación

```
Agente detecta hecha
       │
       ▼
┌─────────────┐
│  Validar     │  → ¿El hecha es nuevo o contradice existente?
│  Hecho       │
└──────┬──────┘
       │
       ├── Nuevo → Insertar nodo/arista
       │
       ├── Contradictorio → Crear nueva versión, marcar anterior como superseded
       │
       └── Duplicado → Actualizar confianza (incrementar)
```

---

## 10. Ejemplo de Grafo para una Empresa

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE GRAPH: ADÁN                         │
│                                                                  │
│  ┌──────────┐                                                   │
│  │ Hernán   │──── FOUNDS ────▶┌──────────────┐                  │
│  │ (Person) │                 │  Paradixe    │                  │
│  └──────────┘                 │  (Company)   │                  │
│                               └──────┬───────┘                  │
│                                      │                          │
│                              OPERATES_IN                         │
│                                      │                          │
│                                      ▼                          │
│                               ┌──────────────┐                  │
│                               │  Tech SaaS   │                  │
│                               │  (Market)    │                  │
│                               └──────────────┘                  │
│                                      │                          │
│                               COMPETES_WITH                      │
│                                      │                          │
│                                      ▼                          │
│                               ┌──────────────┐                  │
│                               │  Competidor X │                  │
│                               │  (Company)    │                  │
│                               └──────────────┘                  │
│                                                                  │
│  ┌──────────────┐                                               │
│  │  ADÁN        │──── BELONGS_TO ────▶ Paradixe                 │
│  │  (Project)   │                                               │
│  └──────┬───────┘                                               │
│         │                                                        │
│    AIMS_FOR                                                      │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │  Lanzamiento │                                               │
│  │  Q1 2027     │                                               │
│  │  (Objective) │                                               │
│  └──────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

**Este diseño está CONGELADO.**  
**Las implementaciones futuras deben adherirse a esta especificación.**  
**Los cambios de diseño requieren Work Order específica.**
