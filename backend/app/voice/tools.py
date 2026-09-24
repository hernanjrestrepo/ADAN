"""
Voice Tools — Herramientas TEF para voz.
"""

from app.tef.interfaces import ToolProvider, ToolMetadata, ToolContext, ToolResult
from app.voice.adapter import ClaroVoiceAdapter

_adapter = ClaroVoiceAdapter()


class STTTool(ToolProvider):
    """Herramienta de Speech-to-Text."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="speech_to_text",
            name="Speech-to-Text",
            description="Convierte audio a texto",
            category="voice",
            permissions=["voice:stt"],
            inputs={"audio_base64": {"type": "string", "description": "Audio en base64", "required": True}},
            outputs={"text": {"type": "string", "description": "Texto transcrito"}},
            timeout_seconds=30,
            tags=["voice", "stt", "transcribe", "audio"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        import base64
        audio = base64.b64decode(params["audio_base64"])
        result = await _adapter.stt(audio)
        return ToolResult(tool_id="speech_to_text", status=result.status, output=result.output)


class TTSTool(ToolProvider):
    """Herramienta de Text-to-Speech."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="text_to_speech",
            name="Text-to-Speech",
            description="Convierte texto a audio",
            category="voice",
            permissions=["voice:tts"],
            inputs={"text": {"type": "string", "description": "Texto a convertir", "required": True}},
            outputs={"audio_url": {"type": "string", "description": "URL del audio generado"}},
            timeout_seconds=30,
            tags=["voice", "tts", "speak", "audio"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        result = await _adapter.tts(params["text"])
        return ToolResult(tool_id="text_to_speech", status=result.status, output=result.output)
