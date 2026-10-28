"""Economía de IA: el Board no se repite sin motivo, y los precios y márgenes salen de los costos medidos."""
from app.models.models import Event
from tests.test_discovery import BoardLLM, _setup, _use


def _boards(db_session):
    db_session.expire_all()
    return db_session.query(Event).filter(Event.event_type == "board_room_completed").count()


def test_diagnosis_reuses_the_current_board_instead_of_running_another(client, db_session):
    cid, headers = _setup(client, "unboard@example.com")
    llm = _use(client, BoardLLM())
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"},
                headers=headers)
    assert client.post(f"/api/v1/nivel1/{cid}/board-room", headers=headers).status_code == 200
    assert _boards(db_session) == 1
    calls = len(llm.board_prompts)

    diagnosis = client.post(f"/api/v1/nivel1/{cid}/diagnosis", headers=headers)
    assert diagnosis.status_code == 200
    assert _boards(db_session) == 1               # no se ejecutó otro Board
    assert len(llm.board_prompts) == calls        # ni una llamada de votos de más

    # Si el cliente aporta algo nuevo, el Board anterior ya no vale y el diagnóstico corre uno nuevo
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "Entrevisté a 15 familias más"}, headers=headers)
    assert client.post(f"/api/v1/nivel1/{cid}/diagnosis", headers=headers).status_code == 200
    assert _boards(db_session) == 2


def test_diagnosis_without_a_board_runs_exactly_one(client, db_session):
    cid, headers = _setup(client, "sinboardprevio@example.com")
    _use(client, BoardLLM())
    client.post(f"/api/v1/nivel1/{cid}/chat", json={"message": "A las familias les cuesta planear viajes"},
                headers=headers)
    assert client.post(f"/api/v1/nivel1/{cid}/diagnosis", headers=headers).status_code == 200
    assert _boards(db_session) == 1


def test_structured_output_schemas_use_only_what_claude_accepts():
    """La API de Claude rechaza minimum/maximum en enteros (400 visto con la clave real)."""
    from app.arena import service as arena
    from app.nivel1 import board_room

    schemas = [value for module in (board_room, arena) for name, value in vars(module).items()
               if name.endswith("_SCHEMA") and isinstance(value, dict)]
    assert len(schemas) >= 3

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "integer":
                assert not {"minimum", "maximum"} & set(node), node
            for value in node.values():
                walk(value)

    for schema in schemas:
        walk(schema)
