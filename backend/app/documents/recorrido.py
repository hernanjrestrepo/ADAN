"""Recorridos con clics: ADAN navega una página como un usuario (clic, escribir, enviar) para llegar a un objetivo
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

MAX_STEPS = 14
_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_PAY_WORDS = re.compile(r"\b(pagar|pague|paga ahora|confirmar (?:el )?pago|comprar ahora|finalizar compra|place order|pay now)\b", re.I)

# Elementos con los que se puede interactuar, numerados para que la IA los nombre por su número
_ELEMENTS = """() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const clean = (t) => (t || '').replace(/\\s+/g, ' ').trim().slice(0, 80);
  // Primero lo que está en un panel abierto (diálogo, chat flotante, capa fija) y lo que se ve en pantalla
  const overlay = (e) => { for (let n = e; n && n !== document.body; n = n.parentElement) {
    const st = getComputedStyle(n); if (n.getAttribute('role') === 'dialog' || n.getAttribute('aria-modal') === 'true'
      || st.position === 'fixed' || st.position === 'sticky') return 1; } return 0; };
  const inView = (e) => { const r = e.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight ? 1 : 0; };
  const all = [...document.querySelectorAll('a[href],button,[role=button],input,textarea,select,[contenteditable=true]')].filter(vis);
  const els = all.map((e, k) => [e, overlay(e) * 2 + inView(e), k]).sort((x, y) => y[1] - x[1] || x[2] - y[2]).map((x) => x[0]).slice(0, 60);
  window.__adan = els;
  return els.map((e, i) => ({ i, tag: e.tagName.toLowerCase(), type: e.type || '',
    label: clean(e.getAttribute('aria-label') || e.getAttribute('placeholder') || e.innerText || e.getAttribute('name') || e.title),
    value: (e.tagName === 'INPUT' || e.tagName === 'TEXTAREA') ? clean(e.value) : (e.isContentEditable ? clean(e.innerText) : '') }));
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
    "Si un campo ya contiene tu texto, NO lo escribas otra vez: envíalo con `enter` o con el botón de enviar. Si "
    "escribes en un chat, espera su respuesta (`esperar`) antes de seguir. "
    "`nota`: qué ves y qué haces, en una frase. NUNCA escribas datos de tarjeta ni confirmes un pago: si llegas a la "
    "pantalla de pago, descríbela y termina con `fin`.\n"
    "`texto` es lo que TÚ escribes (el mensaje completo), nunca la etiqueta del campo. Ejemplo para un chat: "
    "{\"accion\": \"escribir\", \"indice\": 0, \"texto\": \"Hola, quiero un viaje de 4 noches a Cartagena para 2 "
    "personas\", \"nota\": \"Le escribo al chat lo que pide el objetivo\"}. Para un campo de texto vacío usa `escribir` "
    "directamente (no hace falta hacer clic antes)."
)


async def _act(page, action: str, idx: int, value: str) -> None:
    """Hace la acción sobre el elemento número `idx`. Si no se deja llenar (chats con editores propios), hace clic y
    escribe con el teclado, como una persona."""
    if action == "enter":
        await page.keyboard.press("Enter")
        return
    element = (await page.evaluate_handle(f"() => window.__adan[{idx}]")).as_element()
    if element is None:
        raise LookupError("elemento")
    await element.scroll_into_view_if_needed(timeout=3000)
    if action == "clic":
        try:
            await element.click(timeout=5000)
        except Exception:  # noqa: BLE001 - algo lo tapa: clic por JavaScript
            await element.evaluate("(e) => e.click()")
        return
    try:
        await element.fill(value, timeout=4000)
    except Exception:  # noqa: BLE001
        await element.click(timeout=4000)
        await page.keyboard.press("Control+A")
        await page.keyboard.type(value, delay=15)


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
                    # Formulario de clave (entrar o crear cuenta) sin cuenta de prueba: se detiene, nunca inventa una
                    if not user and any(e["type"] == "password" for e in elements):
                        steps.append({"paso": n + 1, "accion": "fin", "url": page.url,
                                      "nota": "La página pide entrar o crear una cuenta. Me detengo: para seguir, dame "
                                              "una cuenta de prueba en «🧭 Recorrer una página»."})
                        break
                    text = (await page.evaluate("() => document.body ? document.body.innerText : ''"))[:3000]
                    listing = "\n".join(f"[{e['i']}] {e['tag']}{'/' + e['type'] if e['type'] else ''}: {e['label']}"
                                        + (f" (ya contiene: «{e['value']}»)" if e.get('value') else "") for e in elements)
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
                        steps[-1]["nota"] += " — me detengo: ese botón confirma un pago y ADAN nunca paga."
                        break
                    # Si la IA puso la etiqueta del campo (o nada) como texto, se escribe lo que pide el objetivo
                    if (action == "escribir" and target and target["type"] not in ("email", "password", "tel")
                            and (not typed.strip() or typed.strip().lower() == target["label"].lower())):
                        typed = goal
                    value = typed.replace("{{usuario}}", user).replace("{{clave}}", password)
                    if action == "escribir" and _CARD.search(value.replace(" ", "")):
                        steps[-1]["nota"] += " — no escribo números de tarjeta."
                        break
                    # Escribir dos veces seguidas en el mismo campo = ya está escrito: se envía
                    prev = steps[-2] if len(steps) > 1 else None
                    if action == "escribir" and prev and prev.get("accion") == "escribir" and prev.get("indice") == idx:
                        action = "enter"
                        steps[-1]["accion"] = "enter"
                    steps[-1]["indice"] = idx
                    try:
                        await _act(page, action, idx, value)
                    except Exception as e:  # noqa: BLE001 - una acción que falla se anota y se sigue con otra
                        steps[-1]["nota"] += f" (no funcionó: {type(e).__name__}; pruebo otra cosa)"
                    # Tras enviar, los chats tardan en responder: se les da más tiempo
                    await page.wait_for_timeout(7000 if action == "enter" else 2500)
                final = {"url": page.url,
                         "texto": (await page.evaluate("() => document.body ? document.body.innerText : ''"))[:6000],
                         "screenshot": await page.screenshot(type="jpeg", quality=70)}
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
