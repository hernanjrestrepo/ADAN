"""Constitución de la empresa: nombre, dominios (RDAP), ruta legal por país y estatutos."""
import io
import json

import httpx
import pytest

from app.ai.base import LLMAdapter, LLMMessage, LLMResponse
from app.ai.kimi_adapter import KimiAdapter
from app.constitucion import dominios
from tests.test_discovery import _setup, _use

NAME = {"veredicto": "conflicto", "explicacion": "Ya existe una panadería con ese nombre en Bogotá.",
        "coincidencias": [{"nombre": "Masa Madre SAS", "tipo": "empresa", "donde": "Bogotá", "fuente": "https://www.rues.org.co"}],
        "registros_oficiales": [{"nombre": "RUES", "url": "https://www.rues.org.co", "que_verificar": "Razón social"}],
        "alternativas": ["Masa Viva", "Horno del Barrio"]}

STEP = {"titulo": "Registro en la Cámara de Comercio", "que_es": "Inscribir la empresa para que exista legalmente.",
        "donde": "Cámara de Comercio", "url": "https://www.ccb.org.co", "documentos": ["Estatutos", "Cédula"],
        "costo": "COP 400.000 aprox.", "tiempo": "1 a 3 días", "errores_comunes": ["Nombre ya registrado"]}
GUIDE = {"pais": "Colombia", "resumen": "Te conviene una S.A.S.",
         "tipos_sociedad": [{"nombre": "S.A.S.", "para_quien": "Casi todos", "ventajas": ["Flexible"], "desventajas": ["Ninguna grave"],
                             "socios": "1 o más", "responsabilidad": "Limitada a los aportes"}],
         "recomendada": {"nombre": "S.A.S.", "por_que": "Un solo socio y responsabilidad limitada."},
         "regimenes": [{"nombre": "Régimen Simple", "quien_puede": "Ingresos bajos", "como_funciona": "Un solo pago",
                        "conviene_si": "Vendes poco al inicio"}],
         "regimen_recomendado": {"nombre": "Régimen Simple", "por_que": "Menos trámites."},
         "pasos": [STEP, {**STEP, "titulo": "RUT ante la DIAN"}], "obligaciones": ["Facturación electrónica"],
         "costo_total": "COP 1,5 millones", "tiempo_total": "2 a 4 semanas",
         "fuentes": [{"nombre": "DIAN", "url": "https://www.dian.gov.co"}]}


class LegalLLM(LLMAdapter):
    """Investiga con chat (sin búsqueda) y estructura según el esquema que le pidan."""

    def __init__(self):
        self.prompts = []

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        self.prompts.append(messages[-1].content)
        if "estatutos" in messages[-1].content:
            return LLMResponse(content="# Estatutos de Masa Viva S.A.S.\n\n## Capítulo I\n\n**Artículo 1.** Nombre: [COMPLETAR: razón social]",
                               model="fake")
        return LLMResponse(content="Investigación: hallazgos con fuentes", model="fake")

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        data = GUIDE if "pasos" in schema["properties"] else NAME
        return LLMResponse(content=json.dumps(data), model="fake", parsed=data)

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048):
        raise AssertionError

    async def health_check(self):
        return True

    def list_models(self):
        return []


def test_slug_keeps_only_valid_domain_characters():
    assert dominios.slugify("Panadería Masa & Madre!") == "panaderiamasaymadre"


@pytest.mark.asyncio
async def test_domains_are_checked_with_rdap():
    taken = {"masaviva.com", "masaviva.co"}

    def handler(request: httpx.Request):
        domain = request.url.path.rsplit("/", 1)[-1]
        if request.url.host == "rdap.org":  # rdap.org redirige al registro de cada extensión, salvo .io
            if domain.endswith(".io"):
                return httpx.Response(404)
            return httpx.Response(302, headers={"Location": f"https://registro.example/domain/{domain}"})
        if request.url.host == "dns.google":
            name = request.url.params["name"]
            return httpx.Response(200, json={"Status": 3} if name.endswith(".io") else {"Status": 2})
        if domain.endswith(".shop"):
            return httpx.Response(503)
        return httpx.Response(200 if domain in taken else 404, json={})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=True)
    result = await dominios.check("Masa Viva", client)
    status = {d["domain"]: d["status"] for d in result["domains"]}
    assert status["masaviva.com"] == "registrado" and status["masaviva.com.co"] == "disponible"
    assert status["masaviva.shop"] == "sin_confirmar"
    # Un 404 del propio rdap.org (extensión sin RDAP) no es "libre": se pregunta al DNS, y NXDOMAIN es solo una pista
    assert status["masaviva.io"] == "probable_libre"
    # Los enlaces de compra llevan el primer dominio libre
    assert all("masaviva.com.co" in r["url"] for r in result["registrars"])
    assert "Confírmalos" in result["prices_note"]


def test_name_check_reports_conflicts_and_domains(client, monkeypatch):
    async def fake_check(name, client=None):
        return {"slug": "masamadre", "domains": [{"domain": "masamadre.co", "status": "disponible"}], "registrars": []}
    monkeypatch.setattr(dominios, "check", fake_check)
    cid, headers = _setup(client, "nombre@example.com")
    llm = _use(client, LegalLLM())
    body = client.post(f"/api/v1/constitucion/{cid}/nombre", json={"name": "Masa Madre", "country": "Colombia"},
                       headers=headers).json()
    assert body["veredicto"] == "conflicto" and body["alternativas"][0] == "Masa Viva"
    assert body["searched"] is False  # sin búsqueda web no se presenta como verificado
    assert body["domains"][0]["status"] == "disponible"
    assert "Masa Madre" in llm.prompts[0] and "Colombia" in llm.prompts[0]


def test_legal_guide_by_country_with_steps_to_check(client):
    cid, headers = _setup(client, "guia@example.com")
    _use(client, LegalLLM())
    guide = client.post(f"/api/v1/constitucion/{cid}/guia", json={"country": "Colombia"}, headers=headers).json()
    assert guide["recomendada"]["nombre"] == "S.A.S." and len(guide["pasos"]) == 2 and guide["done"] == [False, False]
    assert "abogado" in guide["disclaimer"]
    marked = client.post(f"/api/v1/constitucion/{cid}/guia/pasos/1", json={"done": True}, headers=headers).json()
    assert marked["done"] == [False, True]
    assert client.get(f"/api/v1/constitucion/{cid}/guia", headers=headers).json()["done"] == [False, True]
    assert client.post(f"/api/v1/constitucion/{cid}/guia/pasos/9", json={"done": True}, headers=headers).status_code == 404


def test_statutes_are_drafted_and_downloadable_in_word(client):
    cid, headers = _setup(client, "estatutos@example.com")
    llm = _use(client, LegalLLM())
    body = client.post(f"/api/v1/constitucion/{cid}/estatutos", headers=headers, json={
        "pais": "Colombia", "tipo": "S.A.S.", "nombre": "Masa Viva S.A.S.", "capital": "COP 10.000.000",
        "socios": [{"nombre": "Hernán Restrepo", "porcentaje": 100}]}).json()
    assert body["markdown"].startswith("# Estatutos") and "[COMPLETAR" in body["markdown"]
    assert "Hernán Restrepo" in llm.prompts[0] and "Ley" not in body["title"]
    resp = client.get(f"/api/v1/constitucion/{cid}/estatutos/{body['id']}.docx", headers=headers)
    assert resp.status_code == 200
    from docx import Document as Docx
    text = "\n".join(p.text for p in Docx(io.BytesIO(resp.content)).paragraphs)
    assert "Artículo 1." in text and "Capítulo I" in text


def test_constitution_of_another_company_is_off_limits(client):
    cid, _ = _setup(client, "constduena@example.com")
    _, other = _setup(client, "constintrusa@example.com")
    _use(client, LegalLLM())
    assert client.post(f"/api/v1/constitucion/{cid}/guia", json={"country": "Colombia"}, headers=other).status_code == 404


@pytest.mark.asyncio
async def test_kimi_searches_the_web_and_charges_each_search(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "KIMI_API_KEY", "sk-prueba")
    calls = []

    def handler(request: httpx.Request):
        body = json.loads(request.content)
        calls.append(body)
        if len(calls) == 1:
            return httpx.Response(200, json={"choices": [{"finish_reason": "tool_calls", "message": {
                "role": "assistant", "content": "", "tool_calls": [{"id": "t1", "type": "builtin_function",
                                                                     "function": {"name": "$web_search", "arguments": "{\"q\": \"RUES\"}"}}]}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 10}})
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": "Encontré dos empresas."}}],
                                         "usage": {"prompt_tokens": 200, "completion_tokens": 50}})

    kimi = KimiAdapter(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    resp = await kimi.chat_search([LLMMessage("user", "¿Existe Masa Viva?")])
    assert resp.content == "Encontré dos empresas." and resp.metadata == {**resp.metadata, "searched": True, "searches": 1}
    assert calls[0]["tools"][0]["function"]["name"] == "$web_search"
    assert calls[1]["messages"][-1]["role"] == "tool"
    assert resp.cost_usd == pytest.approx((300 * 0.95 + 60 * 4.0) / 1_000_000 + 0.004)


@pytest.mark.asyncio
async def test_kimi_is_asked_to_continue_when_it_only_announces_a_search(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "KIMI_API_KEY", "sk-prueba")
    replies = iter([
        {"finish_reason": "stop", "message": {"content": "Voy a hacer una búsqueda más específica:"}},
        {"finish_reason": "tool_calls", "message": {"role": "assistant", "content": "", "tool_calls": [
            {"id": "t1", "type": "builtin_function", "function": {"name": "$web_search", "arguments": "{}"}}]}},
        {"finish_reason": "stop", "message": {"content": "Respuesta final completa con fuentes: https://www.rues.org.co " * 20}},
    ])
    sent = []

    def handler(request: httpx.Request):
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [next(replies)], "usage": {}})

    kimi = KimiAdapter(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    resp = await kimi.chat_search([LLMMessage("user", "¿Existe Masa Viva?")])
    assert resp.content.startswith("Respuesta final completa") and resp.metadata["searches"] == 1
    assert "Continúa" in sent[1]["messages"][-1]["content"]
