"""Corpus demo para WO-003 Sprint 6: pobla el KG + memoria semantica con un caso de
negocio realista, para verificar el pipeline completo (grafo + embeddings reales +
consulta hibrida) de punta a punta contra infraestructura real.

Uso: cd ai && .venv/Scripts/python.exe ../scripts/seed_kg_corpus_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ai"))

from db import SessionLocal
from memory.hybrid_query import hybrid_query
from memory.ingestion import ingest_text
from memory.repository import create_edge, create_node
from models.ollama_adapter import OllamaBackend

CORPUS = [
    ("hecho", "Un competidor directo lanzo una version gratuita de su producto en marzo"),
    ("hecho", "Tres clientes cancelaron su suscripcion mencionando el precio como razon principal"),
    ("hecho", "El equipo de ventas propuso bajar el precio de entrada en un 20%"),
    ("hecho", "La junta directiva aprobo revisar la estrategia de precios en el proximo trimestre"),
]


def run() -> None:
    db = SessionLocal()
    backend = OllamaBackend()
    try:
        nodes = []
        for tipo, nombre in CORPUS:
            node = create_node(db, tipo=tipo, nombre=nombre)
            nodes.append(node)
        db.flush()

        # Conectar la cadena causal: competidor -> cancelaciones -> propuesta -> decision
        for i in range(len(nodes) - 1):
            create_edge(db, nodes[i].id, nodes[i + 1].id, "genero")
        db.flush()

        # Indexar cada hecho para busqueda semantica real
        for node in nodes:
            ingest_text(db, backend, node.nombre, origen="hecho", nodo_id=node.id)
        db.flush()
        db.commit()

        print(f"Corpus sembrado: {len(nodes)} hechos conectados e indexados.")

        # Demostracion real de consulta hibrida sobre el corpus
        results = hybrid_query(db, backend, "por que estamos perdiendo clientes", top_k_semantic=3)
        print("\nConsulta: 'por que estamos perdiendo clientes'")
        for r in results:
            print(f"  [{r.origen}, distancia={r.distance:.3f}] {r.contenido}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
