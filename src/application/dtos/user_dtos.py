from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.domain.entities.user import UserRole, Gender, FitnessGoal

class UpdateProfileRequest(BaseModel):
    """Solicitud de actualización de perfil (RF-026 a RF-042)."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    gender: Optional[Gender] = None
    age: Optional[int] = Field(None, ge=13, le=120)
    height: Optional[float] = Field(None, ge=100, le=250)
    fitness_goal: Optional[FitnessGoal] = None
    activity_level: Optional[str] = None
    version: int  # Required for optimistic locking

class UserProfileResponse(BaseModel):
    """Respuesta de perfil con todos los campos (RF-026 a RF-042)."""
    id: UUID
    email: str
    full_name: Optional[str]
    role: UserRole
    version: int
    created_at: datetime


class ActiveInstructorResponse(BaseModel):
    """Instructor activo asignado al atleta (para chat y UI)."""
    instructor_id: Optional[UUID] = None
    instructor_name: Optional[str] = None
    # users.id del coach para GET /messages/conversation y POST /messages (puede diferir de instructor_id)
    messaging_user_id: Optional[UUID] = None
    # Profile fields
    age: Optional[int] = None
    gender: Optional[Gender] = None
    height: Optional[float] = None
    fitness_goal: Optional[FitnessGoal] = None
    activity_level: Optional[str] = None

from typing import Dict, Any, List

class ProfileAuditLogResponse(BaseModel):
    """Respuesta de un registro de auditoría de perfil (RF-036, RF-037)."""
    id: UUID
    user_id: UUID
    changed_by: UUID
    changes: Dict[str, Any]
    timestamp: datetime

class ProfileAuditHistoryResponse(BaseModel):
    """Respuesta con historial de auditoría del perfil."""
    user_id: UUID
    total: int
    logs: List[ProfileAuditLogResponse]
