"""Recorridos con clics: ADÁN navega una página como un usuario (clic, escribir, enviar) para llegar a un objetivo
(«llega hasta el pago», «pide un viaje a Cartagena», «entra con mi cuenta y revisa el panel»).

En cada paso la IA ve la pantalla resumida (texto y elementos con número) y decide la siguiente acción. Reglas
duras que no dependen de la IA:
- Nunca se escriben datos de tarjetas ni se confirma un pago: el recorrido se detiene antes de pagar.
- Usuario y clave, si el fundador los da, se escriben en el navegador desde aquí (la IA solo ve {{usuario}} y
  {{clave}}) y no se guardan en ninguna parte.
- Toda petición del navegador pasa por la protección SSRF.
"""
from __future__ import annotations

import logging
import re

from app.ai.base import LLMAdapter, LLMMessage
from app.core.net import BlockedURLError, ensure_public_url
from app.documents import navegador

log = logging.getLogger(__name__)

MAX_STEPS = 10
_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_PAY_WORDS = re.compile(r"\b(pagar|pague|paga ahora|confirmar (?:el )?pago|comprar ahora|finalizar compra|place order|pay now)\b", re.I)

# Elementos con los que se puede interactuar, numerados para que la IA los nombre por su número
_ELEMENTS = """() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const clean = (t) => (t || '').replace(/\\s+/g, ' ').trim().slice(0, 80);
  const els = [...document.querySelectorAll('a[href],button,[role=button],input,textarea,select,[contenteditable=true]')].filter(vis).slice(0, 60);
  window.__adan = els;
  return els.map((e, i) => ({ i, tag: e.tagName.toLowerCase(), type: e.type || '',
    label: clean(e.innerText || e.value || e.getAttribute('aria-label') || e.getAttribute('placeholder') || e.getAttribute('name') || e.title) }));
}"""

STEP_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["accion", "indice", "texto", "nota"],
    "properties": {
        "accion": {"type": "string", "enum": ["clic", "escribir", "enter", "esperar", "fin"]},
        "indice": {"type": "integer"},
        "texto": {"type": "string"},
        "nota": {"type": "string"},
    },
}

GUIDE = (
    "Navegas una página web como un usuario para cumplir un objetivo. En cada paso ves la URL, el texto visible y los "
    "elementos numerados. Responde la siguiente acción: `clic` (indice), `escribir` (indice y texto; para entrar con "
    "la cuenta del fundador escribe exactamente {{usuario}} o {{clave}}), `enter` (enviar lo escrito), `esperar` (si "
    "la página está cargando o el chat está respondiendo) o `fin` cuando el objetivo esté cumplido o sea imposible. "
    "`nota`: qué ves y qué haces, en una frase. NUNCA escribas datos de tarjeta ni confirmes un pago: si llegas a la "
    "pantalla de pago, descríbela y termina con `fin`."
)


async def walk(llm: LLMAdapter, url: str, goal: str, user: str = "", password: str = "") -> dict:
    """Recorre la página hacia `goal`. Devuelve los pasos, lo que se vio al final y la captura final."""
    if not navegador.available():
        return {"error": "El navegador no está disponible en este servidor."}
    from playwright.async_api import async_playwright

    await ensure_public_url(url)
    steps: list[dict] = []
    final: dict = {}
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
            try:
                context = await browser.new_context(viewport=navegador.VIEWPORT, user_agent=navegador.UA, locale="es-CO")
                page = await context.new_page()
                await page.route("**/*", navegador._guard)
                await page.goto(url, wait_until="domcontentloaded", timeout=navegador.PAGE_TIMEOUT_MS)
                await page.wait_for_timeout(navegador.SETTLE_MS)
                for n in range(MAX_STEPS):
                    elements = await page.evaluate(_ELEMENTS)
                    text = (await page.evaluate("() => document.body ? document.body.innerText : ''"))[:3000]
                    listing = "\n".join(f"[{e['i']}] {e['tag']}{'/' + e['type'] if e['type'] else ''}: {e['label']}"
                                        for e in elements)
                    history = "\n".join(f"{s['paso']}. {s['accion']} → {s['nota']}" for s in steps[-6:])
                    resp = await llm.chat_json([
                        LLMMessage("system", GUIDE),
                        LLMMessage("user", f"Objetivo: {goal}\nTienes cuenta del fundador: {'sí' if user else 'no'}\n"
                                           f"Pasos hechos:\n{history or '(ninguno)'}\n\nURL: {page.url}\n"
                                           f"Texto visible:\n{text}\n\nElementos:\n{listing}"),
                    ], STEP_SCHEMA, temperature=0.2, max_tokens=600)
                    act = resp.parsed if isinstance(resp.parsed, dict) else {"accion": "fin", "indice": 0, "texto": "", "nota": ""}
                    action, idx, typed = act.get("accion"), int(act.get("indice") or 0), str(act.get("texto") or "")
                    steps.append({"paso": n + 1, "accion": action, "nota": str(act.get("nota", ""))[:300], "url": page.url})
                    if action == "fin":
                        break
                    if action == "esperar":
                        await page.wait_for_timeout(3000)
                        continue
                    target = elements[idx] if 0 <= idx < len(elements) else None
                    if action in ("clic", "escribir") and target is None:
                        steps[-1]["nota"] += " (elemento no encontrado)"
                        continue
                    if action == "clic" and _PAY_WORDS.search(target["label"]):
                        steps[-1]["nota"] += " — me detengo: ese botón confirma un pago y ADÁN nunca paga."
                        break
                    handle = await page.evaluate_handle(f"() => window.__adan[{idx}]") if target else None
                    if action == "clic":
                        await handle.as_element().click(timeout=5000)
                    elif action == "escribir":
                        value = typed.replace("{{usuario}}", user).replace("{{clave}}", password)
                        if _CARD.search(value.replace(" ", "")):
                            steps[-1]["nota"] += " — no escribo números de tarjeta."
                            break
                        await handle.as_element().fill(value, timeout=5000)
                        if "{{clave}}" in typed:
                            steps[-1]["nota"] = steps[-1]["nota"].replace(password, "••••") if password else steps[-1]["nota"]
                    elif action == "enter":
                        await page.keyboard.press("Enter")
                    await page.wait_for_timeout(2500)
                final_text = (await page.evaluate("() => document.body ? document.body.innerText : ''"))[:6000]
                shot = await page.screenshot(type="jpeg", quality=70)
                final = {"url": page.url, "texto": final_text, "screenshot": shot}
            finally:
                await browser.close()
    except BlockedURLError:
        return {"error": "La dirección no es pública."}
    except Exception as e:  # noqa: BLE001 - un paso que falla no tumba el turno: se cuenta lo que se alcanzó a ver
        log.warning("recorrido_fallo", extra={"url": url, "error": str(e)[:300]})
        return {"steps": steps, "final": final, "error": f"el recorrido se interrumpió ({type(e).__name__})"}
    for s in steps:  # la clave jamás sale del navegador
        if password:
            s["nota"] = s["nota"].replace(password, "••••")
    return {"steps": steps, "final": final}


def as_markdown(url: str, goal: str, result: dict, vision: str = "") -> str:
    lines = [f"# Recorrido por {url}", f"Objetivo: {goal}", ""]
    for s in result.get("steps", []):
        lines.append(f"{s['paso']}. **{s['accion']}** — {s['nota']}")
    if result.get("error"):
        lines.append(f"\n_Se interrumpió: {result['error']}_")
    final = result.get("final") or {}
    if vision:
        lines.append(f"\n## Pantalla final ({final.get('url', '')})\n{vision}")
    if final.get("texto"):
        lines.append(f"\n## Texto de la pantalla final\n{final['texto'][:4000]}")
    return "\n".join(lines)
