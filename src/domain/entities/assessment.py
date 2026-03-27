from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Dict, Any, Optional

class AssessmentCategory(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"

class BodyAgeComparison(str, Enum):
    BODY_OLDER = "BODY_OLDER"
    BODY_YOUNGER = "BODY_YOUNGER"
    BODY_EQUAL = "BODY_EQUAL"

@dataclass
class Assessment:
    id: UUID
    user_id: UUID
    fitness_score: float
    category: AssessmentCategory
    body_age: float
    comparison: BodyAgeComparison
    responses: Dict[str, Any]
    created_at: datetime
