from dataclasses import dataclass
from datetime import datetime, time
from uuid import UUID
from enum import Enum
from typing import Optional

class ReminderType(str, Enum):
    TRAINING = 'TRAINING'
    PHYSICAL_RECORD = 'PHYSICAL_RECORD'
    INSTRUCTOR_FOLLOWUP = 'INSTRUCTOR_FOLLOWUP'

class ReminderFrequency(str, Enum):
    ONCE = 'ONCE'
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'

@dataclass
class Reminder:
    id: UUID
    user_id: UUID
    reminder_type: ReminderType
    title: str
    scheduled_time: str
    timezone: str
    frequency: ReminderFrequency
    is_active: bool = True
    created_at: datetime = None
    description: Optional[str] = None
    last_sent_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
