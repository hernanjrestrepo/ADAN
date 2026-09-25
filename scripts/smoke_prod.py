#!/usr/bin/env python3
"""Prueba de humo del stack de producción, a través de nginx (WO-093).

    python scripts/smoke_prod.py http://127.0.0.1:8080 [--sandbox] [--sandbox-offline]

--sandbox          ejecuta Python en el sandbox a través de TEF.
--sandbox-offline  verifica además que el sandbox no tiene salida a internet (solo con Docker).

Solo usa la biblioteca estándar. Sale con código 1 en la primera verificación que falla.
"""
from __future__ import annotations

import http.cookiejar
import json
import re
import sys
import urllib.error
import urllib.request
import uuid

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8080"
FLAGS = set(sys.argv[2:])
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
passed = 0


def request(method: str, path: str, body: dict | None = None, csrf: bool = True):
    headers = {"Content-Type": "application/json"}
    if csrf:
        headers["X-Requested-With"] = "adan"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with opener.open(req, timeout=60) as resp:
            return resp.status, resp.headers, resp.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read().decode()


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed
    if not condition:
        print(f"✗ {name} {detail}")
        sys.exit(1)
    passed += 1
    print(f"✓ {name}")


status, headers, html = request("GET", "/")
check("la interfaz responde", status == 200 and '<div id="root">' in html, str(status))
check("cabeceras de seguridad", "frame-ancestors 'none'" in headers.get("Content-Security-Policy", "")
      and headers.get_all("X-Frame-Options") == ["DENY"] and headers.get("X-Content-Type-Options") == "nosniff")
status, _, spa = request("GET", "/dashboard")
check("rutas de la SPA sirven index.html", status == 200 and '<div id="root">' in spa)
asset = re.search(r'src="(/assets/[^"]+\.js)"', html)
status, headers, _ = request("GET", asset.group(1)) if asset else (0, {}, "")

check("assets con caché larga", status == 200 and "max-age=31536000" in headers.get("Cache-Control", ""))

status, headers, body = request("GET", "/health")
check("backend sano detrás de nginx", status == 200 and json.loads(body)["status"] == "ok")
check("X-Request-ID de punta a punta", len(headers.get("X-Request-ID", "")) >= 16)
check("cabeceras sin duplicar", headers.get_all("X-Frame-Options") == ["DENY"])
status, _, docs = request("GET", "/docs")
check("sin documentación pública de la API", "swagger" not in docs.lower())

email = f"smoke-{uuid.uuid4().hex[:8]}@example.com"
status, headers, _ = request("POST", "/api/v1/auth/register", {"email": email, "name": "Smoke", "password": "clave-segura-2026"})
check("registro", status == 201, str(status))
check("cookie de sesión httpOnly", "HttpOnly" in headers.get("Set-Cookie", ""))
status, _, _ = request("GET", "/api/v1/auth/me")
check("sesión por cookie", status == 200, str(status))
status, _, _ = request("POST", "/api/v1/companies/", {"name": "Sin cabecera"}, csrf=False)
check("anti-CSRF", status == 403, str(status))
status, _, body = request("POST", "/api/v1/companies/", {"name": "Smoke SAS"})
check("crear empresa", status == 201, str(status))
company_id = json.loads(body)["id"]

if "--sandbox" in FLAGS or "--sandbox-offline" in FLAGS:
    status, _, body = request("POST", "/tef/execute", {"tool_id": "python_sandbox", "company_id": company_id,
                                                       "params": {"code": "print(21 * 2)"}})
    result = json.loads(body) if status == 200 else {}
    check("Python en el sandbox", result.get("status") == "success" and result["output"]["stdout"] == "42\n", body[:300])
if "--sandbox-offline" in FLAGS:
    code = "import urllib.request\nurllib.request.urlopen('http://example.com', timeout=5)"
    status, _, body = request("POST", "/tef/execute", {"tool_id": "python_sandbox", "company_id": company_id,
                                                       "params": {"code": code}})
    result = json.loads(body) if status == 200 else {}
    check("el sandbox no tiene salida a internet", result.get("status") == "error"
          and "URLError" in (result.get("error") or ""), body[:300])
    code = "import urllib.request\nurllib.request.urlopen('http://postgres:5432', timeout=5)"
    status, _, body = request("POST", "/tef/execute", {"tool_id": "python_sandbox", "company_id": company_id,
                                                       "params": {"code": code}})
    result = json.loads(body) if status == 200 else {}
    check("el sandbox no ve la base de datos", result.get("status") == "error", body[:300])

status, _, _ = request("POST", "/api/v1/auth/logout")
check("cerrar sesión", status == 204, str(status))
status, _, _ = request("GET", "/api/v1/auth/me")
check("sesión revocada", status == 401, str(status))
print(f"\n{passed} verificaciones pasaron")
