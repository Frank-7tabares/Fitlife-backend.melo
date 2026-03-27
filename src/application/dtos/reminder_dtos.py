"""DTOs para recordatorios (Historia 8 - RF-095 a RF-100)."""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.domain.entities.reminder import ReminderType, ReminderFrequency


class CreateReminderRequest(BaseModel):
    """Solicitud para crear un recordatorio (RF-095 a RF-100)."""
    reminder_type: ReminderType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    scheduled_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")  # HH:MM
    timezone: str = Field(default="UTC", max_length=50)
    frequency: ReminderFrequency


class UpdateReminderRequest(BaseModel):
    """Solicitud para actualizar un recordatorio."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    scheduled_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")  # HH:MM
    timezone: Optional[str] = Field(None, max_length=50)
    frequency: Optional[ReminderFrequency] = None
    is_active: Optional[bool] = None


class ReminderResponse(BaseModel):
    """Respuesta de un recordatorio individual (RF-095 a RF-100)."""
    id: UUID
    user_id: UUID
    reminder_type: ReminderType
    title: str
    description: Optional[str]
    scheduled_time: str
    timezone: str
    frequency: ReminderFrequency
    is_active: bool
    last_sent_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class ReminderListResponse(BaseModel):
    """Respuesta con listado de recordatorios."""
    total: int
    active_count: int
    reminders: List[ReminderResponse]
