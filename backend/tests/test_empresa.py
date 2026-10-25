"""Construcción de la empresa: Expediente de creación por país, validación de documentos y marca."""
import json

from app.ai.base import LLMAdapter, LLMResponse
from tests.test_discovery import _setup, _use


class BrandLLM(LLMAdapter):
    def __init__(self):
        self.prompts = []

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        self.prompts.append(messages[-1].content)
        props = schema["properties"]
        if "nombres" in props:
            data = {"nombres": [
                {"nombre": "Viajo", "tipo": "evocador", "por_que": "Corto y directo", "sonido": "cálido",
                 "fluidez": 5, "memorabilidad": 4, "distintividad": 3},
                {"nombre": "Zentrip", "tipo": "inventado", "por_que": "Calma al viajar", "sonido": "moderno",
                 "fluidez": 4, "memorabilidad": 5, "distintividad": 5}]}
        elif "conceptos" in props:
            data = {"conceptos": [{"nombre_concepto": "Brújula", "estilo": "icono_texto", "icono": "Compass",
                                   "tipografia": "Poppins", "primario": "#0f766e", "acento": "#f59e0b", "fondo": "#ffffff",
                                   "por_que": "Confianza y rumbo"},
                                  {"nombre_concepto": "Raro", "estilo": "nada", "icono": "NoExiste", "tipografia": "Comic",
                                   "primario": "azul", "acento": "#123", "fondo": "#000000", "por_que": "x"}]}
        elif "slogans" in props:
            data = {"slogans": [{"texto": "Viaja sin enredos", "por_que": "Beneficio claro"}]}
        else:  # validación de un documento
            data = {"valido": True, "tipo_detectado": "Certificado de existencia", "nombre_en_documento": "XMART TRAVEL SAS",
                    "coincide_nombre": True, "numero_identificacion": "901.234.567-8", "fecha": "2026-10-20", "observaciones": []}
        return LLMResponse(content=json.dumps(data), model="fake", parsed=data)

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        self.prompts.append(messages[-1].content)
        return LLMResponse(content="# Paquete\n\n- [ ] Estatutos firmados\n- [ ] Cédulas", model="fake")

    async def generate(self, *a, **k):
        return LLMResponse(content="", model="fake")

    async def health_check(self):
        return True

    def list_models(self):
        return []


def test_the_dossier_depends_on_the_country(client):
    cid, h = _setup(client, "expediente@example.com")
    view = client.get(f"/api/v1/empresa/{cid}/expediente", headers=h).json()
    assert view["pais"] == "OTRO"
    co = client.put(f"/api/v1/empresa/{cid}/expediente/pais", headers=h, json={"pais": "CO"}).json()
    ids = {i["id"]: i for i in co["items"]}
    assert ids["registro_mercantil"]["modo"] == "cliente_presencial" and "rut" in ids and "Certificado de existencia" in ids["registro_mercantil"]["documento"]
    us = client.put(f"/api/v1/empresa/{cid}/expediente/pais", headers=h, json={"pais": "US"}).json()
    assert {"articles", "ein", "operating_agreement"} <= {i["id"] for i in us["items"]}
    marked = client.post(f"/api/v1/empresa/{cid}/expediente/boi/estado", headers=h, json={"estado": "no_aplica", "nota": "Empresa local"}).json()
    assert next(i for i in marked["items"] if i["id"] == "boi")["estado"] == "no_aplica" and marked["hechos"] == 1


def test_adan_prepares_a_procedure_and_validates_the_uploaded_document(client):
    cid, h = _setup(client, "tramite@example.com")
    _use(client, BrandLLM())
    client.put(f"/api/v1/empresa/{cid}/expediente/pais", headers=h, json={"pais": "CO"})
    pack = client.post(f"/api/v1/empresa/{cid}/expediente/registro_mercantil/preparar", headers=h).json()
    assert "Estatutos firmados" in pack["markdown"]
    assert client.get(f"/api/v1/empresa/{cid}/expediente/paquete/{pack['id']}.docx", headers=h).status_code == 200
    text = b"CAMARA DE COMERCIO DE BOGOTA. CERTIFICADO DE EXISTENCIA Y REPRESENTACION LEGAL. XMART TRAVEL SAS NIT 901234567-8"
    res = client.post(f"/api/v1/empresa/{cid}/expediente/registro_mercantil/documento", headers=h,
                      files={"file": ("certificado.txt", text, "text/plain")}).json()
    assert res["validacion"]["valido"] is True
    item = next(i for i in res["expediente"]["items"] if i["id"] == "registro_mercantil")
    assert item["estado"] == "validado" and res["expediente"]["identificacion"]["registro_mercantil"] == "901.234.567-8"


def test_brand_names_logos_and_slogan_build_the_identity(client, monkeypatch):
    from app.constitucion import dominios

    async def fake_check(name, client=None):
        free = name == "Zentrip"
        return {"domains": [{"domain": f"{name.lower()}.com", "status": "disponible" if free else "registrado"}]}
    monkeypatch.setattr(dominios, "check", fake_check)
    cid, h = _setup(client, "marca@example.com")
    llm = _use(client, BrandLLM())
    names = client.post(f"/api/v1/empresa/{cid}/marca/nombres", headers=h, json={"ideas": "calma"}).json()["nombres"]
    assert names[0]["nombre"] == "Zentrip" and names[0]["dominios_libres"] == ["zentrip.com"]  # primero el de dominio libre
    client.post(f"/api/v1/empresa/{cid}/marca/nombre", headers=h, json={"nombre": "Zentrip", "adoptar": True})
    assert client.get(f"/api/v1/companies/{cid}", headers=h).json()["name"] == "Zentrip"
    logos = client.post(f"/api/v1/empresa/{cid}/marca/logos", headers=h).json()["logos"]
    assert logos[0]["icono"] == "Compass" and logos[1]["icono"] == "Sparkles" and logos[1]["primario"] == "#2563eb"
    svg = "data:image/svg+xml;base64,PHN2Zy8+"
    client.post(f"/api/v1/empresa/{cid}/marca/logo", headers=h, json={"concepto": "c1", "imagen": svg})
    company = client.get(f"/api/v1/companies/{cid}", headers=h).json()
    assert company["brand_color"] == "#0f766e" and company["logo"] == svg
    client.post(f"/api/v1/empresa/{cid}/marca/slogans", headers=h)
    client.post(f"/api/v1/empresa/{cid}/marca/slogan", headers=h, json={"texto": "Viaja sin enredos"})
    ident = client.get(f"/api/v1/empresa/{cid}/identidad", headers=h).json()
    assert ident["nombre"] == "Zentrip" and ident["slogan"] == "Viaja sin enredos" and ident["logo"] == svg
    client.post(f"/api/v1/empresa/{cid}/marca/manual", headers=h)
    exp = client.get(f"/api/v1/empresa/{cid}/expediente", headers=h).json()
    states = {i["id"]: i["estado"] for i in exp["items"]}
    assert states["nombre"] == "validado" and states["logo"] == "validado"


def test_camila_builds_the_numbers_inside_the_level_three_room(client, monkeypatch, db_session):
    from app.finanzas.service import Finanzas
    from tests.test_levels import _open_level

    async def fake_org(self, project, ctx):
        return {"resumen": "Equipo pequeño con EVA en ventas.", "moneda": "COP", "roles": []}

    async def fake_model(self, project, ctx):
        rows = [{"mes": m, "caja": 100 - m * 3} for m in range(1, 25)]
        return {"assumptions": {"moneda": "COP"}, "base": {"rows": rows, "kpis": {
            "punto_equilibrio_mes": 14, "capital_necesario": 250000000, "caja_minima": 28, "caja_minima_mes": 24}}}
    monkeypatch.setattr(Finanzas, "org", lambda self, project: None)
    monkeypatch.setattr(Finanzas, "build_org", fake_org)
    monkeypatch.setattr(Finanzas, "build_model", fake_model)
    cid, h = _setup(client, "numeros@example.com")
    _use(client, BrandLLM())
    _open_level(db_session, cid, 3)
    assert client.post(f"/api/v1/empresa/{cid}/numeros", headers=h).json()["kpis"]["punto_equilibrio_mes"] == 14
    msgs = client.get(f"/api/v1/nivel/3/{cid}/status", headers=h).json()["messages"]
    camila = [m for m in msgs if m["agent_name"] == "Camila · CFO"]
    assert camila and "mes 14" in camila[-1]["content"] and "```chart" in camila[-1]["content"]
    states = {i["id"]: i["estado"] for i in client.get(f"/api/v1/empresa/{cid}/expediente", headers=h).json()["items"]}
    assert states["presupuesto"] == "validado" and states["organigrama"] == "validado"


def test_the_library_gathers_brand_palette_and_documents(client, monkeypatch):
    from app.constitucion import dominios

    async def fake_check(name, client=None):
        return {"domains": []}
    monkeypatch.setattr(dominios, "check", fake_check)
    cid, h = _setup(client, "biblioteca@example.com")
    _use(client, BrandLLM())
    client.put(f"/api/v1/empresa/{cid}/expediente/pais", headers=h, json={"pais": "CO"})
    pack = client.post(f"/api/v1/empresa/{cid}/expediente/rut/preparar", headers=h).json()
    client.post(f"/api/v1/empresa/{cid}/marca/logos", headers=h)
    client.post(f"/api/v1/empresa/{cid}/marca/logo", headers=h, json={"concepto": "c1", "imagen": "data:image/svg+xml;base64,PHN2Zy8+"})
    client.post(f"/api/v1/empresa/{cid}/marca/manual", headers=h)
    lib = client.get(f"/api/v1/empresa/{cid}/biblioteca", headers=h).json()
    assert [p["hex"] for p in lib["marca"]["paleta"]] == ["#0f766e", "#f59e0b", "#ffffff"]
    assert lib["marca"]["tipografia"] == "Poppins" and lib["marca"]["manual"] is True
    ids = {d["id"]: d for d in lib["documentos"]}
    assert ids["manual"]["descarga"].endswith("/marca/manual.docx")
    assert ids[pack["id"]]["seccion"] == "legal" and ids[pack["id"]]["legible"] is True
    assert not any(d["tipo"] == "Documento" and d["titulo"] == "Marca de la empresa" for d in lib["documentos"])
    doc = client.get(f"/api/v1/empresa/{cid}/biblioteca/{pack['id']}", headers=h).json()
    assert "Estatutos firmados" in doc["markdown"]
    assert client.get(f"/api/v1/empresa/{cid}/biblioteca/{pack['id']}.docx", headers=h).status_code == 200
    assert client.get(f"/api/v1/empresa/{cid}/biblioteca/manual", headers=h).status_code == 200
    other, h2 = _setup(client, "ajeno@example.com")
    assert client.get(f"/api/v1/empresa/{cid}/biblioteca/{pack['id']}", headers=h2).status_code in (403, 404)
