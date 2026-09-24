"""
Tool Executor — Ejecución de herramientas con permisos, confirmación, timeout, retry y auditoría.

WO-097 (S16): antes los permisos, `requires_confirmation` y `timeout_seconds` se declaraban
pero no se aplicaban, y la auditoría vivía en una lista en memoria que crecía sin límite.
"""

import asyncio
import logging
import time
from collections import deque
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.tef.interfaces import (
    ToolContext, ToolResult,
    ToolRegistryInterface, ToolExecutorInterface,
)

logger = logging.getLogger(__name__)

# Lo que un usuario puede hacer sobre su propia empresa sin permisos adicionales.
# Leer archivos, consultar la base o ejecutar código queda fuera hasta tener un sandbox aislado.
DEFAULT_GRANTED_PERMISSIONS = frozenset({"read:web", "write:communication"})

# Auditoría en memoria solo cuando no hay base (agentes en pruebas unitarias); acotada
MEMORY_AUDIT_LIMIT = 1000


class ToolExecutor(ToolExecutorInterface):
    """
    Pipeline de ejecución:
    1. Lookup
    2. Validación de parámetros
    3. Permisos (los de la herramienta deben estar concedidos)
    4. Dry run
    5. Confirmación del usuario (requires_confirmation)
    6. Ejecución con timeout y reintentos con backoff
    7. Auditoría persistente (tabla tef_audit_log)
    """

    def __init__(
        self,
        registry: ToolRegistryInterface,
        db: Session | None = None,
    ):
        self.registry = registry
        self.db = db
        self._audit_log: deque[dict] = deque(maxlen=MEMORY_AUDIT_LIMIT)

    async def execute(
        self,
        tool_id: str,
        params: dict,
        context: ToolContext,
        dry_run: bool = False,
        db: Session | None = None,
    ) -> ToolResult:
        db = db or self.db
        start_time = time.time()

        def finish(result: ToolResult, audit_status: str | None = None) -> ToolResult:
            result.duration_ms = int((time.time() - start_time) * 1000)
            self._audit(tool_id, audit_status or result.status, result.error, context, db, result.duration_ms)
            return result

        # 1. Lookup
        tool = self.registry.get(tool_id)
        if not tool:
            return ToolResult(tool_id=tool_id, status="error", error=f"Tool '{tool_id}' not found")
        meta = tool.metadata()

        # 2. Validate
        is_valid, error = tool.validate(params)
        if not is_valid:
            return finish(ToolResult(tool_id=tool_id, status="error", error=error), "validation_failed")

        # 3. Permisos
        granted = context.granted_permissions
        if granted is None:
            granted = DEFAULT_GRANTED_PERMISSIONS
        missing = sorted(set(meta.permissions) - set(granted))
        if missing:
            return finish(ToolResult(
                tool_id=tool_id, status="permission_denied",
                error=f"Faltan permisos: {', '.join(missing)}",
            ))

        # 4. Dry run
        if dry_run:
            return finish(tool.dry_run(params, context))

        # 5. Confirmación: se devuelve una vista previa y no se ejecuta
        if meta.requires_confirmation and not context.confirmed:
            return finish(ToolResult(
                tool_id=tool_id, status="confirmation_required",
                output={"message": f"'{meta.name}' necesita tu confirmación antes de ejecutarse",
                        "params": params},
            ))

        # 6. Ejecución con timeout y reintentos
        last_error = None
        last_status = "error"
        retries_used = 0
        for attempt in range(meta.retries + 1):
            try:
                result = await asyncio.wait_for(tool.execute(params, context), timeout=meta.timeout_seconds)
                result.retries_used = retries_used
                if result.status == "success":
                    return finish(result)
                if result.status == "permission_denied":
                    return finish(result)
                last_error = result.error
                last_status = "error"
            except asyncio.TimeoutError:
                last_error = f"La herramienta superó su tiempo máximo ({meta.timeout_seconds} s)"
                last_status = "timeout"
            except Exception as e:
                last_error = str(e)
                last_status = "error"
                logger.warning(f"Tool {tool_id} attempt {attempt + 1} failed: {e}")
            retries_used += 1
            if attempt < meta.retries:
                await asyncio.sleep(2 ** attempt * 0.1)

        result = ToolResult(tool_id=tool_id, status=last_status, error=last_error, retries_used=retries_used)
        return finish(result, "timeout" if last_status == "timeout" else "failed")

    def _audit(
        self,
        tool_id: str,
        status: str,
        error: str | None,
        context: ToolContext,
        db: Session | None = None,
        duration_ms: int | None = None,
    ):
        """Registra cada intento: en la base si hay sesión, si no en memoria (acotada)."""
        entry = {
            "tool_id": tool_id,
            "status": status,
            "error": error,
            "company_id": context.company_id,
            "user_id": context.user_id,
            "trace_id": context.trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"Tool Audit: {tool_id} -> {status}")
        if db is None:
            self._audit_log.append(entry)
            return
        from app.tef.models import ToolAuditEntry
        db.add(ToolAuditEntry(
            tool_id=tool_id, status=status, error=error, company_id=context.company_id,
            user_id=context.user_id, trace_id=context.trace_id, duration_ms=duration_ms,
        ))
        db.commit()

    def get_audit_log(
        self,
        company_id: str | None = None,
        limit: int = 50,
        db: Session | None = None,
    ) -> list[dict]:
        """Las últimas `limit` entradas, de la más antigua a la más reciente."""
        db = db or self.db
        if db is None:
            log = [e for e in self._audit_log if not company_id or e["company_id"] == company_id]
            return log[-limit:]
        from app.tef.models import ToolAuditEntry
        query = db.query(ToolAuditEntry)
        if company_id:
            query = query.filter(ToolAuditEntry.company_id == company_id)
        rows = query.order_by(ToolAuditEntry.created_at.desc(), ToolAuditEntry.id.desc()).limit(limit).all()
        return [
            {
                "tool_id": r.tool_id, "status": r.status, "error": r.error, "company_id": r.company_id,
                "user_id": r.user_id, "trace_id": r.trace_id, "timestamp": r.created_at.isoformat(),
            }
            for r in reversed(rows)
        ]
