"""
TEF Interfaces — Contratos que toda herramienta debe implementar.
"""

import abc
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ============================================================
# ToolMetadata — Declaración de la herramienta
# ============================================================

@dataclass
class ToolMetadata:
    """Metadata completa de una herramienta."""
    id: str
    name: str
    description: str
    category: str                          # file, database, network, computation, communication, sandbox
    permissions: list[str] = field(default_factory=list)
    inputs: dict[str, dict] = field(default_factory=dict)     # param_name -> {type, description, required}
    outputs: dict[str, dict] = field(default_factory=dict)    # field_name -> {type, description}
    estimated_cost: float = 0.0            # costo estimado (tokens, dinero, etc.)
    estimated_latency_ms: int = 1000       # latencia estimada
    timeout_seconds: int = 30
    retries: int = 2
    version: str = "1.0.0"
    owner: str = "system"
    requires_confirmation: bool = False     # ¿necesita confirmación del usuario?
    supports_dry_run: bool = False          # ¿soporta ejecución en seco?
    supports_parallel: bool = True          # ¿puede ejecutarse en paralelo?
    supports_streaming: bool = False        # ¿soporta streaming de resultados?
    tags: list[str] = field(default_factory=list)


# ============================================================
# ToolContext — Contexto de ejecución
# ============================================================

@dataclass
class ToolContext:
    """Contexto disponible para la ejecución de una herramienta."""
    company_id: str
    user_id: str
    trace_id: str
    conversation_id: str | None = None
    project_id: str | None = None
    metadata: dict = field(default_factory=dict)
    # Permisos concedidos a quien ejecuta; None = los permisos por defecto del ejecutor
    granted_permissions: frozenset[str] | None = None
    # El usuario confirmó la acción (herramientas con requires_confirmation)
    confirmed: bool = False


# ============================================================
# ToolResult — Resultado de ejecución
# ============================================================

@dataclass
class ToolResult:
    """Resultado de la ejecución de una herramienta."""
    tool_id: str
    status: str                            # success, error, timeout, permission_denied, dry_run
    output: Any = None
    error: str | None = None
    duration_ms: int = 0
    retries_used: int = 0
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================
# ToolProvider — Interfaz abstracta de herramienta
# ============================================================

class ToolProvider(abc.ABC):
    """
    Interfaz que toda herramienta debe implementar.
    
    Contrato:
    - metadata() retorna la declaración de la herramienta
    - execute() ejecuta la herramienta
    - validate() valida parámetros antes de ejecutar
    """

    @abc.abstractmethod
    def metadata(self) -> ToolMetadata:
        """Retorna la metadata de la herramienta."""
        ...

    @abc.abstractmethod
    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        """Ejecuta la herramienta con los parámetros dados."""
        ...

    def validate(self, params: dict) -> tuple[bool, str | None]:
        """
        Valida los parámetros antes de ejecutar.
        Retorna (is_valid, error_message).
        """
        meta = self.metadata()
        for param_name, param_def in meta.inputs.items():
            if param_def.get("required", False) and param_name not in params:
                return False, f"Parameter '{param_name}' is required"
        return True, None

    def dry_run(self, params: dict, context: ToolContext) -> ToolResult:
        """
        Ejecución en seco (sin efectos secundarios).
        Solo retorna qué haría la herramienta.
        """
        return ToolResult(
            tool_id=self.metadata().id,
            status="dry_run",
            output={"action": "would execute", "params": params},
        )


# ============================================================
# ToolRegistry — Interfaz del registro de herramientas
# ============================================================

class ToolRegistryInterface(abc.ABC):
    """Interfaz para el registro de herramientas."""

    @abc.abstractmethod
    def register(self, tool: ToolProvider) -> None:
        """Registra una herramienta."""
        ...

    @abc.abstractmethod
    def get(self, tool_id: str) -> ToolProvider | None:
        """Obtiene una herramienta por ID."""
        ...

    @abc.abstractmethod
    def list_all(self) -> list[ToolMetadata]:
        """Lista todas las herramientas registradas."""
        ...

    @abc.abstractmethod
    def discover(self, query: str, permissions: list[str] | None = None) -> list[ToolMetadata]:
        """Descubre herramientas relevantes para una query."""
        ...


# ============================================================
# ToolExecutor — Interfaz del ejecutor
# ============================================================

class ToolExecutorInterface(abc.ABC):
    """Interfaz para la ejecución de herramientas."""

    @abc.abstractmethod
    async def execute(
        self,
        tool_id: str,
        params: dict,
        context: ToolContext,
        dry_run: bool = False,
        db=None,
    ) -> ToolResult:
        """Ejecuta una herramienta con permisos, confirmación, timeout, retry y auditoría."""
        ...
