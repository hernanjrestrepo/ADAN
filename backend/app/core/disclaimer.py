"""Aviso de IA (AD-DEC-0002, decisión 6).

Se muestra en la interfaz, al final de cada documento generado y en las respuestas de la API.
"""

AI_DISCLAIMER = (
    "ADÁN es una inteligencia artificial. Sus análisis y recomendaciones no reemplazan "
    "la asesoría de profesionales (legal, tributaria, financiera u otra), y Paradixe no se "
    "hace responsable por los resultados de las decisiones que se tomen con base en ellos."
)

_DOCUMENT_MARKER = "\n\n---\n\n> ⚠️ "


def with_disclaimer(markdown: str) -> str:
    """Agrega el aviso al final de un documento generado."""
    return f"{markdown.rstrip()}{_DOCUMENT_MARKER}{AI_DISCLAIMER}\n"


def strip_disclaimer(markdown: str) -> str:
    """Quita el aviso para evaluar solo el contenido (ej. Gate Review)."""
    return markdown.split(_DOCUMENT_MARKER, 1)[0]
