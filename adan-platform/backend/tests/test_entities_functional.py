"""Functional tests against real PostgreSQL (docker compose postgres/redis must be up).
BP-0006, BP-0007: verifies the core entity graph writes and reads correctly.

Isolation: each test flushes (visible within its own transaction) but never commits -
the fixture always rolls back, so the real database is never left with test residue,
regardless of how many times the suite runs."""

import uuid

import pytest

from app.db import SessionLocal
from app.models import Empresa, Nivel, Proyecto, Usuario

pytestmark = pytest.mark.functional


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def test_empresa_proyecto_nivel_graph(db) -> None:
    unique = uuid.uuid4().hex[:8]
    usuario = Usuario(email=f"func-test-{unique}@adan.local", hashed_password="x", display_name="Test")
    db.add(usuario)
    db.flush()

    empresa = Empresa(razon_social=f"Functional Test Co. {unique}")
    db.add(empresa)
    db.flush()

    proyecto = Proyecto(empresa_id=empresa.id, usuario_principal_id=usuario.id)
    db.add(proyecto)
    db.flush()

    nivel = Nivel(proyecto_id=proyecto.id, numero=1, nombre="El Dolor")
    db.add(nivel)
    db.flush()

    fetched = db.query(Proyecto).filter(Proyecto.id == proyecto.id).first()
    assert fetched is not None
    assert fetched.empresa_id == empresa.id
    assert fetched.usuario_principal_id == usuario.id
    assert fetched.niveles[0].nombre == "El Dolor"

    # Contrato Base (AD-006 SS2) - todo tiene version/estado por defecto
    assert fetched.status == "active"
    assert fetched.created_at is not None


def test_score_polymorphic_empresa_or_usuario(db) -> None:
    """AD-006 v1.2: Score es N:1 con Empresa (Venture Score) o con Usuario (Score del Responsable)."""
    from app.models import Score

    unique = uuid.uuid4().hex[:8]
    usuario = Usuario(email=f"score-test-{unique}@adan.local", hashed_password="x")
    empresa = Empresa(razon_social=f"Score Test Co. {unique}")
    db.add_all([usuario, empresa])
    db.flush()

    venture_score = Score(empresa_id=empresa.id, tipo="venture", valor=72.5, confidence_level=0.4)
    responsable_score = Score(usuario_id=usuario.id, tipo="responsable", valor=88.0, confidence_level=0.5)
    db.add_all([venture_score, responsable_score])
    db.flush()

    assert db.query(Score).filter(Score.empresa_id == empresa.id).first().tipo == "venture"
    assert db.query(Score).filter(Score.usuario_id == usuario.id).first().tipo == "responsable"
