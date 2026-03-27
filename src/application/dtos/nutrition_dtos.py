from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class MealDTO(BaseModel):
    name: str
    description: str
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None

class DailyPlanDTO(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    meals: List[MealDTO]

class CreateNutritionPlanRequest(BaseModel):
    name: str
    description: str
    week_number: int = Field(..., ge=1, le=53)
    year: int
    daily_plans: List[DailyPlanDTO]
    is_active: bool = True

class NutritionPlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str
    week_number: int
    year: int
    daily_plans: List[DailyPlanDTO]
    is_active: bool
    created_at: datetime
