from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    USER = 'USER'
    INSTRUCTOR = 'INSTRUCTOR'
    ADMIN = 'ADMIN'

class Gender(str, Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'
    PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY'

class FitnessGoal(str, Enum):
    WEIGHT_LOSS = 'WEIGHT_LOSS'
    MUSCLE_GAIN = 'MUSCLE_GAIN'
    GENERAL_FITNESS = 'GENERAL_FITNESS'
    ATHLETIC_PERFORMANCE = 'ATHLETIC_PERFORMANCE'
    HEALTH_MAINTENANCE = 'HEALTH_MAINTENANCE'

@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    full_name: Optional[str] = None
    version: int = 1
    age: Optional[int] = None
    gender: Optional[Gender] = None
    height: Optional[float] = None
    fitness_goal: Optional[FitnessGoal] = None
    activity_level: Optional[str] = None
