"""Herramientas del equipo: recorrido con clics, revisión de código y sus límites de seguridad."""
from app.documents import recorrido, repositorio
from tests.test_discovery import TURN_1, ScriptLLM, _setup, _use


def test_a_github_link_in_the_chat_gets_a_code_review_from_mateo(client, monkeypatch):
    async def fake_fetch(url, llm, goal, token=""):
        assert token == ""
        return {"repo": "paradixe/xmart", "rama": "main", "descripcion": "", "lenguaje": "TypeScript", "privado": False,
                "archivos_totales": 120, "arbol": ["src/app.tsx"], "archivos": {"src/app.tsx": "export default 1"}}

    async def fake_review(llm, data, goal, context=""):
        return "El checkout llama a Wompi desde el servidor: bien hecho."
    monkeypatch.setattr(repositorio, "fetch", fake_fetch)
    monkeypatch.setattr(repositorio, "review", fake_review)
    cid, h = _setup(client, "repo@example.com")
    llm = _use(client, ScriptLLM([TURN_1]))
    msg = client.post(f"/api/v1/nivel1/{cid}/chat", headers=h,
                      json={"message": "Este es el código: https://github.com/paradixe/xmart"}).json()["message"]
    assert msg["metadata_json"]["trabajando"]["tipo"] == "repositorio"
    assert "Mateo (CTO) ya lo está leyendo" in llm.calls[0][0].content
    msgs = client.get(f"/api/v1/nivel1/{cid}/status", headers=h).json()["messages"]
    assert msgs[-1]["agent_name"] == "Mateo · CTO" and "Wompi desde el servidor" in msgs[-1]["content"]
    lib = client.get(f"/api/v1/empresa/{cid}/biblioteca", headers=h).json()
    assert any(d["tipo"] == "Revisión de código" for d in lib["documentos"])


def test_a_walk_with_the_founders_account_never_keeps_the_password(client, monkeypatch):
    seen = {}

    async def fake_walk(llm, url, goal, user="", password=""):
        seen.update(user=user, password=password)
        return {"steps": [{"paso": 1, "accion": "escribir", "nota": f"Entré con la clave {password}", "url": url},
                          {"paso": 2, "accion": "fin", "nota": "Llegué al checkout de Wompi y me detuve", "url": url}],
                "final": {"url": url, "texto": "Total a pagar", "screenshot": None}}
    monkeypatch.setattr(recorrido, "walk", fake_walk)
    cid, h = _setup(client, "recorrido@example.com")
    _use(client, ScriptLLM([TURN_1]))
    res = client.post(f"/api/v1/herramientas/{cid}/recorrido", headers=h, json={
        "url": "https://xmart.travel", "objetivo": "llegar al pago", "usuario": "demo@xmart.travel", "clave": "S3creta!", "nivel": 1})
    assert res.json()["started"] is True and seen == {"user": "demo@xmart.travel", "password": "S3creta!"}
    msgs = client.get(f"/api/v1/nivel1/{cid}/status", headers=h).json()["messages"]
    assert all("S3creta!" not in m["content"] for m in msgs)
    assert msgs[-1]["agent_name"] == "Andrés · Producto"


def test_card_numbers_and_payment_buttons_are_hard_stops():
    assert recorrido._CARD.search("4242424242424242") and recorrido._PAY_WORDS.search("Confirmar pago")
    assert not recorrido._PAY_WORDS.search("Ver planes")


def test_repo_urls_are_parsed_and_bad_ones_rejected():
    assert repositorio.parse("https://github.com/paradixe/xmart.git") == ("paradixe", "xmart")
    try:
        repositorio.parse("https://gitlab.com/x/y")
        raise AssertionError("debía fallar")
    except repositorio.RepoError:
        pass
