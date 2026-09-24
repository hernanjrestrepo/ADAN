"""Entorno de Alembic de ADÁN.

La conexión sale de `config.attributes["connection"]` (cuando la app migra al arrancar)
o de DATABASE_URL. Funciona con SQLite (modo batch para ALTER) y con PostgreSQL.
"""
from alembic import context

from app.core.config import settings
from app.core.database import Base, import_all_models, make_engine
from app.core.migrations import include_object_for

import_all_models()
target_metadata = Base.metadata


def _configure(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=connection.dialect.name == "sqlite",
        compare_type=True,
        include_object=include_object_for(connection.dialect.name),
    )


def run_migrations_offline() -> None:
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = context.config.attributes.get("connection")
    if connection is not None:
        _configure(connection)
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = make_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        _configure(connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
