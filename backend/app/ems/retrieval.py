"""
Retrieval — Sistema de recuperación de conocimiento híbrido.

Combina SQL (datos estructurados), Vector Search (búsqueda semántica),
y Knowledge Graph (relaciones) para recuperar contexto relevante.
"""

from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.ems.models import EMSDocument, EMSChunk, KnowledgeFact
from app.ems.providers import (
    EmbeddingProvider, VectorStoreProvider, SearchResult
)


@dataclass
class RetrievalResult:
    """Resultado de la recuperación de conocimiento."""
    query: str
    chunks: list[dict] = field(default_factory=list)
    facts: list[dict] = field(default_factory=list)
    documents: list[dict] = field(default_factory=list)
    total_results: int = 0
    sources: list[str] = field(default_factory=list)
    context_text: str = ""


class HybridRetriever:
    """
    Recuperador híbrido que combina:
    - SQL: Búsqueda por exact match en metadata
    - Vector Search: Búsqueda semántica por similitud
    - Knowledge Graph: Hechos y relaciones
    """

    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreProvider,
    ):
        self.db = db
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def retrieve(
        self,
        company_id: str,
        query: str,
        top_k: int = 5,
        include_facts: bool = True,
        include_documents: bool = True,
    ) -> RetrievalResult:
        """
        Recupera conocimiento relevante para una query.
        
        Combina resultados de múltiples fuentes y los rankea.
        """
        result = RetrievalResult(query=query)

        # 1. Vector Search (búsqueda semántica)
        query_embedding = self.embedding_provider.embed_query(query)
        vector_results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
            filter_metadata={"company_id": company_id},
        )

        for vr in vector_results:
            result.chunks.append({
                "id": vr.id,
                "text": vr.text,
                "score": vr.score,
                "source": "vector_search",
                "metadata": vr.metadata,
            })
            result.sources.append("vector_search")

        # 2. SQL Search (búsqueda por keywords en contenido)
        sql_results = self._sql_search(company_id, query, top_k)
        for sr in sql_results:
            # Evitar duplicados con vector search
            if not any(c["id"] == sr["id"] for c in result.chunks):
                result.chunks.append(sr)
                result.sources.append("sql_search")

        # 3. Knowledge Facts (si está habilitado)
        if include_facts:
            facts = self._get_facts(company_id, query)
            result.facts = facts
            if facts:
                result.sources.append("knowledge_facts")

        # 4. Documentos recientes (si está habilitado)
        if include_documents:
            docs = self._get_recent_documents(company_id, limit=3)
            result.documents = docs
            if docs:
                result.sources.append("recent_documents")

        # 5. Construir contexto combinado
        result.total_results = len(result.chunks) + len(result.facts) + len(result.documents)
        result.context_text = self._build_context(result)

        return result

    def _sql_search(
        self, company_id: str, query: str, limit: int
    ) -> list[dict]:
        """Búsqueda SQL por keywords en chunks."""
        # Buscar chunks que contengan palabras clave de la query
        keywords = [w for w in query.lower().split() if len(w) > 3]

        if not keywords:
            return []

        # Construir filtro LIKE para cada keyword
        from sqlalchemy import or_
        conditions = []
        for keyword in keywords[:5]:  # Máximo 5 keywords
            conditions.append(EMSChunk.content.ilike(f"%{keyword}%"))

        chunks = (
            self.db.query(EMSChunk)
            .join(EMSDocument, EMSChunk.document_id == EMSDocument.id)
            .filter(EMSChunk.company_id == company_id)
            .filter(EMSDocument.status != "archived")
            .filter(or_(*conditions))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": chunk.id,
                "text": chunk.content,
                "score": 0.5,  # Score base para SQL search
                "source": "sql_search",
                "metadata": {"document_id": chunk.document_id, "chunk_index": chunk.chunk_index},
            }
            for chunk in chunks
        ]

    def _get_facts(self, company_id: str, query: str) -> list[dict]:
        """Obtiene hechos relevantes del Knowledge Graph."""
        keywords = [w for w in query.lower().split() if len(w) > 3]

        if not keywords:
            return []

        from sqlalchemy import or_
        conditions = []
        for keyword in keywords[:5]:
            conditions.append(KnowledgeFact.subject.ilike(f"%{keyword}%"))
            conditions.append(KnowledgeFact.predicate.ilike(f"%{keyword}%"))
            conditions.append(KnowledgeFact.object_value.ilike(f"%{keyword}%"))

        facts = (
            self.db.query(KnowledgeFact)
            .filter(KnowledgeFact.company_id == company_id)
            .filter(KnowledgeFact.is_active == True)
            .filter(or_(*conditions))
            .limit(10)
            .all()
        )

        return [
            {
                "id": fact.id,
                "type": fact.fact_type,
                "subject": fact.subject,
                "predicate": fact.predicate,
                "object": fact.object_value,
                "confidence": fact.confidence,
                "source": fact.source,
            }
            for fact in facts
        ]

    def _get_recent_documents(self, company_id: str, limit: int) -> list[dict]:
        """Obtiene documentos recientes de la empresa."""
        docs = (
            self.db.query(EMSDocument)
            .filter(EMSDocument.company_id == company_id)
            .filter(EMSDocument.status == "processed")
            .order_by(EMSDocument.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": doc.id,
                "title": doc.title,
                "source_type": doc.source_type,
                "version": doc.version,
                "confidence": doc.confidence,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
            }
            for doc in docs
        ]

    def _build_context(self, result: RetrievalResult) -> str:
        """Construye el contexto combinado de todas las fuentes."""
        parts = []

        # Chunks más relevantes
        if result.chunks:
            parts.append("CONOCIMIENTO RECUPERADO:")
            for i, chunk in enumerate(result.chunks[:5], 1):
                score = chunk.get("score", 0)
                text = chunk.get("text", "")[:300]
                parts.append(f"  [{i}] (score: {score:.2f}) {text}")

        # Hechos
        if result.facts:
            parts.append("\nHECHOS CONOCIDOS:")
            for fact in result.facts[:5]:
                subj = fact.get("subject", "")
                pred = fact.get("predicate", "")
                obj = fact.get("object", "")
                conf = fact.get("confidence", 0)
                parts.append(f"  - {subj} {pred} {obj} (confianza: {conf:.0%})")

        # Documentos
        if result.documents:
            parts.append("\nDOCUMENTOS DISPONIBLES:")
            for doc in result.documents:
                title = doc.get("title", "")
                stype = doc.get("source_type", "")
                ver = doc.get("version", 1)
                parts.append(f"  - {title} ({stype}, v{ver})")

        return "\n".join(parts) if parts else "Sin conocimiento disponible."
