"""Prueba de carga ligera: N ejecuciones encoladas concurrentemente, verificando que el
worker (corriendo por separado, ver docs/) las procesa todas sin perdida ni corrupcion.
Esta prueba SOLO encola y verifica persistencia final - requiere que un worker real este
corriendo aparte (`python worker.py`) para que las tareas se consuman, igual que en
produccion. No arranca un worker embebido a proposito: valida el mismo camino que usa
el sistema real, no un atajo de test."""

import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest

from db import SessionLocal
from orchestrator.models import EjecucionAgente
from orchestrator.queue import enqueue_run

pytestmark = pytest.mark.functional

N_CONCURRENT = 5
MAX_WAIT_S = 60


def test_n_concurrent_executions_all_complete() -> None:
    with ThreadPoolExecutor(max_workers=N_CONCURRENT) as pool:
        execution_ids = list(
            pool.map(
                lambda i: enqueue_run("diagnostico-nivel-1", f"Problema de prueba de carga numero {i}"),
                range(N_CONCURRENT),
            )
        )

    assert len(set(execution_ids)) == N_CONCURRENT  # todos los IDs son unicos, sin colision

    db = SessionLocal()
    try:
        deadline = time.monotonic() + MAX_WAIT_S
        pending = set(execution_ids)
        while pending and time.monotonic() < deadline:
            for execution_id in list(pending):
                row = (
                    db.query(EjecucionAgente)
                    .filter(EjecucionAgente.id == uuid.UUID(execution_id))
                    .first()
                )
                db.expire_all()  # fuerza releer el estado real, no la cache de identidad
                if row is not None and row.status in ("completed", "failed"):
                    pending.discard(execution_id)
            if pending:
                time.sleep(1)

        assert not pending, f"Ejecuciones sin terminar tras {MAX_WAIT_S}s: {pending}"

        rows = (
            db.query(EjecucionAgente)
            .filter(EjecucionAgente.id.in_([uuid.UUID(e) for e in execution_ids]))
            .all()
        )
        assert len(rows) == N_CONCURRENT
        inputs_seen = {r.user_input for r in rows}
        assert len(inputs_seen) == N_CONCURRENT  # ninguna tarea se mezclo con otra

        for row in rows:
            db.delete(row)
        db.commit()
    finally:
        db.close()
