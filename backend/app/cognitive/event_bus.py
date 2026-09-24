"""
Event Bus — Backbone de comunicación del sistema cognitivo.

Cada componente publica eventos. El bus los rutea a suscriptores.
Todo se persiste en la tabla events (append-only).
"""

import uuid
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Callable
from sqlalchemy.orm import Session

from app.models.models import Event, Project


@dataclass
class CognitiveEvent:
    """Evento cognitivo del sistema."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    source: str = ""
    agent_id: str | None = None
    project_id: str | None = None
    company_id: str | None = None
    conversation_id: str | None = None
    trace_id: str = ""
    parent_event_id: str | None = None
    payload: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int | None = None


class EventBus:
    """
    Bus de eventos centralizado.
    
    Publica eventos, los persiste en BD, y notifica a suscriptores.
    Garantiza at-least-once delivery.
    """

    def __init__(self, db: Session):
        self.db = db
        self._subscribers: dict[str, list[Callable]] = {}
        self._metrics: dict[str, int] = {}

    def publish(self, event: CognitiveEvent) -> str:
        """Publica un evento: persiste + notifica suscriptores."""
        # 1. Persistir en BD
        self._persist(event)

        # 2. Notificar suscriptores
        self._route(event)

        # 3. Actualizar métricas
        key = f"events_{event.type}"
        self._metrics[key] = self._metrics.get(key, 0) + 1

        return event.id

    def subscribe(self, event_type: str, handler: Callable):
        """Suscribe un handler a un tipo de evento."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def get_metrics(self) -> dict[str, int]:
        """Retorna métricas de eventos publicados."""
        return dict(self._metrics)

    def _persist(self, event: CognitiveEvent):
        """Persiste el evento en la tabla events (append-only)."""
        # Event model uses String(36) columns, so pass strings directly
        event_id_str = event.id if isinstance(event.id, str) else str(event.id)

        # Resolve project_id from company_id if not provided
        project_id_str = event.project_id
        if not project_id_str and event.company_id:
            project = self.db.query(Project).filter(
                Project.company_id == event.company_id
            ).first()
            if project:
                project_id_str = str(project.id)

        # Skip persistence if no valid project_id (Event requires FK)
        if not project_id_str:
            return

        db_event = Event(
            id=event_id_str,
            project_id=project_id_str,
            event_type=event.type,
            entity_type=event.source,
            entity_id=event_id_str,
            data={
                "source": event.source,
                "agent_id": event.agent_id,
                "trace_id": event.trace_id,
                "parent_event_id": event.parent_event_id,
                "payload": event.payload,
                "duration_ms": event.duration_ms,
            },
            created_at=event.timestamp,
        )
        self.db.add(db_event)
        self.db.flush()

    def _route(self, event: CognitiveEvent):
        """Rutea el evento a suscriptores interesados."""
        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                pass  # Los errores de suscriptores no bloquean el bus


def create_trace_id() -> str:
    """Genera un trace_id único para una operación completa."""
    return f"trace-{uuid.uuid4().hex[:12]}"
