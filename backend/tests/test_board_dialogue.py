"""Diálogo con el Board: hablarle en general o responderle a un especialista, y que el voto solo cambie con evidencia."""
import json

from app.ai.base import LLMResponse
from tests.test_discovery import BoardLLM, _setup, _use


class DialogueLLM(BoardLLM):
    def __init__(self, replies):
        super().__init__()
        self.replies = replies
        self.dialogue_prompts = []

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        if "replies" in schema.get("properties", {}):
            self.dialogue_prompts.append(messages[-1].content)
            data = self.replies.pop(0)
            return LLMResponse(content=json.dumps(data), model="fake", parsed=data)
        return await super().chat_json(messages, schema, model, temperature, max_tokens)


def test_the_founder_talks_with_the_board_and_votes_change_only_when_justified(client):
    cid, h = _setup(client, "dialogo@example.com")
    llm = _use(client, DialogueLLM([
        {"replies": [{"agent": "CFO", "reply": "Con 20 preventas a USD 50 ya hay ingresos medidos.", "vote": "PROCEED",
                      "changed": True, "reason": "Trajo 20 preventas pagadas"},
                     {"agent": "Gerente", "reply": "intruso", "vote": "PROCEED", "changed": True}],
         "ceo": "El CFO queda conforme; falta Legal.", "consensus": "Hay caja inicial validada"},
        {"replies": [{"agent": "Legal", "reply": "Sin registro ante la SIC no avanzo.", "vote": "PROCEED", "changed": False}],
         "ceo": "Legal mantiene su voto.", "consensus": "sin consenso todavía"},
    ]))
    url = f"/api/v1/nivel1/{cid}/board-room/dialogo"
    assert client.post(url, headers=h, json={"message": "Hola"}).status_code == 404  # sin sesión del Board
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"}, headers=h)
    assert client.post(f"/api/v1/nivel1/{cid}/board-room", headers=h).status_code == 200

    first = client.post(url, headers=h, json={"message": "Ya tengo 20 preventas pagadas"}).json()
    assert [r["agent"] for r in first["turn"]["replies"]] == ["CFO"]  # quien no es del Board no habla
    assert first["tally"]["votes"]["CFO"] == "PROCEED" and first["tally"]["proceed"] == 1

    # Respuesta a un especialista: si no cambia su voto, sigue el vigente aunque el modelo diga otro
    second = client.post(url, headers=h, json={"message": "¿Qué registro necesito?", "agent": "Legal"}).json()
    assert second["turn"]["agent"] == "Legal" and second["turn"]["replies"][0]["vote"] == "PIVOT"
    assert second["tally"]["votes"]["Legal"] == "PIVOT"
    assert "Ya tengo 20 preventas pagadas" in llm.dialogue_prompts[1]  # el hilo se recuerda

    thread = client.get(url, headers=h).json()
    assert len(thread["thread"]) == 2 and thread["tally"]["proceed"] == 1
    assert client.post(url, headers=h, json={"message": "x", "agent": "Gerente"}).status_code == 400

    # El siguiente Board lee lo conversado
    client.post(f"/api/v1/nivel1/{cid}/board-room", headers=h)
    assert any("Ya tengo 20 preventas pagadas" in p for p in llm.board_prompts)
    assert client.get(url, headers=h).json()["thread"] == []  # sesión nueva, hilo nuevo


def test_the_dialogue_is_private(client):
    cid, _ = _setup(client, "duenoboard@example.com")
    _, other = _setup(client, "ajenoboard@example.com")
    assert client.get(f"/api/v1/nivel1/{cid}/board-room/dialogo", headers=other).status_code == 404


def test_an_empty_board_answer_is_retried_and_never_shown_as_garbage(client):
    cid, h = _setup(client, "vacio@example.com")
    _use(client, DialogueLLM([
        {"replies": [], "ceo": "Xmart Travel", "consensus": ""},
        {"replies": [{"agent": "legal", "reply": "Con la explicación del bono sin compra obligatoria, mi objeción baja.",
                      "vote": "PIVOT", "changed": False}], "ceo": "Legal entiende el punto; falta el dictamen escrito.", "consensus": "x"},
    ]))
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"}, headers=h)
    client.post(f"/api/v1/nivel1/{cid}/board-room", headers=h)
    turn = client.post(f"/api/v1/nivel1/{cid}/board-room/dialogo", headers=h, json={"message": "No es pirámide"}).json()["turn"]
    assert turn["replies"][0]["agent"] == "Legal" and turn["ceo"].startswith("Legal entiende")


def test_the_founder_can_continue_anyway_and_it_lowers_the_score(client):
    cid, h = _setup(client, "continuo@example.com")
    _use(client, DialogueLLM([]))
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"}, headers=h)
    url = f"/api/v1/nivel1/{cid}/board-room/continuar"
    assert client.post(url, headers=h, json={"reason": "sin sesión"}).status_code == 404
    client.post(f"/api/v1/nivel1/{cid}/board-room", headers=h)
    res = client.post(url, headers=h,
                      json={"reason": "Ya expliqué los tres temas; el mercado solo se valida lanzando"}).json()
    assert res["recorded"] is True and len(res["open_objections"]) == 6  # en la prueba los seis votaron PIVOT
    evidence = client.get(f"/api/v1/scoring/{cid}/evidence", headers=h).json()
    note = [e for e in evidence if "decidió continuar" in e["claim"]]
    assert note and note[0]["polarity"] == "contradicts" and note[0]["kind"] == "inference"


def test_the_board_session_and_its_dialogue_live_in_the_same_conversation(client):
    cid, h = _setup(client, "unasala@example.com")
    _use(client, DialogueLLM([{"replies": [{"agent": "CFO", "reply": "Con 20 preventas pagadas cambio mi voto.",
                                            "vote": "PROCEED", "changed": True, "reason": "20 preventas"}],
                               "ceo": "El CFO queda conforme; sigue faltando Legal.", "consensus": "Caja inicial validada"}]))
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"}, headers=h)
    client.post(f"/api/v1/nivel1/{cid}/board-room", headers=h)
    client.post(f"/api/v1/nivel1/{cid}/board-room/dialogo", headers=h, json={"message": "Tengo 20 preventas"})
    msgs = client.get(f"/api/v1/nivel1/{cid}/status", headers=h).json()["messages"]
    board = [m for m in msgs if (m.get("metadata_json") or {}).get("escena") == "board"]
    names = [m["agent_name"] for m in board]
    assert names[0] == "ADAN" and "Camila · CFO" in names and "Lucía · Legal" in names
    assert any(m["role"] == "user" and m["content"] == "Tengo 20 preventas" for m in board)
    assert "Cambio mi voto" in board[-2]["content"] and board[-1]["agent_name"] == "ADAN"
