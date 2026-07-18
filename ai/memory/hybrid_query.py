"""Consulta hibrida: busqueda semantica (pgvector) + traversal del grafo (kg_aristas),
combinadas en un solo ranking. WO-003 Sprint 3.

Por que hibrida y no solo semantica: dos hechos pueden estar relacionados en el grafo
(ej. "Competidor X" -afecta_a-> "Decision de bajar precios") sin que sus textos se
parezcan semanticamente. Una busqueda semantica pura se perderia esa conexion. El
traversal desde los mejores resultados semanticos rescata contexto relacionado que el
embedding por si solo no ve."""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from memory.repository import traverse
from memory.search import semantic_search
from models.base import ModelBackend

GRAPH_BOOST_PENALTY = 0.3  # los resultados por grafo entran con una distancia peor que
# el peor resultado semantico directo, para que el ranking los muestre despues, no antes


@dataclass
class HybridResult:
    contenido: str
    origen: str  # "semantico" | "grafo"
    distance: float  # menor = mejor. Los de "grafo" llevan una penalizacion fija.
    nodo_id: uuid.UUID | None = None


def hybrid_query(
    db: Session,
    model_backend: ModelBackend,
    query: str,
    proyecto_id: uuid.UUID | None = None,
    top_k_semantic: int = 5,
    graph_depth: int = 1,
) -> list[HybridResult]:
    semantic_hits = semantic_search(db, model_backend, query, proyecto_id=proyecto_id, top_k=top_k_semantic)

    results: list[HybridResult] = []
    seen_node_ids: set[uuid.UUID] = set()
    worst_semantic_distance = 0.0

    for row, distance in semantic_hits:
        results.append(
            HybridResult(contenido=row.contenido, origen="semantico", distance=distance, nodo_id=row.nodo_id)
        )
        worst_semantic_distance = max(worst_semantic_distance, distance)
        if row.nodo_id is not None:
            seen_node_ids.add(row.nodo_id)

    # Traversal desde cada nodo semanticamente relevante - rescata contexto conectado
    graph_boost_distance = worst_semantic_distance + GRAPH_BOOST_PENALTY
    already_added: set[uuid.UUID] = set(seen_node_ids)

    for node_id in list(seen_node_ids):
        subgraph = traverse(db, node_id, max_depth=graph_depth)
        for node in subgraph["nodos"]:
            if node.id in already_added:
                continue
            already_added.add(node.id)
            results.append(
                HybridResult(
                    contenido=node.nombre, origen="grafo", distance=graph_boost_distance, nodo_id=node.id
                )
            )

    results.sort(key=lambda r: r.distance)
    return results
