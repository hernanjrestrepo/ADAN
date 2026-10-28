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


# ============================================================
# Migración 0013: cada persona conserva su valor en dólares
# ============================================================

def test_rescale_migration_multiplies_balances_by_1000_and_back(tmp_path):
    from alembic import command
    from sqlalchemy import create_engine, text

    from app.core.migrations import alembic_config

    engine = create_engine(f"sqlite:///{tmp_path / 'm.db'}")
    with engine.begin() as conn:
        command.upgrade(alembic_config(conn), "0012")
        conn.execute(text("INSERT INTO apple_movements (id, user_id, kind, amount, reference, detail, created_at) "
                          "VALUES ('m1', 'u1', 'compra', 25, 'p1', 'x', '2026-10-20'), "
                          "('m2', 'u1', 'nivel', -5, 'c:1', 'x', '2026-10-21'), "
                          "('m3', 'u2', 'referido', 0.025, 'c:1', 'x', '2026-10-21')"))
        conn.execute(text("INSERT INTO apple_purchases (id, user_id, apples, amount_cop, trm, provider, status, "
                          "checkout_url, created_at) VALUES ('p1', 'u1', 25, 100000, 4000, 'wompi', 'aprobada', '', "
                          "'2026-10-20')"))
        conn.execute(text("INSERT INTO apple_level_unlocks (id, company_id, level_number, user_id, apples, created_at) "
                          "VALUES ('l1', 'c', 1, 'u1', 5, '2026-10-21')"))
        command.upgrade(alembic_config(conn), "0013")
        amounts = {r[0]: float(r[1]) for r in conn.execute(text("SELECT id, amount FROM apple_movements"))}
        assert amounts == {"m1": 25_000, "m2": -5_000, "m3": 25}                       # 25 → 25.000; 0,025 → 25
        assert conn.execute(text("SELECT apples, amount_cop FROM apple_purchases")).one() == (25_000, 100000)
        assert float(conn.execute(text("SELECT apples FROM apple_level_unlocks")).scalar()) == 5_000
        command.downgrade(alembic_config(conn), "0012")
        assert {r[0]: float(r[1]) for r in conn.execute(text("SELECT id, amount FROM apple_movements"))} == {
            "m1": 25, "m2": -5, "m3": 0.025}
        assert conn.execute(text("SELECT apples FROM apple_purchases")).scalar() == 25
