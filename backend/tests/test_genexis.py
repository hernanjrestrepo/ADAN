"""Genexis construye el MVP de verdad y la graduación cierra el proceso."""
import json

from app.ai.base import LLMAdapter, LLMResponse
from app.core.config import settings
from tests.test_discovery import _setup, _use

PAGE = ('<!DOCTYPE html><html><body><img src="{{LOGO}}"><h1>Zentrip</h1><section id="contacto"><!--FORMULARIO-->'
        '</section></body></html>')


class Builder(LLMAdapter):
    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048):
        for piece in ("```html\n", PAGE[:40], PAGE[40:], "\n```"):
            yield piece

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        return LLMResponse(content="# Especificación\n\n- Como viajero quiero…", model="fake")

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        data = {"resumen_ejecutivo": "Empresa lista.", "frase": "¡Lo lograste!",
                "plan_90_dias": [{"periodo": "Días 1-30", "objetivo": "Primeras ventas", "acciones": ["Lanzar"]}],
                "kpis": [{"nombre": "Viajes vendidos", "meta": 5, "unidad": "viajes", "frecuencia": "mensual"}]}
        return LLMResponse(content=json.dumps(data), model="fake", parsed=data)

    async def generate(self, *a, **k):
        return LLMResponse(content="", model="fake")

    async def health_check(self):
        return True

    def list_models(self):
        return []


def test_genexis_builds_a_sandboxed_landing_that_captures_leads_with_consent(client):
    cid, h = _setup(client, "genexis@example.com")
    _use(client, Builder())
    assert client.post(f"/api/v1/genexis/{cid}/especificacion", headers=h).json()["especificacion"]["markdown"].startswith("# Esp")
    assert client.post(f"/api/v1/genexis/{cid}/sitio", headers=h, json={"tipo": "landing"}).json()["sitios"]["landing"]["estado"] == "construyendo"
    url = client.get(f"/api/v1/genexis/{cid}", headers=h).json()["sitios"]["landing"]["url"]
    page = client.get(url)
    assert page.status_code == 200 and "sandbox" in page.headers["content-security-policy"]
    assert "Ley 1581" in page.text and "{{LOGO}}" not in page.text and "<!--FORMULARIO-->" not in page.text
    slug = url.rsplit("/", 1)[1]
    no = client.post(f"/api/v1/sitio/{slug}/interes", data={"nombre": "Ana", "correo": "ana@example.com"})
    assert no.status_code == 422  # sin autorización no se guarda
    ok = client.post(f"/api/v1/sitio/{slug}/interes", data={"nombre": "Ana", "correo": "ana@example.com", "autorizo": "si"})
    assert ok.status_code == 200 and "Gracias" in ok.text
    leads = client.get(f"/api/v1/genexis/{cid}/interesados", headers=h).json()
    assert leads[0]["correo"] == "ana@example.com"
    assert client.get(f"/api/v1/genexis/{cid}/interesados.csv", headers=h).text.count("ana@example.com") == 1
    other = _setup(client, "otro-genexis@example.com")[1]
    assert client.get(f"/api/v1/genexis/{cid}/interesados", headers=other).status_code == 404
    z = client.get(f"/api/v1/genexis/{cid}/codigo.zip", headers=h)
    assert z.status_code == 200 and z.content[:2] == b"PK"


def test_the_prototype_needs_approval_and_apples(client, monkeypatch):
    monkeypatch.setattr(settings, "PARADIXE_SUPERADMINS", "jefe@paradixe.xyz")
    cid, h = _setup(client, "proto@example.com")
    _use(client, Builder())
    r = client.post(f"/api/v1/genexis/{cid}/sitio", headers=h, json={"tipo": "prototipo"})
    assert r.status_code == 402 and "@pples" in r.json()["detail"]
    price = client.get(f"/api/v1/genexis/{cid}", headers=h).json()["precio_prototipo"]
    admin = _setup(client, "jefe@paradixe.xyz")[1]
    uid = next(u["id"] for u in client.get("/api/v1/admin/usuarios?q=proto", headers=admin).json())
    client.post(f"/api/v1/admin/usuarios/{uid}/regalo", headers=admin, json={"apples": price + 5, "reason": "pruebas"})
    client.post(f"/api/v1/genexis/{cid}/sitio", headers=h, json={"tipo": "prototipo", "aprobar_apples": True})
    assert client.get(f"/api/v1/genexis/{cid}", headers=h).json()["sitios"]["prototipo"]["url"]


def test_closing_level_seven_graduates_the_company(client, db_session):
    from tests.test_levels import _open_level
    cid, h = _setup(client, "graduacion@example.com")
    _use(client, Builder())
    _open_level(db_session, cid, 7)
    client.get(f"/api/v1/nivel/7/{cid}/status", headers=h)
    assert client.post(f"/api/v1/empresa/{cid}/graduacion", headers=h).status_code == 409  # aún sin cerrar el 7
    client.post(f"/api/v1/nivel/7/{cid}/cerrar", headers=h, json={"reason": "Cerramos para operar en modo continuo"})
    st = client.get(f"/api/v1/empresa/{cid}/graduacion", headers=h).json()
    assert st["graduada"] and st["certificado"].startswith("ADAN-") and st["libro"]["markdown"].startswith("# Libro de la Empresa")
    assert st["kpis"][0]["nombre"] == "Viajes vendidos"
    entry = client.post(f"/api/v1/empresa/{cid}/seguimiento", headers=h, json={"valores": {"Viajes vendidos": 3}}).json()
    assert entry["valores"] == {"Viajes vendidos": 3.0}
    lib = client.get(f"/api/v1/empresa/{cid}/biblioteca", headers=h).json()
    assert any(d["tipo"] == "Libro de la Empresa" for d in lib["documentos"])
