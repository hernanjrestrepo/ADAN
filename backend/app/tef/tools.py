"""
TEF Tools — Herramientas iniciales para demostrar el framework.
"""

import ast
import json
import math
import hashlib
import operator
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.net import public_http_client
from app.tef.interfaces import ToolProvider, ToolMetadata, ToolContext, ToolResult


def _disabled_result(tool_id: str, reason: str) -> ToolResult:
    """Resultado de una herramienta deshabilitada por seguridad hasta tener aislamiento real."""
    return ToolResult(
        tool_id=tool_id,
        status="permission_denied",
        error=f"Tool disabled for security: {reason}",
    )


# ============================================================
# Calculator
# ============================================================

_CALC_MAX_LENGTH = 500
_CALC_MAX_EXPONENT = 1000
_CALC_MAX_BITS = 10_000


def _checked_pow(base, exponent):
    """pow() con límite de tamaño para evitar agotar CPU/memoria."""
    if abs(exponent) > _CALC_MAX_EXPONENT or (
        isinstance(base, int) and base.bit_length() * abs(exponent) > _CALC_MAX_BITS
    ):
        raise ValueError("Result too large")
    return pow(base, exponent)


_CALC_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: _checked_pow,
}
_CALC_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_CALC_FUNCTIONS = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sum": sum, "pow": _checked_pow, "sqrt": math.sqrt,
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log,
}
_CALC_CONSTANTS = {"pi": math.pi, "e": math.e}


def _safe_eval(node):
    """Evalúa un AST aritmético; rechaza cualquier otra construcción (sin eval)."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id in _CALC_CONSTANTS:
        return _CALC_CONSTANTS[node.id]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _CALC_UNARYOPS:
        return _CALC_UNARYOPS[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _CALC_BINOPS:
        return _CALC_BINOPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_safe_eval(elt) for elt in node.elts]
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _CALC_FUNCTIONS
        and not node.keywords
    ):
        return _CALC_FUNCTIONS[node.func.id](*[_safe_eval(arg) for arg in node.args])
    raise ValueError(f"Unsupported expression element: {type(node).__name__}")


class CalculatorTool(ToolProvider):
    """Herramienta de cálculo matemático."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="calculator",
            name="Calculator",
            description="Realiza cálculos matemáticos",
            category="computation",
            permissions=[],
            inputs={
                "expression": {"type": "string", "description": "Expresión matemática", "required": True},
            },
            outputs={
                "result": {"type": "number", "description": "Resultado del cálculo"},
            },
            timeout_seconds=5,
            retries=0,
            tags=["math", "calculate", "arithmetic", "número", "calcular"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        try:
            expression = params["expression"]
            if len(expression) > _CALC_MAX_LENGTH:
                raise ValueError("Expression too long")
            result = _safe_eval(ast.parse(expression, mode="eval"))
            return ToolResult(
                tool_id="calculator",
                status="success",
                output={"result": result, "expression": expression},
            )
        except Exception as e:
            return ToolResult(
                tool_id="calculator",
                status="error",
                error=str(e),
            )


# ============================================================
# File Reader
# ============================================================

class FileReaderTool(ToolProvider):
    """Herramienta de lectura de archivos."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="file_reader",
            name="File Reader",
            description="Deshabilitada: leía cualquier archivo del servidor",
            category="file",
            permissions=["read:files"],
            inputs={
                "path": {"type": "string", "description": "Ruta del archivo", "required": True},
                "encoding": {"type": "string", "description": "Codificación (default: utf-8)", "required": False},
            },
            outputs={
                "content": {"type": "string", "description": "Contenido del archivo"},
                "size": {"type": "integer", "description": "Tamaño en bytes"},
            },
            timeout_seconds=10,
            tags=["file", "read", "text", "archivo", "leer"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        # Leía cualquier ruta (.env, /proc, la BD). Vuelve con un almacenamiento por empresa.
        return _disabled_result("file_reader", "reads arbitrary files on the server")


# ============================================================
# HTTP Request
# ============================================================

class HttpRequestTool(ToolProvider):
    """Herramienta de requests HTTP."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="http_request",
            name="HTTP Request",
            description="Realiza requests HTTP a APIs externas",
            category="network",
            permissions=["read:web"],
            inputs={
                "url": {"type": "string", "description": "URL del endpoint", "required": True},
                "method": {"type": "string", "description": "Método HTTP (GET, POST, etc.)", "required": False},
                "headers": {"type": "object", "description": "Headers HTTP", "required": False},
                "body": {"type": "string", "description": "Body del request", "required": False},
                "timeout": {"type": "integer", "description": "Timeout en segundos", "required": False},
            },
            outputs={
                "status_code": {"type": "integer", "description": "Código de respuesta HTTP"},
                "body": {"type": "string", "description": "Body de la respuesta"},
                "headers": {"type": "object", "description": "Headers de la respuesta"},
            },
            timeout_seconds=30,
            tags=["http", "api", "request", "web", "api", "consultar"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        try:
            url = params["url"]
            method = params.get("method", "GET").upper()
            headers = params.get("headers", {})
            body = params.get("body")
            timeout = params.get("timeout", 30)

            async with public_http_client(timeout=min(float(timeout), 30)) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    content=body,
                )

            return ToolResult(
                tool_id="http_request",
                status="success",
                output={
                    "status_code": response.status_code,
                    "body": response.text[:10000],
                    "headers": dict(response.headers),
                },
            )
        except Exception as e:
            return ToolResult(
                tool_id="http_request",
                status="error",
                error=str(e),
            )


# ============================================================
# SQL Query (Mock — ejecuta contra la BD del sistema)
# ============================================================

class SqlQueryTool(ToolProvider):
    """Herramienta de consulta SQL (solo SELECT)."""

    def __init__(self, db=None):
        self._db = db

    def set_db(self, db):
        self._db = db

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="sql_query",
            name="SQL Query",
            description="Deshabilitada: SQL libre sobre la base de datos compartida",
            category="database",
            permissions=["read:database"],
            inputs={
                "query": {"type": "string", "description": "Consulta SQL (solo SELECT)", "required": True},
            },
            outputs={
                "rows": {"type": "array", "description": "Filas resultantes"},
                "count": {"type": "integer", "description": "Número de filas"},
            },
            timeout_seconds=10,
            tags=["sql", "database", "query", "consulta", "base de datos"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        # SQL libre sobre la BD compartida puede leer datos de otras empresas
        # (ej. users.hashed_password). Vuelve con vistas limitadas por empresa.
        return _disabled_result("sql_query", "raw SQL on the shared database cannot be scoped to one company")


# ============================================================
# Python Sandbox (Ejecución segura de código Python)
# ============================================================

class PythonSandboxTool(ToolProvider):
    """Ejecuta código Python en el sandbox aislado (servicio sandbox/, WO-093).

    Sin SANDBOX_URL sigue apagada: nunca ejecuta código dentro del backend.
    """

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="python_sandbox",
            name="Python Sandbox",
            description="Ejecuta código Python en un sandbox aislado, sin red ni secretos",
            category="sandbox",
            permissions=["execute:code"],
            inputs={
                "code": {"type": "string", "description": "Código Python a ejecutar", "required": True},
                "timeout": {"type": "integer", "description": "Timeout en segundos (máx. 10)", "required": False},
            },
            outputs={
                "stdout": {"type": "string", "description": "Salida estándar"},
                "stderr": {"type": "string", "description": "Errores"},
                "exit_code": {"type": "integer", "description": "Código de salida"},
            },
            timeout_seconds=15,
            retries=0,
            tags=["python", "code", "sandbox", "ejecutar", "código"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        from app.core.config import settings
        if not settings.SANDBOX_URL:
            return _disabled_result("python_sandbox", "no sandbox configured (SANDBOX_URL)")
        # Servicio interno configurado por el operador: sin proxy de salida
        async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
            response = await client.post(
                f"{settings.SANDBOX_URL.rstrip('/')}/run",
                json={"code": params["code"], "timeout": int(params.get("timeout", 5))},
                headers={"X-Sandbox-Token": settings.SANDBOX_TOKEN},
            )
        if response.status_code != 200:
            return ToolResult(tool_id="python_sandbox", status="error",
                              error=f"Sandbox respondió {response.status_code}: {response.text[:200]}")
        body = response.json()
        return ToolResult(
            tool_id="python_sandbox",
            status="success" if body["status"] == "success" else "error",
            output=body,
            error=None if body["status"] == "success" else (body.get("stderr") or body["status"])[:2000],
        )


# ============================================================
# Email Sender (Mock)
# ============================================================

class EmailSenderTool(ToolProvider):
    """Herramienta de envío de emails (mock para demostración)."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="email_sender",
            name="Email Sender",
            description="Envía emails (mock — simula envío)",
            category="communication",
            permissions=["write:communication"],
            inputs={
                "to": {"type": "string", "description": "Destinatario", "required": True},
                "subject": {"type": "string", "description": "Asunto", "required": True},
                "body": {"type": "string", "description": "Cuerpo del email", "required": True},
            },
            outputs={
                "message_id": {"type": "string", "description": "ID del mensaje"},
                "status": {"type": "string", "description": "Estado del envío"},
            },
            timeout_seconds=10,
            requires_confirmation=True,
            tags=["email", "send", "correo", "enviar", "mensaje"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        # Mock: simula envío
        message_id = hashlib.sha256(
            f"{params['to']}{params['subject']}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        return ToolResult(
            tool_id="email_sender",
            status="success",
            output={
                "message_id": message_id,
                "status": "sent (mock)",
                "to": params["to"],
                "subject": params["subject"],
            },
            metadata={
                "mock": True,
                "note": "This is a mock email sender. No real email was sent.",
            },
        )
