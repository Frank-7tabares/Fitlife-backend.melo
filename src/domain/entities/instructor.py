"""Entidades del dominio para instructores (Historia 3, RF-043 a RF-050)."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import List, Optional


@dataclass
class Instructor:
    """Instructor de fitness: nombre, certificaciones, especializaciones, calificación y conteo de usuarios activos."""
    id: UUID
    name: str
    certifications: List[str]
    specializations: str
    rating_avg: float  # calculada desde InstructorRating, persistida para listados
    active_users_count: int  # calculada desde InstructorAssignment, no persistida en modelo base
    certificate_url: Optional[str] = None
    certificate_status: str = "pending"  # pending | verified | rejected


@dataclass
class InstructorAssignment:
    """Relación usuario-instructor con historial (RF-046, RF-047)."""
    id: UUID
    user_id: UUID
    instructor_id: UUID
    started_at: datetime
    ended_at: Optional[datetime]
    is_active: bool


@dataclass
class InstructorRating:
    """Calificación de un usuario a su instructor (1-5). RF-048, RF-050."""
    id: UUID
    user_id: UUID
    instructor_id: UUID
    rating: int  # 1-5
    created_at: datetime
    comment: Optional[str] = None
