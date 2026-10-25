"""Lo que no es texto: imágenes y capturas (OCR con la visión de Kimi), PDFs escaneados y grabaciones de audio o
video (transcripción local con Whisper: el audio no sale del servidor).

- Imágenes: Kimi transcribe todo el texto y describe tablas, gráficos y lo que se ve.
- PDF escaneado: cada página es una imagen; se leen las primeras páginas con la misma visión.
- Audio y video: faster-whisper en el servidor, en español por defecto; tarda, por eso corre aparte.
"""
from __future__ import annotations

import asyncio
import base64
import io
import logging

import httpx

from app.ai.kimi_adapter import KIMI_TEMPERATURE
from app.core.config import settings

logger = logging.getLogger(__name__)

IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
               ".gif": "image/gif"}
AUDIO_EXT = {".mp3", ".m4a", ".wav", ".ogg", ".opus", ".aac", ".flac", ".amr"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".3gp"}
MAX_PDF_OCR_PAGES = 12

OCR_PROMPT = (
    "Lee esta imagen para un consultor de empresas. 1) Transcribe TODO el texto que aparece, tal cual, conservando "
    "cifras y tablas (usa tablas Markdown si las hay). 2) Si hay gráficos, diagramas o fotos, describe en pocas "
    "líneas qué muestran y los datos clave. Español. No inventes nada que no se vea."
)


class MediaError(RuntimeError):
    pass


def can_see() -> bool:
    return bool(settings.KIMI_API_KEY)


async def ocr_image(data: bytes, mime: str, prompt: str | None = None) -> str:
    """Texto y descripción de una imagen con la visión de Kimi (o lo que pida `prompt`)."""
    if not can_see():
        raise MediaError("La lectura de imágenes no está disponible en este momento.")
    # Como en el adaptador: sin «thinking» Kimi k2.6 acepta temperatura distinta de 1
    body = {"model": settings.KIMI_MODEL, "max_tokens": 3000, "temperature": KIMI_TEMPERATURE, "thinking": {"type": "disabled"},
            "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64.b64encode(data).decode()}"}},
        {"type": "text", "text": prompt or OCR_PROMPT}]}]}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{settings.KIMI_BASE_URL.rstrip('/')}/chat/completions", json=body,
                              headers={"Authorization": f"Bearer {settings.KIMI_API_KEY}"})
    if r.status_code != 200:
        raise MediaError(f"No se pudo leer la imagen (código {r.status_code}).")
    return (r.json()["choices"][0]["message"].get("content") or "").strip()


def _pdf_page_images(data: bytes) -> list[tuple[bytes, str]]:
    from pypdf import PdfReader
    out = []
    for page in PdfReader(io.BytesIO(data)).pages[:MAX_PDF_OCR_PAGES]:
        try:
            imgs = list(page.images)
        except Exception:  # noqa: BLE001 - una página rara no detiene el resto
            continue
        if not imgs:
            continue
        biggest = max(imgs, key=lambda im: len(im.data))
        name = biggest.name.lower()
        mime = "image/png" if name.endswith(".png") else "image/jpeg"
        out.append((biggest.data, mime))
    return out


async def ocr_pdf(data: bytes) -> tuple[str, int]:
    """OCR de un PDF escaneado: devuelve el texto y cuántas páginas se leyeron."""
    pages = _pdf_page_images(data)
    if not pages:
        return "", 0
    sem = asyncio.Semaphore(4)

    async def one(i: int, img: bytes, mime: str) -> str:
        async with sem:
            try:
                return f"--- Página {i + 1} ---\n" + await ocr_image(img, mime)
            except MediaError as exc:
                return f"--- Página {i + 1} --- [{exc}]"

    texts = await asyncio.gather(*(one(i, img, mime) for i, (img, mime) in enumerate(pages)))
    return "\n\n".join(texts), len(pages)


_whisper = None


def transcribe(path: str) -> str:
    """Transcribe audio o video en el servidor (faster-whisper). Bloquea: se llama en un hilo aparte."""
    global _whisper
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise MediaError("La transcripción de grabaciones no está instalada en este servidor.") from exc
    if _whisper is None:
        _whisper = WhisperModel(settings.WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, info = _whisper.transcribe(path, language=settings.WHISPER_LANGUAGE or None, vad_filter=True,
                                         beam_size=1)
    lines = []
    for seg in segments:
        m, s = divmod(int(seg.start), 60)
        lines.append(f"[{m:02d}:{s:02d}] {seg.text.strip()}")
    text = "\n".join(lines)
    logger.info("Transcripción lista: %s s de audio, idioma %s", round(info.duration), info.language)
    return text
