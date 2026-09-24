"""Funcional: API CRUD/traversal del Knowledge Graph contra Postgres real."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.auth.jwt import create_access_token, hash_password
from app.db import SessionLocal
from app.main import app
from app.models.usuario import Usuario

pytestmark = pytest.mark.functional


@pytest.fixture
def authed_client():
    db = SessionLocal()
    unique = uuid.uuid4().hex[:8]
    email = f"kg-api-test-{unique}@adan-demo.io"
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


def test_create_nodes_edge_and_traverse(authed_client: TestClient) -> None:
    n1 = authed_client.post("/kg/nodes", json={"tipo": "entidad", "nombre": "API Node 1"})
    assert n1.status_code == 201
    n2 = authed_client.post("/kg/nodes", json={"tipo": "hecho", "nombre": "API Node 2"})
    assert n2.status_code == 201

    n1_id, n2_id = n1.json()["id"], n2.json()["id"]

    edge_resp = authed_client.post(
        "/kg/edges", json={"origen_id": n1_id, "destino_id": n2_id, "tipo_relacion": "afecta_a"}
    )
    assert edge_resp.status_code == 201

    traverse_resp = authed_client.get(f"/kg/nodes/{n1_id}/traverse?max_depth=2")
    assert traverse_resp.status_code == 200
    body = traverse_resp.json()
    node_names = {n["nombre"] for n in body["nodos"]}
    assert node_names == {"API Node 1", "API Node 2"}
    assert len(body["aristas"]) == 1

    # limpieza: los endpoints de creacion hacen commit real, sin esto quedaria residuo
    db = SessionLocal()
    db.execute(text("DELETE FROM kg_aristas WHERE origen_id = :n1"), {"n1": n1_id})
    db.execute(text("DELETE FROM kg_nodos WHERE id IN (:n1, :n2)"), {"n1": n1_id, "n2": n2_id})
    db.commit()
    db.close()


def test_get_node_not_found(authed_client: TestClient) -> None:
    resp = authed_client.get(f"/kg/nodes/{uuid.uuid4()}")
    assert resp.status_code == 404
