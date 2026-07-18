-- Knowledge Graph relacional + memoria semantica - WO-003. Ver contracts/events/ (futuro
-- contrato si otra celula necesita escribir aqui) y memory/models.py para el detalle.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS kg_nodos (
    id UUID PRIMARY KEY,
    proyecto_id UUID REFERENCES proyectos(id),
    tipo VARCHAR(100) NOT NULL,
    nombre VARCHAR(500) NOT NULL,
    atributos JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_kg_nodos_proyecto_id ON kg_nodos(proyecto_id);
CREATE INDEX IF NOT EXISTS ix_kg_nodos_tipo ON kg_nodos(tipo);

CREATE TABLE IF NOT EXISTS kg_aristas (
    id UUID PRIMARY KEY,
    origen_id UUID NOT NULL REFERENCES kg_nodos(id),
    destino_id UUID NOT NULL REFERENCES kg_nodos(id),
    tipo_relacion VARCHAR(100) NOT NULL,
    atributos JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_kg_aristas_origen ON kg_aristas(origen_id);
CREATE INDEX IF NOT EXISTS ix_kg_aristas_destino ON kg_aristas(destino_id);

CREATE TABLE IF NOT EXISTS memoria_semantica (
    id UUID PRIMARY KEY,
    proyecto_id UUID REFERENCES proyectos(id),
    nodo_id UUID REFERENCES kg_nodos(id),
    contenido TEXT NOT NULL,
    origen VARCHAR(100) NOT NULL,
    embedding VECTOR(768) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_memoria_semantica_proyecto_id ON memoria_semantica(proyecto_id);
-- Indice HNSW para busqueda aproximada por similitud coseno - se crea despues de tener
-- datos reales si el volumen lo justifica (Economia Conceptual: no optimizar sin evidencia
-- de que hace falta). Con corpus demo pequeno, un scan secuencial exacto es suficiente y
-- mas simple.
