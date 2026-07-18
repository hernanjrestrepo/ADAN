"""Funcional: /agents/run encola correctamente en Redis real (contrato con /ai).
La ejecucion real (worker -> Ollama -> Postgres) se verifica en ai/tests/ y se demostro
manualmente end-to-end en el reporte de WO-002 Sprint 4."""

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.agent_queue import QUEUE_KEY, get_redis_client
from app.auth.jwt import create_access_token, hash_password
from app.db import SessionLocal
from app.main import app
from app.models.usuario import Usuario

pytestmark = pytest.mark.functional


@pytest.fixture
def authed_client():
    # commit() es necesario aqui (no alcanza con flush): la API bajo prueba abre su PROPIA
    # sesion via el dependency get_db, en una conexion distinta - solo ve filas comprometidas.
    db = SessionLocal()
    unique = uuid.uuid4().hex[:8]
    email = f"agents-test-{unique}@adan-demo.io"
    user = Usuario(email=email, hashed_password=hash_password("x"))
    db.add(user)
    db.commit()
    token = create_access_token(email)
    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {token}"
    try:
        yield client
    finally:
        db.delete(user)
        db.commit()
        db.close()


def test_run_unknown_agent_returns_404(authed_client: TestClient) -> None:
    resp = authed_client.post("/agents/run", json={"agent_id": "no-existe", "user_input": "x"})
    assert resp.status_code == 404


def test_run_known_agent_enqueues_real_redis_message(authed_client: TestClient) -> None:
    redis_client = get_redis_client()
    redis_client.delete(QUEUE_KEY)  # aisla esta prueba de mensajes previos en la cola

    resp = authed_client.post(
        "/agents/run", json={"agent_id": "diagnostico-nivel-1", "user_input": "hola"}
    )
    assert resp.status_code == 202
    execution_id = resp.json()["execution_id"]

    _, raw = redis_client.brpop([QUEUE_KEY], timeout=2)
    message = json.loads(raw)
    assert message["execution_id"] == execution_id
    assert message["agent_id"] == "diagnostico-nivel-1"
    assert message["user_input"] == "hola"


def test_get_run_not_found(authed_client: TestClient) -> None:
    resp = authed_client.get(f"/agents/runs/{uuid.uuid4()}")
    assert resp.status_code == 404
