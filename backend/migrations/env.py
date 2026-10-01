"""Alembic env — usa DATABASE_URL de la app y la base declarativa única."""
from logging.config import fileConfig

from alembic import context

from app.core.config import settings
from app.core.database import Base, create_db_engine, import_all_models

config = context.config

if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)

import_all_models()
target_metadata = Base.metadata


def _configure(connection) -> None:
    if connection.dialect.name == "postgresql":
        # Permite reflejar columnas pgvector al comparar esquemas
        from pgvector.sqlalchemy import Vector

        connection.dialect.ischema_names["vector"] = Vector
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # SQLite no soporta ALTER TABLE completo: usar modo batch
        render_as_batch=connection.dialect.name == "sqlite",
        compare_type=True,
    )


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # La app puede pasar su propia conexión (app/core/migrations.py)
    connection = config.attributes.get("connection")
    if connection is not None:
        _configure(connection)
        with context.begin_transaction():
            context.run_migrations()
        return

    engine = create_db_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        _configure(conn)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
