"""
Omnichannel API — Endpoints para plataforma omnichannel.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.models import User
from app.omnichannel.channels import (
    ChannelManager, WebChatChannel, WhatsAppChannel,
    TelegramChannel, EmailChannel,
)

router = APIRouter(prefix="/omnichannel", tags=["omnichannel"])

_manager = ChannelManager()
_manager.register(WebChatChannel())
_manager.register(WhatsAppChannel())
_manager.register(TelegramChannel())
_manager.register(EmailChannel())


class MessageRequest(BaseModel):
    channel: str
    data: dict


class ResponseRequest(BaseModel):
    channel: str
    recipient_id: str
    content: str
    content_type: str = "text"


@router.get("/channels")
async def list_channels(current_user: User = Depends(get_current_user)):
    """Lista canales disponibles."""
    return {"channels": _manager.list_channels()}


@router.post("/receive")
async def receive_message(
    request: MessageRequest,
    current_user: User = Depends(get_current_user),
):
    """Recibe un mensaje de un canal."""
    message = await _manager.receive(request.channel, request.data)
    return {
        "id": message.id,
        "channel": message.channel,
        "sender_id": message.sender_id,
        "content": message.content,
        "content_type": message.content_type,
    }


@router.post("/respond")
async def respond_message(
    request: ResponseRequest,
    current_user: User = Depends(get_current_user),
):
    """Envía una respuesta a un canal."""
    from app.omnichannel.channels import ChannelResponse
    response = ChannelResponse(
        channel=request.channel,
        recipient_id=request.recipient_id,
        content=request.content,
        content_type=request.content_type,
    )
    result = await _manager.respond(request.channel, response)
    return {"delivered": result}


@router.get("/health/{channel_id}")
async def channel_health(channel_id: str, current_user: User = Depends(get_current_user)):
    return await _manager.health(channel_id)


@router.get("/health")
async def omnichannel_health():
    return {"status": "healthy", "channels": _manager.list_channels(), "version": "0.1.0-wo012"}
