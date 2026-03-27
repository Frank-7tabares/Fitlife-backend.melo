from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional


class ActivityLevel(str, Enum):
    SEDENTARY = "SEDENTARY"
    LIGHT = "LIGHT"
    MODERATE = "MODERATE"
    ACTIVE = "ACTIVE"
    VERY_ACTIVE = "VERY_ACTIVE"


@dataclass
class PhysicalRecord:
    id: UUID
    user_id: UUID
    weight: float
    height: float
    activity_level: ActivityLevel
    recorded_at: datetime
    body_fat_percentage: Optional[float] = None
    waist: Optional[float] = None
    hip: Optional[float] = None

    @property
    def bmi(self) -> float:
        return self.weight / ((self.height / 100) ** 2)
