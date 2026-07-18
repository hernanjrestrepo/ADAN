"""Funcional: Knowledge Graph contra Postgres real. BP-0007 (AD-CMP-04).

kg_nodos.proyecto_id tiene una FK real a proyectos.id (schema.sql) - las pruebas que no
necesitan aislar por Proyecto usan proyecto_id=None (nodos de alcance global, capa Global
de AD-CMP-04 SS1, valido por diseno). La prueba que si necesita dos Proyectos reales para
verificar aislamiento crea filas minimas via SQL crudo (Usuario/Empresa/Proyecto) sin
importar el ORM de /backend - misma disciplina de separacion de siempre."""

import uuid

import pytest
from sqlalchemy import text

from db import SessionLocal
from memory.models import KGArista
from memory.repository import create_edge, create_node, list_nodes_by_proyecto, traverse

pytestmark = pytest.mark.functional


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def _create_real_proyecto(db) -> uuid.UUID:
    """Crea Usuario+Empresa+Proyecto minimos via SQL crudo, solo para satisfacer la FK
    real de kg_nodos.proyecto_id en esta prueba - sin importar el ORM de /backend."""
    unique = uuid.uuid4().hex[:8]
    usuario_id = uuid.uuid4()
    empresa_id = uuid.uuid4()
    proyecto_id = uuid.uuid4()
    db.execute(
        text(
            "INSERT INTO usuarios (id, email, hashed_password, status, created_at, updated_at) "
            "VALUES (:id, :email, 'x', 'active', now(), now())"
        ),
        {"id": usuario_id, "email": f"kg-test-{unique}@adan-demo.io"},
    )
    db.execute(
        text(
            "INSERT INTO empresas (id, razon_social, status, created_at, updated_at) "
            "VALUES (:id, :nombre, 'active', now(), now())"
        ),
        {"id": empresa_id, "nombre": f"KG Test Co. {unique}"},
    )
    db.execute(
        text(
            "INSERT INTO proyectos (id, empresa_id, usuario_principal_id, status, created_at, updated_at) "
            "VALUES (:id, :empresa_id, :usuario_id, 'active', now(), now())"
        ),
        {"id": proyecto_id, "empresa_id": empresa_id, "usuario_id": usuario_id},
    )
    db.flush()
    return proyecto_id


def test_create_node_and_edge_real_postgres(db) -> None:
    empresa_node = create_node(db, tipo="entidad", nombre="Empresa Demo")
    competidor_node = create_node(db, tipo="hecho", nombre="Competidor subio precios")
    edge = create_edge(db, empresa_node.id, competidor_node.id, "afecta_a")
    db.flush()

    fetched_edge = db.query(KGArista).filter(KGArista.id == edge.id).first()
    assert fetched_edge is not None
    assert fetched_edge.origen_id == empresa_node.id
    assert fetched_edge.destino_id == competidor_node.id


def test_list_nodes_by_proyecto_isolated(db) -> None:
    proyecto_a = _create_real_proyecto(db)
    proyecto_b = _create_real_proyecto(db)
    create_node(db, tipo="entidad", nombre="Nodo A", proyecto_id=proyecto_a)
    create_node(db, tipo="entidad", nombre="Nodo B", proyecto_id=proyecto_b)
    db.flush()

    nodes_a = list_nodes_by_proyecto(db, proyecto_a)
    assert len(nodes_a) == 1
    assert nodes_a[0].nombre == "Nodo A"


def test_traverse_bfs_real_postgres(db) -> None:
    n1 = create_node(db, tipo="entidad", nombre="N1")
    n2 = create_node(db, tipo="entidad", nombre="N2")
    n3 = create_node(db, tipo="entidad", nombre="N3")
    create_edge(db, n1.id, n2.id, "relacionado_con")
    create_edge(db, n2.id, n3.id, "relacionado_con")
    db.flush()

    result = traverse(db, n1.id, max_depth=2)

    node_names = {n.nombre for n in result["nodos"]}
    assert node_names == {"N1", "N2", "N3"}
    assert len(result["aristas"]) == 2


def test_traverse_respects_max_depth(db) -> None:
    n1 = create_node(db, tipo="entidad", nombre="D1")
    n2 = create_node(db, tipo="entidad", nombre="D2")
    n3 = create_node(db, tipo="entidad", nombre="D3")
    create_edge(db, n1.id, n2.id, "rel")
    create_edge(db, n2.id, n3.id, "rel")
    db.flush()

    result = traverse(db, n1.id, max_depth=1)
    node_names = {n.nombre for n in result["nodos"]}
    assert node_names == {"D1", "D2"}  # D3 esta a profundidad 2, fuera de alcance
