-- Tabla ejecuciones_agente - ver contracts/events/agent_execution.md para el contrato completo.
-- DDL cruda (no via SQLAlchemy create_all) porque /ai usa un Base propio, separado del de
-- /backend a proposito (sin acoplamiento de import) - SQLAlchemy no puede resolver la FK a
-- "proyectos" entre dos MetaData distintos. La FK real si existe a nivel de Postgres.
CREATE TABLE IF NOT EXISTS ejecuciones_agente (
    id UUID PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    proyecto_id UUID REFERENCES proyectos(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    user_input TEXT NOT NULL,
    final_output TEXT,
    transcript JSONB,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ
);
