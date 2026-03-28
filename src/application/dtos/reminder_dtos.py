from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.domain.entities.reminder import ReminderType, ReminderFrequency

class CreateReminderRequest(BaseModel):
    reminder_type: ReminderType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    scheduled_time: str = Field(..., pattern='^\\d{2}:\\d{2}$')
    timezone: str = Field(default='UTC', max_length=50)
    frequency: ReminderFrequency

class UpdateReminderRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    scheduled_time: Optional[str] = Field(None, pattern='^\\d{2}:\\d{2}$')
    timezone: Optional[str] = Field(None, max_length=50)
    frequency: Optional[ReminderFrequency] = None
    is_active: Optional[bool] = None

class ReminderResponse(BaseModel):
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
    total: int
    active_count: int
    reminders: List[ReminderResponse]
