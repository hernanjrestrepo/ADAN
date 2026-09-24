"""
Provider Interfaces — Desacoplamiento del EMS del proveedor de embeddings y vector store.

Permite cambiar entre Qdrant, pgvector, Milvus, Weaviate, etc.
sin reescribir la lógica del Enterprise Memory System.
"""

import abc
from dataclasses import dataclass, field


# ============================================================
# Embedding Provider Interface
# ============================================================

class EmbeddingProvider(abc.ABC):
    """Interfaz abstracta para generar embeddings."""

    @abc.abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings para una lista de textos."""
        ...

    @abc.abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Genera embedding para una query de búsqueda."""
        ...

    @abc.abstractmethod
    def dimension(self) -> int:
        """Retorna la dimensión de los embeddings."""
        ...


# ============================================================
# Vector Store Provider Interface
# ============================================================

@dataclass
class VectorRecord:
    """Un registro en el vector store."""
    id: str
    vector: list[float]
    metadata: dict = field(default_factory=dict)
    text: str = ""


@dataclass
class SearchResult:
    """Resultado de búsqueda en el vector store."""
    id: str
    score: float
    text: str
    metadata: dict = field(default_factory=dict)


class VectorStoreProvider(abc.ABC):
    """Interfaz abstracta para almacenamiento vectorial."""

    @abc.abstractmethod
    def upsert(self, records: list[VectorRecord]) -> int:
        """Inserta o actualiza registros. Retorna cantidad procesada."""
        ...

    @abc.abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[SearchResult]:
        """Busca los registros más similares."""
        ...

    @abc.abstractmethod
    def delete(self, ids: list[str]) -> int:
        """Elimina registros por ID."""
        ...

    @abc.abstractmethod
    def count(self) -> int:
        """Retorna la cantidad de registros."""
        ...


# ============================================================
# Implementación Local (para desarrollo y testing)
# ============================================================

class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Implementación local de embeddings usando TF-IDF simplificado.
    Para producción, reemplazar con sentence-transformers o similar.
    """

    def __init__(self, dim: int = 128):
        self._dim = dim
        self._vocab: dict[str, int] = {}

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._text_to_vector(text) for text in texts]

    def embed_query(self, query: str) -> list[float]:
        return self._text_to_vector(query)

    def dimension(self) -> int:
        return self._dim

    def _text_to_vector(self, text: str) -> list[float]:
        """Convierte texto a vector usando hashing simplificado."""
        import hashlib
        words = text.lower().split()
        vector = [0.0] * self._dim

        for word in words:
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            idx = h % self._dim
            vector[idx] += 1.0

        # Normalizar
        norm = sum(x * x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector


class LocalVectorStoreProvider(VectorStoreProvider):
    """
    Implementación local de vector store en memoria.
    Para producción, reemplazar con Qdrant, pgvector, etc.
    """

    def __init__(self):
        self._records: dict[str, VectorRecord] = {}

    def upsert(self, records: list[VectorRecord]) -> int:
        for record in records:
            self._records[record.id] = record
        return len(records)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[SearchResult]:
        results = []
        for record in self._records.values():
            # Aplicar filtro de metadata
            if filter_metadata:
                match = all(
                    record.metadata.get(k) == v
                    for k, v in filter_metadata.items()
                )
                if not match:
                    continue

            # Calcular similitud coseno
            score = self._cosine_similarity(query_vector, record.vector)
            results.append(SearchResult(
                id=record.id,
                score=score,
                text=record.text,
                metadata=record.metadata,
            ))

        # Ordenar por score descendente
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def delete(self, ids: list[str]) -> int:
        count = 0
        for id in ids:
            if id in self._records:
                del self._records[id]
                count += 1
        return count

    def count(self) -> int:
        return len(self._records)

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calcula similitud coseno entre dos vectores."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
