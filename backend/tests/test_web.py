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
