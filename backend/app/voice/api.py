"""
Voice API — Endpoints para integración de voz.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.models import User
from app.voice.adapter import ClaroVoiceAdapter

router = APIRouter(prefix="/voice", tags=["voice"])

_adapter = ClaroVoiceAdapter()


class STTRequest(BaseModel):
    audio_base64: str
    language: str = "es"


class TTSRequest(BaseModel):
    text: str
    voice: str = "default"


@router.post("/stt")
async def speech_to_text(
    request: STTRequest,
    current_user: User = Depends(get_current_user),
):
    """Convierte audio a texto (Speech-to-Text)."""
    import base64
    audio_data = base64.b64decode(request.audio_base64)
    result = await _adapter.stt(audio_data, request.language)
    return {"status": result.status, "text": result.output.get("text", ""), "duration_ms": result.duration_ms}


@router.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """Convierte texto a audio (Text-to-Speech)."""
    result = await _adapter.tts(request.text, request.voice)
    return {"status": result.status, "audio_url": result.output.get("audio_url", ""), "duration_ms": result.duration_ms}


@router.get("/health")
async def voice_health():
    return await _adapter.health()
