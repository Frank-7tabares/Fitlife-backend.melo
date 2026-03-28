from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import List, Optional

@dataclass
class Instructor:
    id: UUID
    name: str
    certifications: List[str]
    specializations: str
    rating_avg: float
    active_users_count: int
    certificate_url: Optional[str] = None
    certificate_status: str = 'pending'

@dataclass
class InstructorAssignment:
    id: UUID
    user_id: UUID
    instructor_id: UUID
    started_at: datetime
    ended_at: Optional[datetime]
    is_active: bool

@dataclass
class InstructorRating:
    id: UUID
    user_id: UUID
    instructor_id: UUID
    rating: int
    created_at: datetime
    comment: Optional[str] = None
