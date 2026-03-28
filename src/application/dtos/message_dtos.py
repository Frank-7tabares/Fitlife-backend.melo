from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.domain.entities.message import MessageType

class SendMessageRequest(BaseModel):
    recipient_id: UUID
    subject: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: MessageType = MessageType.INSTRUCTOR_MESSAGE

class MessageResponse(BaseModel):
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
    total: int
    unread_count: int
    messages: List[MessageResponse]

class ConversationResponse(BaseModel):
    peer_id: UUID
    messages: List[MessageResponse]

class InboxThreadItem(BaseModel):
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
    message_id: UUID
