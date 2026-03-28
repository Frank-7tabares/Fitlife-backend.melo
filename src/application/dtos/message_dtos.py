"""DTOs para mensajería (Historia 7 - RF-088 a RF-094)."""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.domain.entities.message import MessageType


class SendMessageRequest(BaseModel):
    """Solicitud para enviar un mensaje (RF-088, RF-090)."""
    recipient_id: UUID
    subject: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: MessageType = MessageType.INSTRUCTOR_MESSAGE


class MessageResponse(BaseModel):
    """Respuesta de un mensaje individual (RF-089, RF-091)."""
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    subject: Optional[str]
    content: str
    message_type: MessageType
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]


class MessageListResponse(BaseModel):
    """Respuesta con listado de mensajes (RF-092)."""
    total: int
    unread_count: int
    messages: List[MessageResponse]


class ConversationResponse(BaseModel):
    """Hilo de chat entre el usuario actual y otro usuario (orden cronológico)."""
    peer_id: UUID
    messages: List[MessageResponse]


class InboxThreadItem(BaseModel):
    """Resumen de conversación para bandeja tipo inbox (coach/admin)."""
    peer_id: UUID
    peer_name: str
    peer_email: Optional[str] = None
    last_message_preview: str
    last_message_at: datetime
    last_message_from_me: bool
    unread_count: int


class CoachInboxResponse(BaseModel):
    threads: List[InboxThreadItem]


class MarkAsReadRequest(BaseModel):
    """Solicitud para marcar mensaje como leído (RF-091)."""
    message_id: UUID
