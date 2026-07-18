"""CRUD + traversal del Knowledge Graph. BP-0007 (AD-CMP-04). WO-003 Sprint 1."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models.kg import KGAristaBackend, KGNodoBackend
from app.models.usuario import Usuario

router = APIRouter(prefix="/kg", tags=["knowledge-graph"])


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
