"""Sandbox de ejecución de código Python de ADÁN (WO-093).

Servicio aparte, sin dependencias fuera de la biblioteca estándar. Cada ejecución corre en un
proceso hijo con:
- intérprete aislado (`python -I -S`: sin site-packages ni variables PYTHON*);
- entorno vacío (ningún secreto del backend llega aquí);
- carpeta temporal propia que se borra al terminar;
- límites del sistema operativo: CPU, memoria, procesos, tamaño de archivos y descriptores;
- timeout de reloj.

El aislamiento de red y de sistema de archivos lo pone el contenedor (docker-compose):
red interna sin salida a internet, raíz de solo lectura, sin capacidades, usuario sin privilegios.

    POST /run   {"code": "...", "timeout": 5}   (cabecera X-Sandbox-Token)
    GET  /health
"""
from __future__ import annotations

import hmac
import json
import os
import resource
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("SANDBOX_TOKEN", "")
PORT = int(os.environ.get("SANDBOX_PORT", "8100"))
MAX_CODE_CHARS = 20_000
MAX_OUTPUT_CHARS = 10_000
MAX_TIMEOUT = 10
MEMORY_BYTES = int(os.environ.get("SANDBOX_MEMORY_MB", "256")) * 1024 * 1024
MAX_CONCURRENT = int(os.environ.get("SANDBOX_MAX_CONCURRENT", "4"))

_slots = threading.BoundedSemaphore(MAX_CONCURRENT)


def _limits(timeout: int):
    def apply():
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout + 1))
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
        resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
        resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        os.setsid()
    return apply


def run_code(code: str, timeout: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="run-") as workdir:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", "-c", code],
                cwd=workdir,
                env={"PATH": "/usr/bin:/bin", "HOME": workdir, "LANG": "C.UTF-8"},
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=timeout,
                preexec_fn=_limits(timeout),
            )
        except subprocess.TimeoutExpired as exc:
            return {"status": "timeout", "stdout": (exc.stdout or b"").decode(errors="replace")[:MAX_OUTPUT_CHARS],
                    "stderr": f"Superó el tiempo máximo de {timeout} s", "exit_code": None}
    return {
        "status": "success" if proc.returncode == 0 else "error",
        "stdout": proc.stdout.decode(errors="replace")[:MAX_OUTPUT_CHARS],
        "stderr": proc.stderr.decode(errors="replace")[:MAX_OUTPUT_CHARS],
        "exit_code": proc.returncode,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "adan-sandbox"

    def _send(self, status: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):  # noqa: A002 — firma de BaseHTTPRequestHandler
        sys.stderr.write(json.dumps({"sandbox": format % args}) + "\n")

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"status": "ok"})
        return self._send(404, {"detail": "not found"})

    def do_POST(self):
        if self.path != "/run":
            return self._send(404, {"detail": "not found"})
        if not TOKEN or not hmac.compare_digest(self.headers.get("X-Sandbox-Token", ""), TOKEN):
            return self._send(401, {"detail": "token inválido"})
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_CODE_CHARS * 4:
            return self._send(413, {"detail": "código demasiado grande"})
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            code = body["code"]
            timeout = min(max(int(body.get("timeout", 5)), 1), MAX_TIMEOUT)
        except (ValueError, KeyError, TypeError):
            return self._send(400, {"detail": "se espera {\"code\": str, \"timeout\": int}"})
        if not isinstance(code, str) or len(code) > MAX_CODE_CHARS:
            return self._send(413, {"detail": "código demasiado grande"})
        if not _slots.acquire(blocking=False):
            return self._send(429, {"detail": "sandbox ocupado, intenta de nuevo"})
        try:
            return self._send(200, run_code(code, timeout))
        finally:
            _slots.release()


def main() -> None:
    if not TOKEN:
        sys.exit("SANDBOX_TOKEN es obligatorio")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
