"""Encuestas: ADÁN las diseña, se responden sin cuenta con consentimiento y los resultados se vuelven evidencia."""
import json

from app.ai.base import LLMAdapter, LLMResponse
from tests.test_discovery import _setup, _use

DESIGN = {"titulo": "¿Cómo compras el pan?", "intro": "Somos una panadería de barrio. Queremos entender tu desayuno.",
          "preguntas": [
              {"texto": "¿Compras pan antes de las 7 a. m.?", "tipo": "opcion", "opciones": ["Sí", "No"], "por_que": "Filtro"},
              {"texto": "¿Qué tan grave es no conseguir pan fresco?", "tipo": "escala", "opciones": [], "por_que": "Dolor"},
              {"texto": "¿Cuánto pagas al mes por pan?", "tipo": "numero", "opciones": [], "por_que": "Costo"},
              {"texto": "¿Dónde lo compras?", "tipo": "multiple", "opciones": ["Supermercado", "Panadería", "Tienda"], "por_que": "Alternativas"},
              {"texto": "¿Qué te frustra?", "tipo": "texto", "opciones": [], "por_que": "Abierta"},
              {"texto": "Pregunta rota", "tipo": "opcion", "opciones": ["única"], "por_que": "se vuelve texto"}]}
INSIGHTS = {"resumen": "3 de 3 compran antes de las 7.", "hallazgos": ["3 de 3 compran temprano"], "alertas": ["Muestra pequeña"],
            "evidencia_sugerida": [{"afirmacion": "3 de 3 encuestados compran pan antes de las 7 a. m.", "polaridad": "supports"}]}


class DesignerLLM(LLMAdapter):
    def __init__(self):
        self.prompts = []

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        self.prompts.append(messages[-1].content)
        data = DESIGN if "preguntas" in schema["properties"] else INSIGHTS
        return LLMResponse(content=json.dumps(data), model="fake", parsed=data)

    async def chat(self, *a, **k):
        raise AssertionError

    async def generate(self, *a, **k):
        raise AssertionError

    async def health_check(self):
        return True

    def list_models(self):
        return []


def _survey(client, email):
    cid, headers = _setup(client, email)
    llm = _use(client, DesignerLLM())
    survey = client.post(f"/api/v1/nivel1/{cid}/surveys", json={"objective": "Saber si pagan por pan temprano"},
                         headers=headers).json()
    return cid, headers, llm, survey


def test_adan_designs_the_survey_and_the_public_page_hides_private_data(client):
    cid, headers, llm, survey = _survey(client, "encuesta@example.com")
    assert "Saber si pagan por pan temprano" in llm.prompts[0]
    assert [q["tipo"] for q in survey["preguntas"]] == ["opcion", "escala", "numero", "multiple", "texto", "texto"]
    public = client.get(f"/api/v1/encuestas/{survey['token']}").json()  # sin cuenta
    assert public["titulo"] == "¿Cómo compras el pan?" and all("por_que" not in q for q in public["preguntas"])
    assert "responses" not in public and "objective" not in public
    assert client.get(f"/api/v1/nivel1/{cid}/surveys", headers=headers).json()[0]["responses"] == 0


def test_answers_need_consent_and_are_validated(client):
    _, _, _, survey = _survey(client, "consentimiento@example.com")
    url = f"/api/v1/encuestas/{survey['token']}"
    assert client.post(url, json={"answers": {"q1": "Sí"}, "consent": False}).status_code == 403
    assert client.post(url, json={"answers": {"q1": "Tal vez", "q2": 9}, "consent": True}).status_code == 422
    assert client.post(url, json={"answers": {"q1": "Sí", "q2": 5, "q3": "120000", "q4": ["Panadería", "Inventada"],
                                              "q5": "Que se acaba"}, "consent": True}).status_code == 201
    assert client.post("/api/v1/encuestas/no-existe", json={"answers": {"q1": "Sí"}, "consent": True}).status_code == 404


def test_results_are_counted_and_insights_become_evidence_suggestions(client):
    cid, headers, _, survey = _survey(client, "resultados@example.com")
    url = f"/api/v1/encuestas/{survey['token']}"
    for grave in (5, 4, 5):
        client.post(url, json={"answers": {"q1": "Sí", "q2": grave, "q4": ["Supermercado"]}, "consent": True})
    results = client.get(f"/api/v1/nivel1/{cid}/surveys/{survey['token']}/results", headers=headers).json()
    by_id = {q["id"]: q for q in results["questions"]}
    assert results["responses"] == 3 and by_id["q1"]["counts"] == {"Sí": 3, "No": 0}
    assert by_id["q2"]["average"] == 4.67 and by_id["q4"]["counts"]["Supermercado"] == 3
    insights = client.post(f"/api/v1/nivel1/{cid}/surveys/{survey['token']}/insights", headers=headers).json()
    ev = insights["evidencia_sugerida"][0]
    assert ev["tipo"] == "testimony" and "3 respuestas" in ev["fuente"]
    # La evidencia sugerida se registra con el flujo normal: cuenta como testimonio en el Gate
    assert client.post(f"/api/v1/scoring/{cid}/evidence", headers=headers, json={
        "claim": ev["afirmacion"], "kind": "testimony", "source": ev["fuente"]}).status_code == 201


def test_insights_need_at_least_three_answers_and_a_closed_survey_rejects_answers(client):
    cid, headers, _, survey = _survey(client, "cerrada@example.com")
    assert client.post(f"/api/v1/nivel1/{cid}/surveys/{survey['token']}/insights", headers=headers).status_code == 400
    client.post(f"/api/v1/nivel1/{cid}/surveys/{survey['token']}/open", json={"open": False}, headers=headers)
    resp = client.post(f"/api/v1/encuestas/{survey['token']}", json={"answers": {"q1": "Sí"}, "consent": True})
    assert resp.status_code == 403


def test_results_of_another_company_are_off_limits(client):
    _, _, _, survey = _survey(client, "duenaenc@example.com")
    cid2, other = _setup(client, "intrusaenc@example.com")
    assert client.get(f"/api/v1/nivel1/{cid2}/surveys/{survey['token']}/results", headers=other).status_code == 404
