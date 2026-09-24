"""Repositorio del Knowledge Graph: CRUD de nodos/aristas + traversal simple.
BFS acotado en profundidad - suficiente para un grafo de conocimiento por Proyecto,
que no crece sin limite (a diferencia de un grafo social); si el volumen real lo exige,
se revisita con evidencia, no antes (Economia Conceptual)."""

import uuid

from sqlalchemy.orm import Session

from memory.models import KGArista, KGNodo


def create_node(
    db: Session, tipo: str, nombre: str, proyecto_id: uuid.UUID | None = None, atributos: dict | None = None
) -> KGNodo:
    node = KGNodo(tipo=tipo, nombre=nombre, proyecto_id=proyecto_id, atributos=atributos)
    db.add(node)
    db.flush()
    return node


def create_edge(
    db: Session, origen_id: uuid.UUID, destino_id: uuid.UUID, tipo_relacion: str, atributos: dict | None = None
) -> KGArista:
    edge = KGArista(
        origen_id=origen_id, destino_id=destino_id, tipo_relacion=tipo_relacion, atributos=atributos
    )
    db.add(edge)
    db.flush()
    return edge


def get_node(db: Session, node_id: uuid.UUID) -> KGNodo | None:
    return db.query(KGNodo).filter(KGNodo.id == node_id).first()


def list_nodes_by_proyecto(db: Session, proyecto_id: uuid.UUID, tipo: str | None = None) -> list[KGNodo]:
    query = db.query(KGNodo).filter(KGNodo.proyecto_id == proyecto_id)
    if tipo:
        query = query.filter(KGNodo.tipo == tipo)
    return query.order_by(KGNodo.created_at.desc()).all()


def traverse(db: Session, start_node_id: uuid.UUID, max_depth: int = 2) -> dict:
    """BFS desde start_node_id hasta max_depth. Devuelve {nodos: [...], aristas: [...]}
    - todos los nodos y aristas alcanzados, sin duplicados."""
    visited_nodes: dict[uuid.UUID, KGNodo] = {}
    visited_edges: dict[uuid.UUID, KGArista] = {}
    frontier = [start_node_id]

    for _ in range(max_depth + 1):
        if not frontier:
            break
        next_frontier: list[uuid.UUID] = []
        for node_id in frontier:
            if node_id in visited_nodes:
                continue
            node = get_node(db, node_id)
            if node is None:
                continue
            visited_nodes[node_id] = node

            edges = (
                db.query(KGArista)
                .filter((KGArista.origen_id == node_id) | (KGArista.destino_id == node_id))
                .all()
            )
            for edge in edges:
                visited_edges[edge.id] = edge
                neighbor_id = edge.destino_id if edge.origen_id == node_id else edge.origen_id
                if neighbor_id not in visited_nodes:
                    next_frontier.append(neighbor_id)
        frontier = next_frontier

    return {"nodos": list(visited_nodes.values()), "aristas": list(visited_edges.values())}
