"""ADÁN abre las páginas web que el fundador pega en el chat."""
import httpx
import pytest

from app.documents import web
from tests.test_discovery import TURN_1, ScriptLLM, _setup, _use

HTML = """<html><head><title>Xmart Travel</title><meta name="description" content="Viajes en familia sin enredos">
<script>var x = 1;</script></head><body><nav><a href="/planes">Planes</a> <a href="https://otro.com">Fuera</a></nav>
<h1>Viaja todo incluido</h1><p>Un solo pago para vuelos, hotel y tours.</p><h2>Precios</h2><p>Desde 2.500.000 COP.</p></body></html>"""


def test_find_urls_with_and_without_scheme():
    text = "Mira https://xmart.travel/planes, y también www.competidor.com.co y ceo@paradixe.xyz. Repito https://xmart.travel/planes"
    assert web.find_urls(text) == ["https://xmart.travel/planes", "https://www.competidor.com.co"]


def test_parse_html_reads_title_text_and_internal_links():
    page = web.parse_html(HTML, "https://xmart.travel/")
    assert page["titulo"] == "Xmart Travel" and page["descripcion"] == "Viajes en familia sin enredos"
    assert "H1: Viaja todo incluido" in page["encabezados"] and "Un solo pago" in page["texto"]
    assert "var x" not in page["texto"] and page["enlaces"] == ["Planes → https://xmart.travel/planes"]


@pytest.mark.asyncio
async def test_fetch_page_and_blocked_addresses():
    transport = httpx.MockTransport(lambda req: httpx.Response(200, text=HTML, headers={"content-type": "text/html"}))
    async with httpx.AsyncClient(transport=transport) as client:
        page = await web.fetch_page("https://xmart.travel/", client)
    assert page["titulo"] == "Xmart Travel" and "Desde 2.500.000 COP" in web.as_markdown(page)
    assert (await web.fetch_page("http://127.0.0.1:8000/admin"))["error"] == "la dirección no es pública"


def test_the_team_reads_a_shared_link_in_the_chat(client, monkeypatch):
    async def fake_fetch_all(urls):
        return [{"url": urls[0], **web.parse_html(HTML, urls[0])}]
    monkeypatch.setattr(web, "fetch_all", fake_fetch_all)
    cid, h = _setup(client, "web@example.com")
    llm = _use(client, ScriptLLM([TURN_1]))
    client.post(f"/api/v1/nivel1/{cid}/chat", headers=h, json={"message": "Esta es mi página: xmart.travel"})
    system = llm.calls[0][0].content
    assert "ABRISTE LAS PÁGINAS" in system and "Un solo pago para vuelos" in system
    lib = client.get(f"/api/v1/empresa/{cid}/biblioteca", headers=h).json()
    assert any(d["tipo"] == "Página web leída" and "Xmart Travel" in d["titulo"] for d in lib["documentos"])


@pytest.mark.asyncio
async def test_a_javascript_page_is_opened_in_the_real_browser(monkeypatch):
    from app.documents import media, navegador

    async def fake_render(url, subpages=3):
        return {"main": {"url": url, "status": 200, "title": "Xmart Travel", "text": "Cuéntale a Aura el viaje que sueñas. " * 20,
                         "heads": ["H1: Cuéntale a Aura"], "buttons": ["Conversar con Aura", "Vuelos"], "forms": ["Escribe tu viaje"],
                         "links": [], "screenshot": b"jpeg"}, "internal": [], "subpages": []}

    async def fake_ocr(data, mime, prompt=None):
        assert "captura de una página web" in prompt
        return "Portada con foto de San Andrés y un chat con Aura."
    monkeypatch.setattr(navegador, "available", lambda: True)
    monkeypatch.setattr(navegador, "render", fake_render)
    monkeypatch.setattr(media, "can_see", lambda: True)
    monkeypatch.setattr(media, "ocr_image", fake_ocr)
    shell = {"url": "https://xmartravel.com/", "titulo": "Xmart Travel", "descripcion": "Viaja mejor", "encabezados": [],
             "texto": "", "enlaces": [], "aviso": "casi no tiene texto"}
    page = await web.see(shell)
    md = web.as_markdown(page)
    assert page["navegador"] and "aviso" not in page
    assert "Conversar con Aura" in md and "San Andrés" in md and "Cuéntale a Aura" in md


def test_pages_already_read_are_remembered_and_not_reopened(client, monkeypatch):
    calls = []

    async def fake_fetch_all(urls):
        calls.append(urls)
        return [{"url": urls[0], **web.parse_html(HTML, urls[0])}]
    monkeypatch.setattr(web, "fetch_all", fake_fetch_all)
    cid, h = _setup(client, "memoria-web@example.com")
    llm = _use(client, ScriptLLM([TURN_1] * 6))
    client.post(f"/api/v1/nivel1/{cid}/chat", headers=h, json={"message": "Revisa https://xmart.travel/"})
    client.post(f"/api/v1/nivel1/{cid}/chat", headers=h, json={"message": "Otra vez https://xmart.travel/"})
    assert len(calls) == 1  # la segunda vez usa lo que ya leyó hace un momento
    client.post(f"/api/v1/nivel1/{cid}/chat", headers=h, json={"message": "¿Qué te pareció el precio?"})
    assert "YA ABRISTE" in llm.calls[-1][0].content and "Un solo pago para vuelos" in llm.calls[-1][0].content


def test_the_logo_found_on_the_site_is_offered_and_adopted(client, monkeypatch):
    from app.empresa import logo_externo

    page_html = HTML.replace("<title>", '<link rel="apple-touch-icon" href="/icon.png"><title>').replace(
        "<h1>", '<img src="/img/logo-xmart.svg" alt="Xmart"><h1>')

    async def fake_fetch_all(urls):
        return [{"url": urls[0], **web.parse_html(page_html, urls[0])}]

    async def fake_download(url):
        assert url == "https://xmart.travel/img/logo-xmart.svg"
        return b'<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#0f766e"/><circle fill="#f59e0b"/><path fill="#fff"/></svg>', "image/svg+xml"
    monkeypatch.setattr(web, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(logo_externo, "download", fake_download)
    cid, h = _setup(client, "logo-web@example.com")
    _use(client, ScriptLLM([TURN_1]))
    msg = client.post(f"/api/v1/nivel1/{cid}/chat", headers=h, json={"message": "Mira https://xmart.travel/"}).json()["message"]
    suggested = msg["metadata_json"]["logo_sugerido"]["url"]
    assert suggested == "https://xmart.travel/img/logo-xmart.svg"
    res = client.post(f"/api/v1/empresa/{cid}/marca/logo-actual", headers=h, json={"url": suggested}).json()
    assert res["identidad"]["logo"].startswith("data:image/svg+xml;base64,") and res["identidad"]["color"] == "#0f766e"
    lib = client.get(f"/api/v1/empresa/{cid}/biblioteca", headers=h).json()
    assert [p["hex"] for p in lib["marca"]["paleta"]][:2] == ["#0f766e", "#f59e0b"]
