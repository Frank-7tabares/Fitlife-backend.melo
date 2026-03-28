from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional

class MessageType(str, Enum):
    INSTRUCTOR_MESSAGE = 'INSTRUCTOR_MESSAGE'
    USER_MESSAGE = 'USER_MESSAGE'
    SYSTEM_NOTIFICATION = 'SYSTEM_NOTIFICATION'

@dataclass
class Message:
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    content: str
    message_type: MessageType
    is_read: bool = False
    created_at: datetime = None
    subject: Optional[str] = None
    read_at: Optional[datetime] = None
