from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid

class ReminderModel(Base):
    __tablename__ = 'reminders'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    reminder_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    scheduled_time = Column(String(5), nullable=False)
    timezone = Column(String(50), nullable=False, default='UTC')
    frequency = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    last_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
