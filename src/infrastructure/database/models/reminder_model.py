"""Modelo de base de datos: Recordatorio (Historia 8 - Recordatorios)."""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid


class ReminderModel(Base):
    """Modelo de recordatorio en base de datos.
    
    Campos:
    - user_id -> users.id (FK)
    - reminder_type: TRAINING, PHYSICAL_RECORD, INSTRUCTOR_FOLLOWUP
    - scheduled_time: HH:MM formato
    - timezone: Zona horaria del usuario (RF-100)
    - frequency: ONCE, DAILY, WEEKLY, MONTHLY
    - is_active: Recordatorio activo (RF-098)
    """
    __tablename__ = "reminders"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reminder_type = Column(String(50), nullable=False)  # TRAINING, PHYSICAL_RECORD, INSTRUCTOR_FOLLOWUP
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    scheduled_time = Column(String(5), nullable=False)  # HH:MM
    timezone = Column(String(50), nullable=False, default="UTC")  # America/Bogota, etc.
    frequency = Column(String(50), nullable=False)  # ONCE, DAILY, WEEKLY, MONTHLY
    is_active = Column(Boolean, default=True, index=True)
    last_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
