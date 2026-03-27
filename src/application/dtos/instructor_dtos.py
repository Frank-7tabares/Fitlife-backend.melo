"""DTOs para API de instructores (Historia 3)."""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class CreateInstructorRequest(BaseModel):
    """Para crear instructores (seed/admin). certificate_url obligatorio para verificación de profesional."""
    name: str
    certifications: List[str] = []
    specializations: str = ""
    certificate_url: Optional[str] = None  # URL del certificado profesional (recomendado para seguridad)


class InstructorResponse(BaseModel):
    id: UUID
    name: str
    certifications: List[str]
    specializations: str
    rating_avg: float
    active_users_count: int
    certificate_url: Optional[str] = None
    certificate_status: str = "pending"  # pending | verified | rejected


class VerifyCertificateRequest(BaseModel):
    status: str  # "verified" | "rejected"


class AssignInstructorRequest(BaseModel):
    instructor_id: UUID


class RateInstructorRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Calificación 1-5")
    comment: Optional[str] = None
