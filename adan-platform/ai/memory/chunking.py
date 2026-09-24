"""Chunking simple de texto para ingesta en memoria semantica. Por parrafos, con limite
de tamano y overlap - suficiente para documentos de negocio (Diagnosticos, Planes) sin
necesitar un tokenizer real todavia (Economia Conceptual: no anadir esa dependencia sin
evidencia de que el chunking por caracteres no alcanza)."""

CHUNK_SIZE = 800  # caracteres, aproximacion razonable a ~200 tokens
CHUNK_OVERLAP = 100


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide el texto en fragmentos de hasta `chunk_size` caracteres, respetando limites
    de parrafo cuando es posible, con `overlap` caracteres de solapamiento entre fragmentos
    consecutivos para no perder contexto en el borde."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
        if len(paragraph) > chunk_size:
            # parrafo demasiado largo por si solo - se corta en bloques con overlap
            start = 0
            while start < len(paragraph):
                chunks.append(paragraph[start : start + chunk_size])
                start += chunk_size - overlap
            current = ""
        else:
            current = paragraph

    if current:
        chunks.append(current)

    return chunks
