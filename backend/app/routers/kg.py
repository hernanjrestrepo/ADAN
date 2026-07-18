"""CRUD + traversal del Knowledge Graph. BP-0007 (AD-CMP-04). WO-003 Sprint 1."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.embeddings import embed_text
from app.models.kg import KGAristaBackend, KGNodoBackend, MemoriaSemanticaBackend
from app.models.usuario import Usuario

router = APIRouter(prefix="/kg", tags=["knowledge-graph"])

GRAPH_BOOST_PENALTY = 0.3  # ver ai/memory/hybrid_query.py - misma constante, mismo criterio


class CreateNodeRequest(BaseModel):
    tipo: str
    nombre: str
    proyecto_id: str | None = None
    atributos: dict | None = None


class CreateEdgeRequest(BaseModel):
    origen_id: str
    destino_id: str
    tipo_relacion: str
    atributos: dict | None = None


class NodeResponse(BaseModel):
    id: str
    tipo: str
    nombre: str
    proyecto_id: str | None
    atributos: dict | None


class EdgeResponse(BaseModel):
    id: str
    origen_id: str
    destino_id: str
    tipo_relacion: str


class TraverseResponse(BaseModel):
    nodos: list[NodeResponse]
    aristas: list[EdgeResponse]


def _node_to_response(n: KGNodoBackend) -> NodeResponse:
    return NodeResponse(
        id=str(n.id),
        tipo=n.tipo,
        nombre=n.nombre,
        proyecto_id=str(n.proyecto_id) if n.proyecto_id else None,
        atributos=n.atributos,
    )


def _edge_to_response(e: KGAristaBackend) -> EdgeResponse:
    return EdgeResponse(
        id=str(e.id), origen_id=str(e.origen_id), destino_id=str(e.destino_id), tipo_relacion=e.tipo_relacion
    )


@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(
    payload: CreateNodeRequest, db: Session = Depends(get_db), _user: Usuario = Depends(get_current_user)
) -> NodeResponse:
    node = KGNodoBackend(
        tipo=payload.tipo,
        nombre=payload.nombre,
        proyecto_id=uuid.UUID(payload.proyecto_id) if payload.proyecto_id else None,
        atributos=payload.atributos,
        created_at=datetime.now(UTC),
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return _node_to_response(node)


@router.post("/edges", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
def create_edge(
    payload: CreateEdgeRequest, db: Session = Depends(get_db), _user: Usuario = Depends(get_current_user)
) -> EdgeResponse:
    edge = KGAristaBackend(
        origen_id=uuid.UUID(payload.origen_id),
        destino_id=uuid.UUID(payload.destino_id),
        tipo_relacion=payload.tipo_relacion,
        atributos=payload.atributos,
        created_at=datetime.now(UTC),
    )
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return _edge_to_response(edge)


class IngestMemoryRequest(BaseModel):
    contenido: str
    origen: str = "documento"
    proyecto_id: str | None = None
    nodo_id: str | None = None


class IngestMemoryResponse(BaseModel):
    id: str


@router.post("/memory", response_model=IngestMemoryResponse, status_code=status.HTTP_201_CREATED)
def ingest_memory(
    payload: IngestMemoryRequest, db: Session = Depends(get_db), _user: Usuario = Depends(get_current_user)
) -> IngestMemoryResponse:
    """Indexa un texto para busqueda semantica real - via la API, sin pasar por un Agente.
    Sin chunking (a diferencia de ai/memory/ingestion.py, usado por el runtime de agentes)
    - para documentos largos, el chunking real sigue viviendo en /ai (Sprint 2); este
    endpoint cubre el caso simple de indexar un hecho o fragmento ya acotado desde la UI
    de exploracion (Sprint 5)."""
    embedding = embed_text(payload.contenido)
    row = MemoriaSemanticaBackend(
        contenido=payload.contenido,
        origen=payload.origen,
        embedding=embedding,
        proyecto_id=uuid.UUID(payload.proyecto_id) if payload.proyecto_id else None,
        nodo_id=uuid.UUID(payload.nodo_id) if payload.nodo_id else None,
        created_at=datetime.now(UTC),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return IngestMemoryResponse(id=str(row.id))


@router.get("/nodes/{node_id}", response_model=NodeResponse)
def get_node(
    node_id: str, db: Session = Depends(get_db), _user: Usuario = Depends(get_current_user)
) -> NodeResponse:
    node = db.query(KGNodoBackend).filter(KGNodoBackend.id == node_id).first()
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return _node_to_response(node)


@router.get("/proyectos/{proyecto_id}/nodes", response_model=list[NodeResponse])
def list_nodes_by_proyecto(
    proyecto_id: str, db: Session = Depends(get_db), _user: Usuario = Depends(get_current_user)
) -> list[NodeResponse]:
    nodes = (
        db.query(KGNodoBackend)
        .filter(KGNodoBackend.proyecto_id == proyecto_id)
        .order_by(KGNodoBackend.created_at.desc())
        .all()
    )
    return [_node_to_response(n) for n in nodes]


def _traverse_from(db: Session, node_id: str, max_depth: int) -> dict[str, KGNodoBackend]:
    """BFS acotado - devuelve solo los nodos visitados (id -> objeto), que es lo unico
    que necesita /kg/query. El endpoint /nodes/{id}/traverse hace su propia pasada
    completa (nodos+aristas) mas abajo, sin compartir esta funcion, para no acoplar
    dos formas de uso con requisitos de retorno distintos."""
    visited_nodes: dict[str, KGNodoBackend] = {}
    frontier = [node_id]
    for _ in range(max_depth + 1):
        if not frontier:
            break
        next_frontier: list[str] = []
        for nid in frontier:
            if nid in visited_nodes:
                continue
            node = db.query(KGNodoBackend).filter(KGNodoBackend.id == nid).first()
            if node is None:
                continue
            visited_nodes[nid] = node
            edges = (
                db.query(KGAristaBackend)
                .filter((KGAristaBackend.origen_id == nid) | (KGAristaBackend.destino_id == nid))
                .all()
            )
            for edge in edges:
                neighbor = str(edge.destino_id) if str(edge.origen_id) == nid else str(edge.origen_id)
                if neighbor not in visited_nodes:
                    next_frontier.append(neighbor)
        frontier = next_frontier
    return visited_nodes


@router.get("/nodes/{node_id}/traverse", response_model=TraverseResponse)
def traverse_from_node(
    node_id: str,
    max_depth: int = 2,
    db: Session = Depends(get_db),
    _user: Usuario = Depends(get_current_user),
) -> TraverseResponse:
    start = db.query(KGNodoBackend).filter(KGNodoBackend.id == node_id).first()
    if start is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    visited_nodes: dict[str, KGNodoBackend] = {}
    visited_edges: dict[str, KGAristaBackend] = {}
    frontier = [node_id]

    for _ in range(max_depth + 1):
        if not frontier:
            break
        next_frontier: list[str] = []
        for nid in frontier:
            if nid in visited_nodes:
                continue
            node = db.query(KGNodoBackend).filter(KGNodoBackend.id == nid).first()
            if node is None:
                continue
            visited_nodes[nid] = node
            edges = (
                db.query(KGAristaBackend)
                .filter((KGAristaBackend.origen_id == nid) | (KGAristaBackend.destino_id == nid))
                .all()
            )
            for edge in edges:
                visited_edges[str(edge.id)] = edge
                neighbor = str(edge.destino_id) if str(edge.origen_id) == nid else str(edge.origen_id)
                if neighbor not in visited_nodes:
                    next_frontier.append(neighbor)
        frontier = next_frontier

    return TraverseResponse(
        nodos=[_node_to_response(n) for n in visited_nodes.values()],
        aristas=[_edge_to_response(e) for e in visited_edges.values()],
    )


class HybridResultResponse(BaseModel):
    contenido: str
    origen: str  # "semantico" | "grafo"
    distance: float
    nodo_id: str | None


@router.get("/query", response_model=list[HybridResultResponse])
def hybrid_query(
    q: str,
    proyecto_id: str | None = None,
    top_k: int = 5,
    graph_depth: int = 1,
    db: Session = Depends(get_db),
    _user: Usuario = Depends(get_current_user),
) -> list[HybridResultResponse]:
    """Combina busqueda semantica (pgvector cosine_distance) + traversal del grafo desde
    los mejores resultados semanticos - misma logica que ai/memory/hybrid_query.py,
    reimplementada aqui sobre los modelos espejo del backend (sin import cruzado,
    Plan Maestro SS3.2). Ver docstring de ese modulo para la justificacion completa."""
    query_embedding = embed_text(q)

    semantic_q = db.query(
        MemoriaSemanticaBackend,
        MemoriaSemanticaBackend.embedding.cosine_distance(query_embedding).label("distance"),
    )
    if proyecto_id is not None:
        semantic_q = semantic_q.filter(MemoriaSemanticaBackend.proyecto_id == proyecto_id)
    semantic_hits = semantic_q.order_by("distance").limit(top_k).all()

    results: list[HybridResultResponse] = []
    seen_node_ids: set[str] = set()
    worst_distance = 0.0

    for row, distance in semantic_hits:
        results.append(
            HybridResultResponse(
                contenido=row.contenido,
                origen="semantico",
                distance=float(distance),
                nodo_id=str(row.nodo_id) if row.nodo_id else None,
            )
        )
        worst_distance = max(worst_distance, float(distance))
        if row.nodo_id:
            seen_node_ids.add(str(row.nodo_id))

    graph_boost_distance = worst_distance + GRAPH_BOOST_PENALTY
    already_added = set(seen_node_ids)
    for node_id in list(seen_node_ids):
        subgraph = _traverse_from(db, node_id, graph_depth)
        for nid, node in subgraph.items():
            if nid in already_added:
                continue
            already_added.add(nid)
            results.append(
                HybridResultResponse(
                    contenido=node.nombre, origen="grafo", distance=graph_boost_distance, nodo_id=nid
                )
            )

    results.sort(key=lambda r: r.distance)
    return results
