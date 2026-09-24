# TOOL_ARCHITECTURE — Sistema de Herramientas de ADÁN

**WO:** WO-002.1  
**Fecha:** 2026-07-24  
**Estado:** Diseño (sin implementar)  
**Prerequisito:** WO-001 cerrada, WO-002 baseline congelado

---

## 1. Visión General

Las herramientas son las manos de ADÁN. Mientras los agentes son la mente (piensan, planifican, deciden), las herramientas son lo que ejecuta acciones concretas: buscar en internet, calcular, generar documentos, acceder a bases de datos, enviar emails.

**Principio:** ADÁN no puede hacer nada sin herramientas. Las herramientas son la interfaz entre la cognición y la acción.

---

## 2. Arquitectura de Herramientas

### 2.1 Diagrama

```
┌─────────────────────────────────────────────────────────┐
│                      TOOL MANAGER                        │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │   Registry   │    │  Discovery   │    │  Executor │  │
│  │              │    │              │    │           │  │
│  │ tool_1       │    │ "necesito    │    │ run()     │  │
│  │ tool_2       │    │  buscar X"   │    │ timeout   │  │
│  │ tool_N       │    │  → sugiere   │    │ retry     │  │
│  │              │    │    tool_X    │    │ fallback  │  │
│  └──────────────┘    └──────────────┘    └───────────┘  │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │  Permission  │    │  Versioning  │    │  Observer │  │
│  │  Manager     │    │              │    │           │  │
│  │              │    │ tool@1.0     │    │ metrics   │  │
│  │ auth check   │    │ tool@1.1     │    │ logs      │  │
│  │ scope check  │    │ tool@2.0     │    │ alerts    │  │
│  └──────────────┘    └──────────────┘    └───────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Componentes

| Componente | Responsabilidad |
|---|---|
| Registry | Catálogo de todas las herramientas disponibles |
| Discovery | Sugerir herramientas basándose en la necesidad del agente |
| Executor | Ejecutar herramientas con timeout, retry y fallback |
| Permission Manager | Verificar que el agente tiene permiso para usar la herramienta |
| Versioning | Mantener múltiples versiones de herramientas |
| Observer | Registrar métricas, logs y alertas de ejecución |

---

## 3. Definición de Herramienta

### 3.1 Estructura

```python
class Tool:
    # Identificación
    id: str                              # "web_search"
    name: str                            # "Búsqueda Web"
    description: str                     # "Busca información en internet"
    version: str                         # "1.0.0"
    category: str                        # "search", "computation", "communication", etc.
    tags: list[str]                      # ["web", "internet", "information"]
    
    # Interfaz
    parameters: list[ParameterDef]       # parámetros de entrada
    return_type: str                     # tipo de retorno
    
    # Comportamiento
    timeout_seconds: int                 # timeout máximo
    max_retries: int                     # reintentos máximos
    retry_delay_seconds: float           # delay entre reintentos
    fallback_tool_id: str | None         # herramienta alternativa si falla
    
    # Permisos
    required_permissions: list[str]      # permisos necesarios
    scope: str                           # "read", "write", "admin"
    
    # Observabilidad
    metrics_enabled: bool                # ¿registrar métricas?
    log_level: str                       # "none", "input", "output", "full"
    
    # Estado
    enabled: bool                        # ¿está habilitada?
    deprecated: bool                     # ¿está obsoleta?
    deprecation_message: str | None      # mensaje de deprecación
    
    # Implementación
    handler: Callable                    # función que ejecuta la herramienta
```

### 3.2 Definición de Parámetros

```python
class ParameterDef:
    name: str                            # "query"
    type: str                            # "string", "integer", "float", "boolean", "enum", "json"
    description: str                     # "Término de búsqueda"
    required: bool                       # True
    default: Any | None                  # None
    min_value: Any | None                # 1 (para integers)
    max_value: Any | None                # 100 (para integers)
    enum_values: list[Any] | None        # ["web", "images", "news"] (para enums)
    pattern: str | None                  # regex pattern (para strings)
```

---

## 4. Registro de Herramientas

### 4.1 Mecanismo

Las herramientas se registran al inicio del sistema. Cada herramienta se define como una clase que hereda de `Tool` y se registra en el `ToolRegistry`:

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        self._tools[tool.id] = tool
    
    def get(self, tool_id: str) -> Tool | None:
        return self._tools.get(tool_id)
    
    def list_all(self) -> list[Tool]:
        return list(self._tools.values())
    
    def list_by_category(self, category: str) -> list[Tool]:
        return [t for t in self._tools.values() if t.category == category]
    
    def list_by_permission(self, permission: str) -> list[Tool]:
        return [t for t in self._tools.values() if permission in t.required_permissions]
```

### 4.2 Ejemplo de Registro

```python
# Definición de herramienta
web_search_tool = Tool(
    id="web_search",
    name="Búsqueda Web",
    description="Busca información en internet usando un motor de búsqueda",
    version="1.0.0",
    category="search",
    tags=["web", "internet", "information"],
    parameters=[
        ParameterDef(
            name="query",
            type="string",
            description="Término de búsqueda",
            required=True
        ),
        ParameterDef(
            name="num_results",
            type="integer",
            description="Número de resultados a retornar",
            required=False,
            default=5,
            min_value=1,
            max_value=20
        )
    ],
    return_type="list[SearchResult]",
    timeout_seconds=30,
    max_retries=2,
    retry_delay_seconds=1.0,
    fallback_tool_id=None,
    required_permissions=["search:internet"],
    scope="read",
    metrics_enabled=True,
    log_level="input",
    enabled=True,
    deprecated=False,
    deprecation_message=None,
    handler=web_search_handler
)

# Registro
registry.register(web_search_tool)
```

---

## 5. Descubrimiento de Herramientas

### 5.1 Problema

Los agentes no siempre saben qué herramienta necesitan. El Planner dice "necesito buscar información sobre el mercado" pero no sabe que existe una herramienta llamada `web_search`.

### 5.2 Solución

El Tool Manager ofrece un servicio de descubrimiento que sugiere herramientas basándose en:

1. **Descripción de la necesidad** (texto libre del agente)
2. **Tags de las herramientas** (match semántico)
3. **Historial de uso** (qué herramientas se usaron para necesidades similares)

### 5.3 Pipeline de Descubrimiento

```
Necesidad del agente: "buscar información sobre el mercado de SaaS en LATAM"
       │
       ▼
┌─────────────────┐
│ 1. EXTRACT       │  → Keywords: "buscar", "información", "mercado", "SaaS", "LATAM"
│    KEYWORDS      │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 2. MATCH AGAINST │  → web_search (tags: web, internet, information)
│    TOOL TAGS     │  → database_query (tags: data, query)
│                  │  → market_research (tags: market, research)
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 3. RANK BY       │  → web_search: 0.85 (match "buscar" + "información")
│    RELEVANCE     │  → market_research: 0.72 (match "mercado")
│                  │  → database_query: 0.30 (match "query")
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 4. RETURN TOP-3  │  → [web_search, market_research, database_query]
│    SUGGESTIONS   │
└─────────────────┘
```

### 5.4 API de Descubrimiento

```python
class ToolManager:
    def discover_tools(self, need_description: str, top_k: int = 3) -> list[ToolSuggestion]:
        """
        Sugiere herramientas para una necesidad descrita en lenguaje natural.
        """
        # 1. Extraer keywords
        keywords = extract_keywords(need_description)
        
        # 2. Calcular score por herramienta
        scores = []
        for tool in self.registry.list_all():
            if not tool.enabled or tool.deprecated:
                continue
            score = self._calculate_relevance(tool, need_description, keywords)
            scores.append((tool, score))
        
        # 3. Ordenar y retornar top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return [ToolSuggestion(tool=t, score=s) for t, s in scores[:top_k]]
    
    def _calculate_relevance(self, tool: Tool, description: str, keywords: list[str]) -> float:
        # Score por match de tags
        tag_match = len(set(keywords) & set(tool.tags)) / max(len(keywords), 1)
        
        # Score por similitud semántica con descripción
        desc_similarity = cosine_similarity(
            embed(description),
            embed(tool.description)
        )
        
        # Score por historial de uso
        usage_score = self._get_usage_score(tool.id)
        
        return 0.4 * tag_match + 0.4 * desc_similarity + 0.2 * usage_score
```

---

## 6. Permisos

### 6.1 Modelo de Permisos

Cada herramienta requiere permisos específicos. Los agentes tienen permisos asignados según su rol:

| Agente | Permisos |
|---|---|
| Planner | `read:*` (solo lectura) |
| Executor | `tool:execute`, `read:*`, `write:memory` |
| Observer | `read:*`, `metrics:write` |
| Critic | `read:*` (solo lectura) |
| Reviewer | `read:*`, `decision:propose` |
| Memory Manager | `memory:read`, `memory:write`, `memory:consolidate` |
| Tool Manager | `tool:manage`, `tool:execute` |
| Event Manager | `event:publish`, `event:subscribe` |

### 6.2 Verificación de Permisos

```python
class PermissionManager:
    def check_permission(self, agent_id: str, tool_id: str) -> bool:
        agent_permissions = self.get_agent_permissions(agent_id)
        tool_requirements = self.registry.get(tool_id).required_permissions
        
        for required in tool_requirements:
            if required not in agent_permissions:
                return False
        
        return True
    
    def get_agent_permissions(self, agent_id: str) -> list[str]:
        # Permisos del agente + permisos del scope
        agent = self.get_agent(agent_id)
        return agent.permissions + self.get_scope_permissions(agent.scope)
```

### 6.3 Escalabilidad de Permisos

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

---

## 7. Ejecución

### 7.1 Pipeline de Ejecución

```
Solicitud de ejecución
       │
       ▼
┌─────────────────┐
│ 1. VALIDATE      │  → ¿La herramienta existe? ¿Está habilitada?
│    REQUEST       │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 2. CHECK         │  → ¿El agente tiene permiso?
│    PERMISSIONS   │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 3. VALIDATE      │  → ¿Los parámetros son correctos?
│    PARAMETERS    │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 4. EXECUTE       │  → Ejecutar con timeout
│    WITH TIMEOUT  │
└──────────┬──────┘
           │
       ┌───┴───┐
       │       │
     Éxito   Fallo
       │       │
       ▼       ▼
┌──────────┐ ┌──────────┐
│ 5. RETURN │ │ 6. RETRY │
│  RESULT   │ │    or    │
│           │ │ FALLBACK │
└──────────┘ └────┬─────┘
                  │
              ┌───┴───┐
              │       │
            Éxito   Fallo definitivo
              │       │
              ▼       ▼
         ┌──────────┐ ┌──────────┐
         │ 5. RETURN │ │ 7. REPORT│
         │  RESULT   │ │  ERROR   │
         │           │ │          │
         └──────────┘ └──────────┘
```

### 7.2 Implementación del Executor

```python
class ToolExecutor:
    async def execute(
        self,
        tool_id: str,
        parameters: dict,
        agent_id: str,
        context: ExecutionContext
    ) -> ToolExecutionResult:
        
        tool = self.registry.get(tool_id)
        
        # 1. Validar que la herramienta existe y está habilitada
        if not tool or not tool.enabled:
            return ToolExecutionResult(
                tool_id=tool_id,
                status="not_found",
                error=f"Tool {tool_id} not found or disabled"
            )
        
        # 2. Verificar permisos
        if not self.permission_manager.check_permission(agent_id, tool_id):
            return ToolExecutionResult(
                tool_id=tool_id,
                status="permission_denied",
                error=f"Agent {agent_id} lacks permission for {tool_id}"
            )
        
        # 3. Validar parámetros
        validation = self._validate_parameters(tool, parameters)
        if not validation.valid:
            return ToolExecutionResult(
                tool_id=tool_id,
                status="invalid_parameters",
                error=validation.error
            )
        
        # 4. Ejecutar con timeout
        try:
            result = await asyncio.wait_for(
                tool.handler(**parameters),
                timeout=tool.timeout_seconds
            )
            
            return ToolExecutionResult(
                tool_id=tool_id,
                tool_version=tool.version,
                status="success",
                output=result,
                duration_ms=int((time.time() - start_time) * 1000)
            )
            
        except asyncio.TimeoutError:
            # 5. Retry
            if retry_count < tool.max_retries:
                await asyncio.sleep(tool.retry_delay_seconds)
                return await self.execute(tool_id, parameters, agent_id, context, retry_count + 1)
            
            # 6. Fallback
            if tool.fallback_tool_id:
                return await self.execute(tool.fallback_tool_id, parameters, agent_id, context)
            
            # 7. Error definitivo
            return ToolExecutionResult(
                tool_id=tool_id,
                status="timeout",
                error=f"Tool {tool_id} timed out after {tool.timeout_seconds}s"
            )
```

---

## 8. Versionado

### 8.1 Política

Las herramientas se versionan con semver (MAJOR.MINOR.PATCH):

| Tipo de Cambio | Versión | Ejemplo |
|---|---|---|
| Bug fix, sin cambio de interfaz | PATCH | 1.0.0 → 1.0.1 |
| Nueva funcionalidad, interfaz compatible | MINOR | 1.0.0 → 1.1.0 |
| Cambio de interfaz (breaking) | MAJOR | 1.0.0 → 2.0.0 |

### 8.2 Mecanismo

```python
class ToolVersion:
    tool_id: str
    version: str
    changelog: str
    deprecated: bool
    deprecation_date: date | None
    removal_date: date | None
    migration_guide: str | None
```

### 8.3 Compatibilidad

- Las versiones MINOR son backward-compatible
- Las versiones MAJOR requieren que los agentes actualicen sus llamadas
- Las versiones deprecated siguen funcionando por 90 días después de la deprecación
- Las versiones removed se eliminan del registry

---

## 9. Timeout

### 9.1 Política de Timeout

| Categoría de Herramienta | Timeout Default | Máximo |
|---|---|---|
| Búsqueda web | 30s | 60s |
| Cálculos | 5s | 30s |
| Acceso a BD | 10s | 30s |
| Generación de documentos | 60s | 120s |
| Llamadas a LLM | 120s | 300s |
| Envío de emails | 30s | 60s |
| Operaciones de archivos | 10s | 30s |

### 9.2 Manejo de Timeout

```python
# Timeout por herramienta
tool.timeout_seconds = 30

# Timeout global de ejecución (si el plan tiene múltiples pasos)
PLAN_TIMEOUT_SECONDS = 600  # 10 minutos máximo por plan
```

---

## 10. Fallback

### 10.1 Estrategia de Fallback

Cuando una herramienta falla, el sistema puede:

1. **Retry:** Reintentar la misma herramienta (con delay exponencial)
2. **Fallback:** Usar una herramienta alternativa
3. **Degrade:** Continuar sin el resultado de la herramienta
4. **Escalate:** Reportar al usuario que la herramienta falló

### 10.2 Configuración de Fallback

```python
# Ejemplo: web_search falla → intentar database_query como fallback
web_search_tool = Tool(
    id="web_search",
    fallback_tool_id="database_query",  # fallback
    max_retries=2,                       # reintentar 2 veces antes de fallback
    retry_delay_seconds=1.0
)
```

### 10.3 Cadena de Fallback

```
web_search → database_query → manual_input
```

Si `web_search` falla después de 2 reintentos, intenta `database_query`. Si esa también falla, solicita input manual del usuario.

---

## 11. Observabilidad

### 11.1 Métricas por Herramienta

| Métrica | Descripción |
|---|---|
| `tool_executions_total` | Total de ejecuciones |
| `tool_executions_success` | Ejecuciones exitosas |
| `tool_executions_failed` | Ejecuciones fallidas |
| `tool_executions_timeout` | Ejecuciones con timeout |
| `tool_duration_seconds` | Duración promedio de ejecución |
| `tool_retry_rate` | Tasa de reintentos |
| `tool_fallback_rate` | Tasa de uso de fallback |

### 11.2 Logs

```python
# Log de cada ejecución
ToolExecutionLog:
    tool_id: str
    tool_version: str
    agent_id: str
    parameters: dict                    # (sanitized, sin secrets)
    result_status: str
    duration_ms: int
    retry_count: int
    used_fallback: bool
    error: str | None
    timestamp: datetime
    trace_id: str                       # para tracing distribuido
```

### 11.3 Dashboard

```
┌─────────────────────────────────────────────────┐
│              TOOL USAGE DASHBOARD                │
│                                                  │
│  Tool              Execs   Success   Avg Time    │
│  ─────────────     ─────   ───────   ────────    │
│  web_search        142     94%       2.3s        │
│  database_query    87      99%       0.4s        │
│  calculator        234     100%      0.1s        │
│  document_gen      56      89%       15.2s       │
│  email_send        12      92%       3.1s        │
│                                                  │
│  Alerts:                                         │
│  ⚠ document_gen: 11% failure rate (> 10% threshold)│
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 12. Herramientas Iniciales (Nivel 2)

### 12.1 Categorías

| Categoría | Herramientas | Descripción |
|---|---|---|
| Búsqueda | `web_search`, `database_search` | Buscar información |
| Cálculo | `calculator`, `data_analysis` | Procesar datos |
| Documentos | `document_generate`, `document_read` | Crear/leer documentos |
| Memoria | `memory_search`, `memory_write` | Acceder/modificar memoria |
| Eventos | `event_publish`, `event_subscribe` | Publicar/suscribir eventos |
| Comunicación | `notify_user`, `ask_user` | Interactuar con el usuario |

### 12.2 Definiciones Iniciales

```python
INITIAL_TOOLS = [
    # Búsqueda
    Tool(
        id="web_search",
        name="Búsqueda Web",
        description="Busca información en internet",
        category="search",
        timeout_seconds=30,
        required_permissions=["read:web"]
    ),
    
    # Cálculo
    Tool(
        id="calculator",
        name="Calculadora",
        description="Realiza cálculos matemáticos",
        category="computation",
        timeout_seconds=5,
        required_permissions=["tool:execute"]
    ),
    
    # Documentos
    Tool(
        id="document_generate",
        name="Generador de Documentos",
        description="Genera documentos estructurados (diagnósticos, reportes, etc.)",
        category="document",
        timeout_seconds=60,
        required_permissions=["write:memory"]
    ),
    
    # Memoria
    Tool(
        id="memory_search",
        name="Búsqueda en Memoria",
        description="Busca información en la memoria del sistema",
        category="memory",
        timeout_seconds=10,
        required_permissions=["memory:read"]
    ),
    
    # Eventos
    Tool(
        id="event_publish",
        name="Publicador de Eventos",
        description="Publica un evento en el sistema",
        category="event",
        timeout_seconds=5,
        required_permissions=["event:publish"]
    ),
    
    # Comunicación
    Tool(
        id="ask_user",
        name="Preguntar al Usuario",
        description="Formula una pregunta al usuario y espera su respuesta",
        category="communication",
        timeout_seconds=300,  # 5 minutos para que el usuario responda
        required_permissions=["tool:execute"]
    )
]
```

---

## 13. Extensibilidad

### 13.1 Agregar Nueva Herramienta

Para agregar una nueva herramienta al sistema:

1. Definir la clase `Tool` con todos los campos requeridos
2. Implementar el `handler` (función que ejecuta la herramienta)
3. Registrar en `ToolRegistry` al inicio del sistema
4. Definir permisos requeridos
5. Documentar la herramienta

### 13.2 Plugin System (Futuro)

En el futuro, las herramientas podrán cargarse como plugins:

```python
# Estructura de plugin
plugins/
├── web_search/
│   ├── plugin.json          # metadata del plugin
│   ├── tool.py              # implementación
│   └── tests/
└── database/
    ├── plugin.json
    ├── tool.py
    └── tests/
```

---

**Este diseño está CONGELADO.**  
**Las implementaciones futuras deben adherirse a esta especificación.**  
**Los cambios de diseño requieren Work Order específica.**
