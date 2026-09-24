"""
Tool Executor — Ejecución de herramientas con retry, fallback y auditoría.
"""

import time
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.tef.interfaces import (
    ToolProvider, ToolMetadata, ToolContext, ToolResult,
    ToolRegistryInterface, ToolExecutorInterface,
)

logger = logging.getLogger(__name__)


class ToolExecutor(ToolExecutorInterface):
    """
    Ejecutor de herramientas con:
    - Validación de parámetros
    - Verificación de permisos
    - Retry con backoff exponencial
    - Fallback a herramienta alternativa
    - Auditoría de ejecución
    - Publicación de eventos
    """

    def __init__(
        self,
        registry: ToolRegistryInterface,
        db: Session | None = None,
    ):
        self.registry = registry
        self.db = db
        self._audit_log: list[dict] = []

    async def execute(
        self,
        tool_id: str,
        params: dict,
        context: ToolContext,
        dry_run: bool = False,
    ) -> ToolResult:
        """
        Ejecuta una herramienta con el pipeline completo:
        1. Lookup
        2. Validate
        3. Permission check
        4. Execute (with retry)
        5. Audit
        """
        start_time = time.time()

        # 1. Lookup
        tool = self.registry.get(tool_id)
        if not tool:
            return ToolResult(
                tool_id=tool_id,
                status="error",
                error=f"Tool '{tool_id}' not found",
            )

        meta = tool.metadata()

        # 2. Validate
        is_valid, error = tool.validate(params)
        if not is_valid:
            self._audit(tool_id, "validation_failed", error, context)
            return ToolResult(
                tool_id=tool_id,
                status="error",
                error=error,
            )

        # 3. Permission check (simplified)
        # En producción, verificar contra ToolPermission

        # 4. Dry run
        if dry_run:
            result = tool.dry_run(params, context)
            self._audit(tool_id, "dry_run", None, context)
            return result

        # 5. Execute with retry
        last_error = None
        retries_used = 0

        for attempt in range(meta.retries + 1):
            try:
                result = await tool.execute(params, context)
                result.duration_ms = int((time.time() - start_time) * 1000)
                result.retries_used = retries_used

                if result.status == "success":
                    self._audit(tool_id, "success", None, context)
                    return result

                # Si es error de permisos, no reintentar
                if result.status == "permission_denied":
                    self._audit(tool_id, "permission_denied", result.error, context)
                    return result

                last_error = result.error
                retries_used += 1

            except Exception as e:
                last_error = str(e)
                retries_used += 1
                logger.warning(f"Tool {tool_id} attempt {attempt + 1} failed: {e}")

            # Backoff exponencial
            if attempt < meta.retries:
                await self._async_sleep(2 ** attempt * 0.1)

        # 6. Fallback (si hay herramienta alternativa)
        # Por ahora, no hay fallback automático

        # 7. Audit failure
        duration_ms = int((time.time() - start_time) * 1000)
        self._audit(tool_id, "failed", last_error, context)

        return ToolResult(
            tool_id=tool_id,
            status="error",
            error=last_error,
            duration_ms=duration_ms,
            retries_used=retries_used,
        )

    def _audit(
        self,
        tool_id: str,
        status: str,
        error: str | None,
        context: ToolContext,
    ):
        """Registra en auditoría."""
        entry = {
            "tool_id": tool_id,
            "status": status,
            "error": error,
            "company_id": context.company_id,
            "user_id": context.user_id,
            "trace_id": context.trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._audit_log.append(entry)
        logger.info(f"Tool Audit: {tool_id} -> {status}")

    def get_audit_log(
        self,
        company_id: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Retorna el log de auditoría."""
        log = self._audit_log
        if company_id:
            log = [e for e in log if e["company_id"] == company_id]
        return log[-limit:]

    async def _async_sleep(self, seconds: float):
        """Sleep asíncrono."""
        import asyncio
        await asyncio.sleep(seconds)
