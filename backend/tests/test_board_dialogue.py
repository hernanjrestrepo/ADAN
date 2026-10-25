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
