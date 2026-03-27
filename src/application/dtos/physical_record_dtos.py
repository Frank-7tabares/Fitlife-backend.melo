from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ...domain.entities.physical_record import ActivityLevel


class PhysicalRecordRequest(BaseModel):
    weight: float = Field(..., gt=0, ge=1.0, le=500.0, description="Peso en kg (1–500)")
    height: float = Field(..., gt=0, ge=50.0, le=300.0, description="Altura en cm (50–300)")
    body_fat_percentage: Optional[float] = Field(
        None, ge=2.0, le=70.0, description="% grasa corporal (2–70)"
    )
    waist: Optional[float] = Field(None, ge=30.0, le=300.0, description="Cintura en cm (30–300)")
    hip: Optional[float] = Field(None, ge=30.0, le=300.0, description="Cadera en cm (30–300)")
    activity_level: ActivityLevel
    recorded_at: Optional[datetime] = Field(
        default=None,
        description="Marca de tiempo del registro (ISO 8601). Si no se proporciona, se usa la fecha/hora actual.",
    )

    @field_validator("recorded_at", mode="before")
    @classmethod
    def default_recorded_at(cls, v: Optional[datetime]) -> datetime:
        if v is None:
            return datetime.now(timezone.utc)
        return v


class PhysicalRecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    weight: float
    height: float
    bmi: float
    body_fat_percentage: Optional[float]
    waist: Optional[float]
    hip: Optional[float]
    activity_level: ActivityLevel
    recorded_at: datetime

    model_config = {"from_attributes": True}


class PhysicalRecordListResponse(BaseModel):
    records: List[PhysicalRecordResponse]
    total: int
