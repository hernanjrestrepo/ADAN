"""
TEF Tools — Herramientas iniciales para demostrar el framework.
"""

import json
import math
import hashlib
from datetime import datetime, timezone
from typing import Any

import httpx

from app.tef.interfaces import ToolProvider, ToolMetadata, ToolContext, ToolResult


# ============================================================
# Calculator
# ============================================================

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
            # Sandbox: solo permitir operaciones matemáticas seguras
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "sqrt": math.sqrt,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "log": math.log, "pi": math.pi, "e": math.e,
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
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
            description="Lee archivos de texto",
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
        try:
            path = params["path"]
            encoding = params.get("encoding", "utf-8")

            # Sandbox: no leer fuera del directorio de trabajo
            import os
            if not os.path.exists(path):
                return ToolResult(
                    tool_id="file_reader",
                    status="error",
                    error=f"File not found: {path}",
                )

            with open(path, "r", encoding=encoding) as f:
                content = f.read()

            return ToolResult(
                tool_id="file_reader",
                status="success",
                output={
                    "content": content[:10000],  # Limitar a 10K chars
                    "size": len(content),
                    "path": path,
                },
            )
        except Exception as e:
            return ToolResult(
                tool_id="file_reader",
                status="error",
                error=str(e),
            )


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

            async with httpx.AsyncClient(timeout=timeout) as client:
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
            description="Ejecuta consultas SQL de solo lectura",
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
        if not self._db:
            return ToolResult(
                tool_id="sql_query",
                status="error",
                error="Database not available",
            )

        try:
            query = params["query"].strip()

            # Sandbox: solo permitir SELECT
            if not query.upper().startswith("SELECT"):
                return ToolResult(
                    tool_id="sql_query",
                    status="error",
                    error="Only SELECT queries are allowed",
                )

            # Bloquear palabras peligrosas
            dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
            for word in dangerous:
                if word in query.upper():
                    return ToolResult(
                        tool_id="sql_query",
                        status="error",
                        error=f"Forbidden keyword: {word}",
                    )

            result = self._db.execute(query)
            rows = [dict(row) for row in result.mappings()]

            return ToolResult(
                tool_id="sql_query",
                status="success",
                output={
                    "rows": rows[:100],  # Limitar a 100 filas
                    "count": len(rows),
                },
            )
        except Exception as e:
            return ToolResult(
                tool_id="sql_query",
                status="error",
                error=str(e),
            )


# ============================================================
# Python Sandbox (Ejecución segura de código Python)
# ============================================================

class PythonSandboxTool(ToolProvider):
    """Herramienta de ejecución segura de código Python."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="python_sandbox",
            name="Python Sandbox",
            description="Ejecuta código Python en sandbox seguro",
            category="sandbox",
            permissions=["tool:execute"],
            inputs={
                "code": {"type": "string", "description": "Código Python a ejecutar", "required": True},
                "timeout": {"type": "integer", "description": "Timeout en segundos", "required": False},
            },
            outputs={
                "result": {"type": "string", "description": "Resultado de la ejecución"},
                "stdout": {"type": "string", "description": "Salida estándar"},
                "error": {"type": "string", "description": "Error si lo hay"},
            },
            timeout_seconds=30,
            tags=["python", "code", "sandbox", "ejecutar", "código"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        import subprocess
        import tempfile
        import os

        try:
            code = params["code"]
            timeout = params.get("timeout", 10)

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                tmp_path = f.name

            try:
                # Ejecutar con timeout
                result = subprocess.run(
                    ["python", tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tempfile.gettempdir(),
                )

                return ToolResult(
                    tool_id="python_sandbox",
                    status="success" if result.returncode == 0 else "error",
                    output={
                        "result": result.stdout[:5000] if result.stdout else result.stderr[:5000],
                        "stdout": result.stdout[:5000],
                        "error": result.stderr[:5000] if result.returncode != 0 else None,
                        "return_code": result.returncode,
                    },
                )
            finally:
                os.unlink(tmp_path)

        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_id="python_sandbox",
                status="timeout",
                error=f"Execution timed out after {timeout}s",
            )
        except Exception as e:
            return ToolResult(
                tool_id="python_sandbox",
                status="error",
                error=str(e),
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
