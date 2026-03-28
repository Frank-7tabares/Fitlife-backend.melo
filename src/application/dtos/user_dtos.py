from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.domain.entities.user import UserRole, Gender, FitnessGoal

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    gender: Optional[Gender] = None
    age: Optional[int] = Field(None, ge=13, le=120)
    height: Optional[float] = Field(None, ge=100, le=250)
    fitness_goal: Optional[FitnessGoal] = None
    activity_level: Optional[str] = None
    version: int

class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    role: UserRole
    version: int
    created_at: datetime

class ActiveInstructorResponse(BaseModel):
    instructor_id: Optional[UUID] = None
    instructor_name: Optional[str] = None
    messaging_user_id: Optional[UUID] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    height: Optional[float] = None
    fitness_goal: Optional[FitnessGoal] = None
    activity_level: Optional[str] = None
from typing import Dict, Any, List

class ProfileAuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    changed_by: UUID
    changes: Dict[str, Any]
    timestamp: datetime

class ProfileAuditHistoryResponse(BaseModel):
    user_id: UUID
    total: int
    logs: List[ProfileAuditLogResponse]
