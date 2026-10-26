"""Navegador real para ADÁN: abre páginas hechas con JavaScript (React, Vue, Next…) en Chromium sin ventana,
espera a que se pinten, lee el texto visible y las secciones internas, y toma una captura que la visión de Kimi
describe (cómo se ve, qué botones hay, cómo se paga).

Cada petición del navegador (la página, sus scripts, imágenes y llamadas) pasa por la misma protección SSRF
del cliente HTTP: nada que resuelva a una red interna se carga. Si Playwright no está instalado, se devuelve
None y el lector HTML simple sigue funcionando.
"""
from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse

from app.core.net import BlockedURLError, ensure_public_url

log = logging.getLogger(__name__)

PAGE_TIMEOUT_MS = 25_000
SETTLE_MS = 2_500
MAX_SUBPAGES = 3
MAX_TEXT = 12_000
VIEWPORT = {"width": 1366, "height": 900}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 "
      "ADAN-Paradixe/1.0")

# Texto visible, encabezados, botones y enlaces internos de la página ya pintada
_EXTRACT = """() => {
  const clean = (t) => (t || '').replace(/\\s+/g, ' ').trim();
  const heads = [...document.querySelectorAll('h1,h2,h3')].map(h => h.tagName + ': ' + clean(h.innerText)).filter(h => h.length > 4);
  const buttons = [...document.querySelectorAll('button,[role=button],input[type=submit],a.btn,a[class*=button]')]
    .map(b => clean(b.innerText || b.value || b.getAttribute('aria-label'))).filter(Boolean);
  const links = [...document.querySelectorAll('a[href]')].map(a => [clean(a.innerText), a.href]).filter(([t, h]) => t && h.startsWith('http'));
  const forms = [...document.querySelectorAll('input,select,textarea')].map(i => clean(i.getAttribute('placeholder') || i.getAttribute('name') || i.getAttribute('aria-label') || i.type)).filter(Boolean);
  const logos = [...document.querySelectorAll('img')].filter(i => /logo/i.test(i.src + ' ' + i.alt + ' ' + i.className + ' ' + i.id) && i.src.startsWith('http')).map(i => i.src).slice(0, 3);
  return { title: document.title, text: document.body ? document.body.innerText : '', heads, logos, buttons: [...new Set(buttons)].slice(0, 40),
           links, forms: [...new Set(forms)].slice(0, 30) };
}"""


def available() -> bool:
    try:
        import playwright.async_api  # noqa: F401
    except ImportError:
        return False
    return True


async def _guard(route):
    try:
        await ensure_public_url(route.request.url)
    except BlockedURLError:
        await route.abort("blockedbyclient")
        return
    except Exception:  # noqa: BLE001 - un error de DNS no debe tumbar la página entera
        await route.abort("failed")
        return
    await route.continue_()


async def _open(context, url: str, screenshot: bool) -> dict:
    page = await context.new_page()
    await page.route("**/*", _guard)
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
        try:
            await page.wait_for_load_state("networkidle", timeout=8_000)
        except Exception:  # noqa: BLE001 - hay sitios que nunca quedan quietos (chats, analítica)
            pass
        await page.wait_for_timeout(SETTLE_MS)
        data = await page.evaluate(_EXTRACT)
        shot = await page.screenshot(type="jpeg", quality=70, full_page=False) if screenshot else None
        return {"url": page.url, "status": resp.status if resp else None, **data, "screenshot": shot}
    finally:
        await page.close()


async def render(url: str, subpages: int = MAX_SUBPAGES) -> dict | None:
    """La página como la ve una persona, más hasta `subpages` secciones internas. None si no hay navegador."""
    if not available():
        return None
    from playwright.async_api import async_playwright

    await ensure_public_url(url)
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
            try:
                context = await browser.new_context(viewport=VIEWPORT, user_agent=UA, locale="es-CO",
                                                    java_script_enabled=True, ignore_https_errors=False)
                main = await _open(context, url, screenshot=True)
                host = urlparse(main["url"]).hostname
                seen = {main["url"].split("#")[0].rstrip("/")}
                internal = []
                for label, href in main.get("links", []):
                    clean = href.split("#")[0].rstrip("/")
                    if urlparse(href).hostname == host and clean not in seen and len(internal) < 15:
                        seen.add(clean)
                        internal.append((label[:60], clean))
                subs = []
                if subpages and internal:
                    results = await asyncio.gather(*(_open(context, h, screenshot=False) for _, h in internal[:subpages]),
                                                   return_exceptions=True)
                    subs = [r for r in results if isinstance(r, dict)]
                return {"main": main, "internal": internal, "subpages": subs}
            finally:
                await browser.close()
    except BlockedURLError:
        raise
    except Exception as e:  # noqa: BLE001 - el navegador puede fallar por mil razones; se informa y se sigue
        log.warning("navegador_fallo", extra={"url": url, "error": str(e)[:300]})
        return {"error": f"el navegador no pudo abrir la página ({type(e).__name__})"}


def merge(base: dict, rendered: dict, vision: str = "") -> dict:
    """Une lo que dio el HTML con lo que se vio en el navegador."""
    main = rendered["main"]
    text = main.get("text") or ""
    for sub in rendered.get("subpages", []):
        if sub.get("text"):
            text += f"\n\n--- Sección {sub['url']} ---\n{sub['text']}"
    out = {**base, "url": main.get("url") or base.get("url"), "titulo": base.get("titulo") or main.get("title", ""),
           "encabezados": main.get("heads") or base.get("encabezados", []), "texto": text[:MAX_TEXT],
           "botones": main.get("buttons", []), "formularios": main.get("forms", []),
           "enlaces": [f"{label} → {href}" for label, href in rendered.get("internal", [])] or base.get("enlaces", []),
           "logos": list(dict.fromkeys((main.get("logos") or []) + (base.get("logos") or [])))[:5],
           "navegador": True}
    out.pop("aviso", None)
    if vision:
        out["pantalla"] = vision
    if len(out["texto"]) < 200 and not vision:
        out["aviso"] = "Incluso en el navegador la página mostró muy poco texto; puede pedir inicio de sesión."
    return out
