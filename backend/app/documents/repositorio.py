"""Revisión de código: Mateo (CTO) lee el repositorio de GitHub del producto y cuenta cómo está construido.

Con la API de GitHub se trae el árbol de archivos, el README, los manifiestos (package.json, requirements…) y los
archivos clave que elige la IA a partir del árbol (rutas, pagos, modelos, configuración). Un repositorio privado
necesita un token de solo lectura que el fundador da en el momento: se usa para esa revisión y no se guarda.
"""
from __future__ import annotations

import base64
import re

import httpx

from app.ai.base import LLMAdapter, LLMMessage

API = "https://api.github.com"
MAX_FILES = 22
MAX_FILE_CHARS = 9_000
MAX_TOTAL_CHARS = 110_000
_REPO = re.compile(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?(?:/|$)", re.I)
MANIFESTS = ("README.md", "readme.md", "package.json", "requirements.txt", "pyproject.toml", "go.mod", "Cargo.toml",
             "composer.json", "Gemfile", "docker-compose.yml", "Dockerfile", ".env.example")
SKIP = re.compile(r"(^|/)(node_modules|dist|build|\.next|vendor|\.git|coverage|__pycache__|\.venv|migrations/versions)/|"
                  r"\.(png|jpe?g|gif|svg|ico|webp|woff2?|ttf|mp4|mp3|lock|min\.js|map|pdf|zip)$", re.I)

PICK_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["archivos"],
               "properties": {"archivos": {"type": "array", "items": {"type": "string"}}}}


class RepoError(ValueError):
    pass


def parse(url: str) -> tuple[str, str]:
    m = _REPO.search(url or "")
    if not m:
        raise RepoError("Pásame el enlace del repositorio de GitHub (github.com/usuario/repositorio).")
    return m.group(1), m.group(2)


async def _get(client: httpx.AsyncClient, path: str) -> httpx.Response:
    resp = await client.get(f"{API}{path}")
    if resp.status_code == 404:
        raise RepoError("No encontré el repositorio: si es privado, comparte un token de solo lectura.")
    if resp.status_code in (401, 403):
        raise RepoError("GitHub no dio acceso: revisa que el token sea válido y tenga permiso de lectura del repositorio.")
    resp.raise_for_status()
    return resp


async def fetch(url: str, llm: LLMAdapter, goal: str, token: str = "") -> dict:
    owner, repo = parse(url)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ADAN-Paradixe"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        meta = (await _get(client, f"/repos/{owner}/{repo}")).json()
        branch = meta.get("default_branch", "main")
        tree = (await _get(client, f"/repos/{owner}/{repo}/git/trees/{branch}?recursive=1")).json().get("tree", [])
        paths = [t["path"] for t in tree if t.get("type") == "blob" and not SKIP.search(t["path"]) and t.get("size", 0) < 200_000]
        resp = await llm.chat_json([
            LLMMessage("system", "Eres el CTO. Del árbol de archivos de un repositorio elige los más importantes para "
                                 "entender cómo está construido y revisar el objetivo dado: entrada de la app, rutas o API, "
                                 "pagos, modelos de datos, autenticación, integraciones y configuración. Máximo 18 rutas "
                                 "exactas del árbol."),
            LLMMessage("user", f"Objetivo de la revisión: {goal or 'arquitectura, calidad y riesgos'}\n\nÁrbol:\n"
                               + "\n".join(paths[:1500])),
        ], PICK_SCHEMA, temperature=0.2, max_tokens=1200)
        picked = [p for p in (resp.parsed or {}).get("archivos", []) if p in set(paths)] if isinstance(resp.parsed, dict) else []
        wanted = [p for p in paths if p.split("/")[-1] in MANIFESTS and p.count("/") <= 1] + picked
        files, total = {}, 0
        for path in list(dict.fromkeys(wanted))[:MAX_FILES]:
            try:
                blob = (await _get(client, f"/repos/{owner}/{repo}/contents/{path}?ref={branch}")).json()
                text = base64.b64decode(blob.get("content", "")).decode("utf-8", "ignore")[:MAX_FILE_CHARS]
            except (RepoError, httpx.HTTPError, ValueError):
                continue
            if total + len(text) > MAX_TOTAL_CHARS:
                break
            files[path] = text
            total += len(text)
    return {"repo": f"{owner}/{repo}", "rama": branch, "descripcion": meta.get("description") or "",
            "lenguaje": meta.get("language") or "", "privado": bool(meta.get("private")), "archivos_totales": len(paths),
            "arbol": paths[:400], "archivos": files}


REVIEW_PROMPT = (
    "Eres Mateo, CTO del equipo de ADAN, revisando el código del producto del fundador. Con el árbol y los archivos "
    "explica en español claro (sin jerga innecesaria): 1) qué hace el producto según el código y con qué tecnología, "
    "2) cómo está organizado, 3) lo que está bien hecho, 4) riesgos concretos (seguridad, pagos, datos, escalabilidad, "
    "deuda técnica) citando el archivo, 5) qué falta para el objetivo de la revisión, y 6) las 3 acciones más "
    "importantes, en orden. Solo lo que se ve en el código; si algo no se alcanza a ver, dilo. Máximo 600 palabras."
)


async def review(llm: LLMAdapter, data: dict, goal: str, context: str = "") -> str:
    body = "\n\n".join(f"### {p}\n```\n{t}\n```" for p, t in data["archivos"].items())
    resp = await llm.chat([
        LLMMessage("system", REVIEW_PROMPT),
        LLMMessage("user", f"{context[:3000]}\n\nObjetivo de la revisión: {goal or 'arquitectura, calidad y riesgos'}\n"
                           f"Repositorio: {data['repo']} (rama {data['rama']}, {data['lenguaje']}, "
                           f"{data['archivos_totales']} archivos). {data['descripcion']}\n\nÁrbol (parcial):\n"
                           + "\n".join(data["arbol"][:300]) + f"\n\nArchivos leídos:\n{body}"),
    ], max_tokens=3500)
    return (resp.content or "").strip()
