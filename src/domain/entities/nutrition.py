from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import List, Optional

@dataclass
class Meal:
    name: str
    description: str
    calories: Optional[int]
    protein: Optional[float]
    carbs: Optional[float]
    fats: Optional[float]

@dataclass
class DailyPlan:
    day_of_week: int
    meals: List[Meal]

@dataclass
class NutritionPlan:
    id: UUID
    user_id: UUID
    name: str
    description: str
    week_number: int
    year: int
    daily_plans: List[DailyPlan]
    is_active: bool
    created_at: datetime
