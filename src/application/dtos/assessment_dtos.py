from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime
from uuid import UUID
from ...domain.entities.assessment import AssessmentCategory, BodyAgeComparison

# RF-058: descargo edad corporal (estimación, no diagnóstico médico)
BODY_AGE_DISCLAIMER = (
    "La edad corporal es una estimación orientativa y no constituye un diagnóstico médico."
)


class SubmitAssessmentRequest(BaseModel):
    user_id: UUID
    real_age: int
    responses: Dict[str, Any]


class AssessmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    fitness_score: float
    category: AssessmentCategory
    body_age: float
    comparison: BodyAgeComparison
    responses: Dict[str, Any]
    created_at: datetime
    body_age_disclaimer: str = Field(
        default=BODY_AGE_DISCLAIMER,
        description="Descargo: la edad corporal es estimación, no diagnóstico médico (RF-058).",
    )
