"""Persistencia propia de /ai - mismo Postgres fisico que /backend, Base/engine separados
a proposito (sin import directo de app.db). El contrato compartido es el ESQUEMA de tabla,
documentado en contracts/events/agent_execution.md."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_ai_settings

settings = get_ai_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
