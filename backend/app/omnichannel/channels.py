"""
Omnichannel — Adaptadores de canales unificados.

Todos implementan: receive, normalize, route, respond, audit.
"""

import abc
import uuid
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ChannelMessage:
    """Mensaje normalizado de cualquier canal."""
    id: str
    channel: str                         # whatsapp, telegram, email, web, voice
    sender_id: str
    sender_name: str
    content: str
    content_type: str                    # text, image, audio, file
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)
    raw_data: Any = None


@dataclass
class ChannelResponse:
    """Respuesta normalizada para cualquier canal."""
    channel: str
    recipient_id: str
    content: str
    content_type: str = "text"
    metadata: dict = field(default_factory=dict)


class BaseChannel(abc.ABC):
    """Interfaz base para canales de comunicación."""

    @abc.abstractmethod
    async def receive(self, raw_data: Any) -> ChannelMessage:
        """Recibe y normaliza un mensaje del canal."""
        ...

    @abc.abstractmethod
    async def respond(self, response: ChannelResponse) -> bool:
        """Envía una respuesta al canal."""
        ...

    @abc.abstractmethod
    async def health(self) -> dict:
        """Verifica salud del canal."""
        ...

    @abc.abstractmethod
    def channel_id(self) -> str:
        """Identificador del canal."""
        ...


# ============================================================
# Web Chat Channel
# ============================================================

class WebChatChannel(BaseChannel):
    """Canal de chat web (WebSocket/HTTP)."""

    async def receive(self, raw_data: Any) -> ChannelMessage:
        return ChannelMessage(
            id=str(uuid.uuid4()),
            channel="web",
            sender_id=raw_data.get("user_id", "anonymous"),
            sender_name=raw_data.get("user_name", "Usuario Web"),
            content=raw_data.get("message", ""),
            content_type="text",
            metadata={"source": "web_chat"},
        )

    async def respond(self, response: ChannelResponse) -> bool:
        # En producción: enviar via WebSocket
        return True

    async def health(self) -> dict:
        return {"status": "healthy", "channel": "web"}

    def channel_id(self) -> str:
        return "web"


# ============================================================
# WhatsApp Channel
# ============================================================

class WhatsAppChannel(BaseChannel):
    """Canal de WhatsApp Business API."""

    async def receive(self, raw_data: Any) -> ChannelMessage:
        return ChannelMessage(
            id=raw_data.get("message_id", str(uuid.uuid4())),
            channel="whatsapp",
            sender_id=raw_data.get("from", ""),
            sender_name=raw_data.get("sender_name", ""),
            content=raw_data.get("text", {}).get("body", ""),
            content_type="text",
            raw_data=raw_data,
        )

    async def respond(self, response: ChannelResponse) -> bool:
        # En producción: WhatsApp Business API
        return True

    async def health(self) -> dict:
        return {"status": "healthy", "channel": "whatsapp"}

    def channel_id(self) -> str:
        return "whatsapp"


# ============================================================
# Telegram Channel
# ============================================================

class TelegramChannel(BaseChannel):
    """Canal de Telegram."""

    async def receive(self, raw_data: Any) -> ChannelMessage:
        msg = raw_data.get("message", {})
        return ChannelMessage(
            id=str(msg.get("message_id", uuid.uuid4())),
            channel="telegram",
            sender_id=str(msg.get("from", {}).get("id", "")),
            sender_name=msg.get("from", {}).get("first_name", ""),
            content=msg.get("text", ""),
            content_type="text",
            raw_data=raw_data,
        )

    async def respond(self, response: ChannelResponse) -> bool:
        # En producción: Telegram Bot API
        return True

    async def health(self) -> dict:
        return {"status": "healthy", "channel": "telegram"}

    def channel_id(self) -> str:
        return "telegram"


# ============================================================
# Email Channel
# ============================================================

class EmailChannel(BaseChannel):
    """Canal de email (IMAP/SMTP)."""

    async def receive(self, raw_data: Any) -> ChannelMessage:
        return ChannelMessage(
            id=raw_data.get("message_id", str(uuid.uuid4())),
            channel="email",
            sender_id=raw_data.get("from", ""),
            sender_name=raw_data.get("sender_name", ""),
            content=raw_data.get("body", ""),
            content_type="text",
            metadata={"subject": raw_data.get("subject", "")},
            raw_data=raw_data,
        )

    async def respond(self, response: ChannelResponse) -> bool:
        # En producción: SMTP
        return True

    async def health(self) -> dict:
        return {"status": "healthy", "channel": "email"}

    def channel_id(self) -> str:
        return "email"


# ============================================================
# Channel Manager
# ============================================================

class ChannelManager:
    """Gestor unificado de canales de comunicación."""

    def __init__(self):
        self._channels: dict[str, BaseChannel] = {}
        self._audit_log: list[dict] = []

    def register(self, channel: BaseChannel):
        """Registra un canal."""
        self._channels[channel.channel_id()] = channel

    async def receive(self, channel_id: str, raw_data: Any) -> ChannelMessage:
        """Recibe un mensaje de un canal."""
        channel = self._channels.get(channel_id)
        if not channel:
            raise ValueError(f"Channel '{channel_id}' not found")
        message = await channel.receive(raw_data)
        self._audit("receive", channel_id, message.id)
        return message

    async def respond(self, channel_id: str, response: ChannelResponse) -> bool:
        """Envía una respuesta a un canal."""
        channel = self._channels.get(channel_id)
        if not channel:
            return False
        result = await channel.respond(response)
        self._audit("respond", channel_id, response.recipient_id)
        return result

    async def health(self, channel_id: str) -> dict:
        channel = self._channels.get(channel_id)
        if not channel:
            return {"status": "not_found"}
        return await channel.health()

    def list_channels(self) -> list[str]:
        return list(self._channels.keys())

    def _audit(self, action: str, channel_id: str, entity_id: str):
        self._audit_log.append({
            "action": action,
            "channel": channel_id,
            "entity_id": entity_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
