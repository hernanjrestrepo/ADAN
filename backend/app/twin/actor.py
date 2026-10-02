"""Quién hace cada cambio (AD-008 §3): Usuario Principal, Usuario, Agente o ADÁN (sistema).

El actor viaja en un ContextVar para que el hook de persistencia (app/twin/hooks.py) pueda
validar permisos y registrar el responsable sin tener que pasarlo por cada función.

    with acting_as(Actor.agent("Board Room")):
        ...  # todo lo que se guarde aquí queda a nombre del Board Room
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator, Literal

ActorKind = Literal["user", "agent", "system"]


@dataclass(frozen=True)
class Actor:
    kind: ActorKind
    id: str | None = None
    label: str | None = None

    @classmethod
    def user(cls, user_id: str, label: str | None = None) -> "Actor":
        return cls("user", user_id, label)

    @classmethod
    def agent(cls, name: str) -> "Actor":
        return cls("agent", name, name)

    @classmethod
    def system(cls, reason: str | None = None) -> "Actor":
        return cls("system", None, reason or "ADÁN")

    def __str__(self) -> str:
        return f"{self.kind}:{self.id}" if self.id else self.kind


SYSTEM = Actor.system()

_current_actor: ContextVar[Actor] = ContextVar("adan_actor", default=SYSTEM)
_change_reason: ContextVar[str | None] = ContextVar("adan_change_reason", default=None)


def current_actor() -> Actor:
    return _current_actor.get()


def current_reason() -> str | None:
    return _change_reason.get()


@contextmanager
def acting_as(actor: Actor, reason: str | None = None) -> Iterator[Actor]:
    token = _current_actor.set(actor)
    reason_token = _change_reason.set(reason)
    try:
        yield actor
    finally:
        _change_reason.reset(reason_token)
        _current_actor.reset(token)


def set_request_actor(actor: Actor) -> None:
    """Fija el actor para el resto de la request (dependencia de FastAPI)."""
    _current_actor.set(actor)
