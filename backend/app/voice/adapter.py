"""
Voice Adapter — Adaptador de voz que reutiliza el proyecto Claro.

NO desarrolla voz. Solo adapta la interfaz existente.
"""

import abc
from dataclasses import dataclass
from typing import Any


@dataclass
class VoiceResult:
    """Resultado de operación de voz."""
    status: str
    output: Any = None
    error: str | None = None
    duration_ms: int = 0


class VoiceAdapter(abc.ABC):
    """Interfaz para adaptadores de voz."""

    @abc.abstractmethod
    async def stt(self, audio_data: bytes, language: str = "es") -> VoiceResult:
        """Speech-to-Text: convierte audio a texto."""
        ...

    @abc.abstractmethod
    async def tts(self, text: str, voice: str = "default") -> VoiceResult:
        """Text-to-Speech: convierte texto a audio."""
        ...

    @abc.abstractmethod
    async def health(self) -> dict:
        """Verifica salud del servicio de voz."""
        ...


class ClaroVoiceAdapter(VoiceAdapter):
    """
    Adaptador que reutiliza el proyecto Claro.
    
    NO desarrolla voz. Solo adapta la interfaz.
    En producción, esto conectaría con el proyecto Claro.
    """

    def __init__(self):
        self._connected = False

    async def stt(self, audio_data: bytes, language: str = "es") -> VoiceResult:
        # En producción: conectar con Claro STT
        return VoiceResult(
            status="success",
            output={"text": "[Audio transcrito por Claro]", "language": language},
            duration_ms=100,
        )

    async def tts(self, text: str, voice: str = "default") -> VoiceResult:
        # En producción: conectar con Claro TTS
        return VoiceResult(
            status="success",
            output={"audio_url": "[URL de audio generado por Claro]", "text": text},
            duration_ms=150,
        )

    async def health(self) -> dict:
        return {"status": "healthy", "adapter": "claro", "connected": self._connected}
