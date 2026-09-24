"""
Chunking — División de texto en chunks para búsqueda semántica.
"""

import hashlib
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """Un chunk de texto."""
    content: str
    index: int
    token_count: int
    content_hash: str
    metadata: dict = field(default_factory=dict)


class TextChunker:
    """
    Chunker de texto que divide documentos en piezas manejables.
    
    Estrategia: chunking por tamaño con overlap para preservar contexto.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 50,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        """Divide el texto en chunks."""
        if not text or not text.strip():
            return []

        # Limpiar texto
        text = self._clean_text(text)

        # Si el texto es corto, retornar un solo chunk
        if len(text.split()) <= self.chunk_size:
            return [Chunk(
                content=text,
                index=0,
                token_count=len(text.split()),
                content_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
                metadata=metadata or {},
            )]

        # Dividir en chunks con overlap
        chunks = []
        words = text.split()
        start = 0
        chunk_index = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            # Solo agregar si cumple tamaño mínimo
            if len(chunk_words) >= self.min_chunk_size:
                chunks.append(Chunk(
                    content=chunk_text,
                    index=chunk_index,
                    token_count=len(chunk_words),
                    content_hash=hashlib.sha256(chunk_text.encode()).hexdigest()[:16],
                    metadata={**(metadata or {}), "chunk_range": f"{start}-{end}"},
                ))
                chunk_index += 1

            # Avanzar con overlap
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def _clean_text(self, text: str) -> str:
        """Limpia el texto de caracteres no deseados."""
        import re
        # Eliminar múltiples espacios
        text = re.sub(r'\s+', ' ', text)
        # Eliminar líneas vacías múltiples
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
