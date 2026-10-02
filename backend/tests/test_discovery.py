"""Guion del Descubrimiento del Dolor: ADÁN entiende cada respuesta, sigue un orden y no repite."""
import json

from app.ai.base import LLMAdapter, LLMResponse
from app.ai.router import ModelRouter
from app.api.v1 import nivel1 as nivel1_api
from app.models.models import Message
from app.nivel1 import discovery
from tests.fakes import FakeLLM


class ScriptLLM(LLMAdapter):
    """Modelo de prueba con salida estructurada: devuelve un turno por llamada."""

    def __init__(self, turns, degraded=None):
        self.turns, self.calls, self.degraded = list(turns), [], degraded

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        self.calls.append(messages)
        turn = self.turns[min(len(self.calls), len(self.turns)) - 1]
        resp = LLMResponse(content=json.dumps(turn, ensure_ascii=False), model="fake", parsed=turn)
        if self.degraded:
            resp.metadata["degraded"] = self.degraded
        return resp

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        raise AssertionError("el chat del Nivel 1 usa salida estructurada")

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048):
        return LLMResponse(content="doc", model="fake")

    async def health_check(self):
        return True

    def list_models(self):
        return []


def topic(tid, estado="respondido", resumen="", base="supuesto"):
    return {"id": tid, "estado": estado, "resumen": resumen, "base": base}


TURN_1 = {
    "respuesta": "Entiendo: las familias pierden horas armando viajes con muchas herramientas. ¿Cada cuánto viajan? (Tema 3 de 7)",
    "temas": [topic("problema", resumen="Planear un viaje exige muchas herramientas separadas"),
              topic("afectados", resumen="Familias de ingreso medio-alto en Colombia")],
    "evidencia_sugerida": [],
}
TURN_2 = {
    "respuesta": "Anotado: 12 de 15 entrevistados tardan más de 10 horas. ¿Cuánto les cuesta? (Tema 4 de 7)",
    "temas": [topic("problema", estado="pendiente"),  # el modelo lo omite: no debe perderse
              topic("momento", resumen="Viajan dos veces al año, en vacaciones", base="dato")],
    "evidencia_sugerida": [{"afirmacion": "12 de 15 familias entrevistadas tardan más de 10 horas planeando un viaje",
                            "tipo": "testimony", "fuente": "Entrevistas de Hernán, septiembre 2026"}],
}


def _setup(client, email):
    resp = client.post("/api/v1/auth/register", json={"email": email, "name": "Hernán Restrepo",
                                                      "password": "password123", "accept_data_policy": True})
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    cid = client.post("/api/v1/companies/", json={"name": "Xmart Travel"}, headers=headers).json()["id"]
    return cid, headers


def _use(client, llm):
    client.app.dependency_overrides[nivel1_api.get_llm] = lambda: llm
    return llm


def test_each_answer_is_understood_and_the_script_advances(client):
    cid, headers = _setup(client, "guion@example.com")
    llm = _use(client, ScriptLLM([TURN_1, TURN_2]))

    first = client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"},
                        headers=headers).json()
    assert first["message"]["content"].startswith("Entiendo: las familias")
    progress = client.get(f"/api/v1/nivel1/{cid}/status", headers=headers).json()["discovery"]
    assert progress["done"] == 2 and progress["next"] == "momento" and progress["total"] == 7
    assert progress["topics"][1]["resumen"] == "Familias de ingreso medio-alto en Colombia"

    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "Viajan dos veces al año; entrevisté 15 familias"},
                headers=headers)
    # El segundo turno ve lo ya entendido y sabe qué tema sigue
    system = llm.calls[1][0].content
    assert "Familias de ingreso medio-alto" in system and "El siguiente tema del guion es «momento»" in system
    progress = client.get(f"/api/v1/nivel1/{cid}/status", headers=headers).json()["discovery"]
    assert progress["topics"][0]["estado"] == "respondido"  # no retrocede
    assert progress["done"] == 3 and progress["next"] == "costo"
    assert progress["evidence_suggestions"][0]["tipo"] == "testimony"


def test_a_suggested_evidence_is_not_suggested_again_once_registered(client):
    cid, headers = _setup(client, "sugerida@example.com")
    _use(client, ScriptLLM([TURN_2]))
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "Entrevisté 15 familias"}, headers=headers)
    suggestion = client.get(f"/api/v1/nivel1/{cid}/status", headers=headers).json()["discovery"]["evidence_suggestions"][0]
    assert client.post(f"/api/v1/scoring/{cid}/evidence", headers=headers, json={
        "claim": suggestion["afirmacion"], "kind": suggestion["tipo"], "source": suggestion["fuente"]}).status_code == 201
    assert client.get(f"/api/v1/nivel1/{cid}/status", headers=headers).json()["discovery"]["evidence_suggestions"] == []


def test_when_all_topics_are_covered_adan_stops_asking():
    state = discovery.empty_state()
    for tid in discovery.TOPIC_IDS:
        state["temas"][tid] = {"estado": "respondido", "resumen": "x", "base": "dato"}
    state["temas"]["costo"]["estado"] = "sin_dato"
    assert discovery.next_topic(state) is None and discovery.progress(state)["complete"]
    assert "no hagas más preguntas" in discovery.system_prompt(state)


def test_degraded_model_answer_is_flagged_and_does_not_touch_the_script(client, db_session):
    cid, headers = _setup(client, "degradado@example.com")
    _use(client, ScriptLLM([TURN_1], degraded="Claude no disponible (APIConnectionError)"))
    body = client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "Hola"}, headers=headers).json()
    assert body["message"]["metadata_json"]["degraded"].startswith("Claude no disponible")
    assert client.get(f"/api/v1/nivel1/{cid}/status", headers=headers).json()["discovery"]["done"] == 0


def test_without_claude_the_router_marks_the_turn_as_degraded(client):
    cid, headers = _setup(client, "sinclave@example.com")
    _use(client, ModelRouter(FakeLLM(chat_replies=["respuesta local"]), claude_factory=lambda tier: None))
    body = client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "Hola"}, headers=headers).json()
    assert body["message"]["content"] == "respuesta local"
    assert body["message"]["metadata_json"]["degraded"] == "sin ANTHROPIC_API_KEY"


def test_unparseable_output_never_reaches_the_client_as_json(client, db_session):
    cid, headers = _setup(client, "roto@example.com")
    _use(client, FakeLLM(chat_replies=['{"respuesta": ']))
    body = client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "Hola"}, headers=headers).json()
    assert body["message"]["content"].startswith("No pude procesar tu mensaje")
    # El mensaje del cliente queda guardado
    assert db_session.query(Message).filter(Message.role == "user", Message.content == "Hola").count() == 1


def test_streaming_prompt_asks_only_for_the_reply():
    prompt = discovery.system_prompt(discovery.empty_state(), structured=False)
    assert "`temas`" not in prompt and "UNA sola pregunta" in prompt


# ============================================================
# Board Room: evalúa lo que ADÁN entendió, no la charla cruda
# ============================================================

class BoardLLM(ScriptLLM):
    """Guarda lo que recibe el Board y devuelve votos válidos."""

    def __init__(self):
        super().__init__([TURN_1])
        self.board_prompts = []

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        if "respuesta" in schema.get("properties", {}):
            return await super().chat_json(messages, schema, model, temperature, max_tokens)
        self.board_prompts.append(messages[-1].content)
        props = schema["properties"]
        if "vote" in props:
            data = {"analysis": "a", "justification": "j", "vote": "PIVOT", "confidence": 40,
                    "key_strengths": [], "key_concerns": [], "questions": []}
        elif "objective" in props:
            data = {"objective": "o", "decision_at_stake": "d"}
        else:
            data = {"synthesis": "Validar con 15 familias", "evidence_requests": ["15 entrevistas"], "next_steps": []}
        return LLMResponse(content=json.dumps(data), model="fake", parsed=data)


def test_board_evaluates_the_script_and_evidence_not_degraded_noise(client, db_session):
    cid, headers = _setup(client, "board@example.com")
    llm = _use(client, BoardLLM())
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"}, headers=headers)
    client.post(f"/api/v1/scoring/{cid}/evidence", headers=headers, json={
        "claim": "Sabre y PayPal anunciaron reserva agéntica en 2026", "kind": "external", "source": "Nota de prensa"})
    # Una respuesta del modelo de respaldo no debe llegar al Board
    conv_id = db_session.query(Message).filter(Message.role == "user").first().conversation_id
    db_session.add(Message(conversation_id=conv_id, role="assistant", content="Problemos principales resueltos",
                           metadata_json={"degraded": "sin ANTHROPIC_API_KEY"}))
    db_session.commit()

    resp = client.post(f"/api/v1/nivel1/{cid}/board-room", headers=headers)
    assert resp.status_code == 200 and resp.json()["decision"] == "PIVOT"
    vote_prompt = llm.board_prompts[1]
    assert "Familias de ingreso medio-alto en Colombia [supuesto]" in vote_prompt
    assert "[fuente externa] Sabre y PayPal" in vote_prompt
    assert "Problemos" not in vote_prompt

    last = client.get(f"/api/v1/nivel1/{cid}/board-room/last", headers=headers)
    assert last.status_code == 200 and last.json()["synthesis"] == "Validar con 15 familias"


def test_last_board_is_404_before_any_session_and_private(client):
    cid, headers = _setup(client, "sinboard@example.com")
    assert client.get(f"/api/v1/nivel1/{cid}/board-room/last", headers=headers).status_code == 404
    _other, other_headers = _setup(client, "otroboard@example.com")
    assert client.get(f"/api/v1/nivel1/{cid}/board-room/last", headers=other_headers).status_code == 404
