"""Modelo de base de datos: Mensaje (Historia 7 - Mensajería)."""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid
from src.domain.entities.message import MessageType


class MessageModel(Base):
    """Modelo de mensaje en base de datos.
    
    Tablas relacionadas:
    - Sender (user_id -> users.id)
    - Recipient (user_id -> users.id)
    """
    __tablename__ = "messages"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(255), nullable=True)
    content = Column(String(2000), nullable=False)
    message_type = Column(String(50), nullable=False)  # INSTRUCTOR_MESSAGE, SYSTEM_NOTIFICATION
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    read_at = Column(DateTime, nullable=True)
