"""Leer páginas web que el fundador comparte en el chat (su sitio, el de un competidor, una nota de prensa).

ADÁN abre el enlace con el cliente HTTP seguro (bloquea redes internas, también en redirecciones), saca el título,
la descripción, los encabezados y el texto visible, y se lo da al equipo como contexto del turno. Sólo HTML y
texto; un PDF enlazado se lee con el extractor de documentos.
"""
from __future__ import annotations

import asyncio
import io
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

from app.core.net import BlockedURLError, public_http_client

TIMEOUT_S = 12.0
MAX_BYTES = 3_000_000
MAX_TEXT = 12_000
MAX_URLS = 3
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ADAN-Paradixe/1.0; +https://adan.paradixe.xyz)",
    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,text/plain;q=0.8,*/*;q=0.5",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}

_URL = re.compile(r"\bhttps?://[^\s<>\"')\]]+", re.I)
# Dominios escritos sin http (www.miempresa.com, miempresa.com.co/servicios)
_BARE = re.compile(r"(?<![@\w.-])((?:www\.)?[a-z0-9][a-z0-9-]{0,62}(?:\.[a-z0-9-]{1,63})*\.(?:com|co|net|org|io|ai|app|shop|"
                   r"store|travel|tech|dev|xyz|us|mx|es|ar|cl|pe|ec|info|biz|online|site|digital)(?:\.[a-z]{2})?(?:/[^\s<>\"')\]]*)?)",
                   re.I)
_SKIP = {"script", "style", "noscript", "svg", "template", "iframe"}
_BLOCK = {"p", "div", "section", "article", "li", "br", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "header", "footer", "main"}


def find_urls(text: str) -> list[str]:
    """Enlaces del mensaje, en orden y sin repetir (máximo 3)."""
    found: list[str] = []
    for m in _URL.finditer(text or ""):
        found.append(m.group(0).rstrip(".,;:!?"))
    rest = _URL.sub(" ", text or "")
    for m in _BARE.finditer(rest):
        found.append("https://" + m.group(1).rstrip(".,;:!?"))
    out: list[str] = []
    for u in found:
        if u.lower() not in {o.lower() for o in out}:
            out.append(u)
    return out[:MAX_URLS]


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.headings: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._parts: list[str] = []
        self._skip = 0
        self._in_title = False
        self._heading: list[str] | None = None
        self._link: tuple[str, list[str]] | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in _SKIP:
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = (a.get("name") or a.get("property") or "").lower()
            if name in ("description", "og:description") and not self.description:
                self.description = (a.get("content") or "").strip()
            elif name == "og:title" and not self.title:
                self.title = (a.get("content") or "").strip()
        elif tag in ("h1", "h2", "h3"):
            self._heading = []
        elif tag == "a" and a.get("href"):
            self._link = (a["href"], [])
        if tag in _BLOCK:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in _SKIP and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3") and self._heading is not None:
            text = " ".join("".join(self._heading).split())
            if text:
                self.headings.append(f"{tag.upper()}: {text}")
            self._heading = None
        elif tag == "a" and self._link:
            label = " ".join("".join(self._link[1]).split())
            if label:
                self.links.append((label, self._link[0]))
            self._link = None
        if tag in _BLOCK:
            self._parts.append("\n")

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title = self.title or data.strip()
            return
        if self._heading is not None:
            self._heading.append(data)
        if self._link:
            self._link[1].append(data)
        self._parts.append(data)

    def text(self) -> str:
        raw = "".join(self._parts)
        lines = [" ".join(line.split()) for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def parse_html(html: str, base_url: str) -> dict:
    page = _Page()
    try:
        page.feed(html)
    except Exception:  # HTML roto: se queda con lo que alcanzó a leer
        pass
    host = urlparse(base_url).hostname or ""
    internal = []
    for label, href in page.links:
        full = urljoin(base_url, href)
        if urlparse(full).hostname == host and full.split("#")[0] != base_url and len(internal) < 15:
            internal.append(f"{label[:60]} → {full.split('#')[0]}")
    return {"titulo": page.title[:200], "descripcion": page.description[:500], "encabezados": page.headings[:30],
            "texto": page.text()[:MAX_TEXT], "enlaces": list(dict.fromkeys(internal))}


async def fetch_page(url: str, client: httpx.AsyncClient | None = None) -> dict:
    """Abre la página y devuelve lo que se lee en ella; si no se puede, `error` explica por qué en palabras simples."""
    own = client is None
    client = client or public_http_client(timeout=TIMEOUT_S, follow_redirects=True, headers=HEADERS)
    try:
        async with client.stream("GET", url) as resp:
            if resp.status_code >= 400:
                return {"url": url, "error": f"la página respondió con error {resp.status_code}"}
            body = b""
            async for chunk in resp.aiter_bytes():
                body += chunk
                if len(body) > MAX_BYTES:
                    break
            final = str(resp.url)
            ctype = resp.headers.get("content-type", "").lower()
            encoding = resp.encoding or "utf-8"
    except BlockedURLError:
        return {"url": url, "error": "la dirección no es pública"}
    except httpx.TimeoutException:
        return {"url": url, "error": "la página tardó demasiado en responder"}
    except httpx.HTTPError as e:
        return {"url": url, "error": f"no se pudo abrir ({type(e).__name__})"}
    finally:
        if own:
            await client.aclose()
    if "pdf" in ctype or final.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(body))
            text = "\n".join((p.extract_text() or "") for p in reader.pages[:30])
        except Exception:
            return {"url": final, "error": "el PDF no se pudo leer"}
        return {"url": final, "titulo": final.rsplit("/", 1)[-1], "descripcion": "", "encabezados": [],
                "texto": text[:MAX_TEXT], "enlaces": []}
    html = body.decode(encoding, errors="replace")
    if "html" not in ctype and "<html" not in html[:2000].lower():
        return {"url": final, "titulo": "", "descripcion": "", "encabezados": [], "texto": html[:MAX_TEXT], "enlaces": []}
    data = {"url": final, **parse_html(html, final)}
    if len(data["texto"]) < 200:
        data["aviso"] = ("La página casi no tiene texto en su HTML: probablemente se arma con JavaScript. Se leyó "
                         "el título, la descripción y los enlaces; pídele al fundador que pegue el texto clave si hace falta.")
    return data


SCREEN_PROMPT = ("Es la captura de una página web. Describe en español, en máximo 12 líneas: qué ofrece y a quién, "
                 "los textos y precios que se ven, los botones y llamados a la acción, cómo se compra o se paga si se "
                 "ve, y la impresión de diseño y confianza. Solo lo que se ve; no inventes.")


async def see(page: dict) -> dict:
    """Si el HTML trae poco, abre la página en el navegador real y describe la captura con visión."""
    from app.documents import media, navegador

    needs = page.get("aviso") or len(page.get("texto") or "") < 1500 or page.get("error")
    if not needs or not navegador.available():
        return page
    try:
        rendered = await navegador.render(page["url"])
    except BlockedURLError:
        return {"url": page["url"], "error": "la dirección no es pública"}
    if not rendered or rendered.get("error"):
        return page if not page.get("error") else {**page, "error": (rendered or {}).get("error", page["error"])}
    vision = ""
    shot = rendered["main"].get("screenshot")
    if shot and media.can_see():
        try:
            vision = await media.ocr_image(shot, "image/jpeg", SCREEN_PROMPT)
        except Exception:  # noqa: BLE001 - sin visión igual queda el texto
            vision = ""
    base = page if not page.get("error") else {"url": page["url"], "titulo": "", "descripcion": "", "encabezados": [],
                                                "texto": "", "enlaces": []}
    return navegador.merge(base, rendered, vision)


async def fetch_all(urls: list[str]) -> list[dict]:
    if not urls:
        return []
    async with public_http_client(timeout=TIMEOUT_S, follow_redirects=True, headers=HEADERS) as client:
        pages = list(await asyncio.gather(*(fetch_page(u, client) for u in urls[:MAX_URLS])))
    return list(await asyncio.gather(*(see(p) for p in pages)))


def as_markdown(page: dict) -> str:
    """La página como documento para la Biblioteca y para el contexto del equipo."""
    if page.get("error"):
        return f"No se pudo abrir {page['url']}: {page['error']}."
    parts = [f"# {page.get('titulo') or page['url']}", f"Fuente: {page['url']}"]
    if page.get("descripcion"):
        parts.append(f"> {page['descripcion']}")
    if page.get("aviso"):
        parts.append(f"_{page['aviso']}_")
    if page.get("pantalla"):
        parts.append("## Lo que se ve en pantalla (navegador real + visión)\n" + page["pantalla"])
    if page.get("botones"):
        parts.append("## Botones y llamados a la acción\n" + " · ".join(page["botones"]))
    if page.get("formularios"):
        parts.append("## Campos de formulario\n" + " · ".join(page["formularios"]))
    if page.get("encabezados"):
        parts.append("## Estructura\n" + "\n".join(f"- {h}" for h in page["encabezados"]))
    if page.get("texto"):
        parts.append("## Contenido\n" + page["texto"])
    if page.get("enlaces"):
        parts.append("## Secciones del sitio\n" + "\n".join(f"- {e}" for e in page["enlaces"]))
    return "\n\n".join(parts)
