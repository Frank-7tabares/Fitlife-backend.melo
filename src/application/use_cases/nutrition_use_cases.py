from uuid import uuid4
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from ...domain.entities.nutrition import NutritionPlan, DailyPlan, Meal
from ...infrastructure.repositories.sqlalchemy_nutrition_repository import SQLAlchemyNutritionRepository
from ..dtos.nutrition_dtos import CreateNutritionPlanRequest, NutritionPlanResponse, DailyPlanDTO, MealDTO

class NutritionUseCases:

    def __init__(self, repository: SQLAlchemyNutritionRepository):
        self.repository = repository

    async def create_plan(self, user_id: UUID, request: CreateNutritionPlanRequest) -> NutritionPlanResponse:
        plan = NutritionPlan(id=uuid4(), user_id=user_id, name=request.name, description=request.description, week_number=request.week_number, year=request.year, daily_plans=[DailyPlan(day_of_week=dp.day_of_week, meals=[Meal(name=m.name, description=m.description, calories=m.calories, protein=m.protein, carbs=m.carbs, fats=m.fats) for m in dp.meals]) for dp in request.daily_plans], is_active=request.is_active, created_at=datetime.utcnow())
        await self.repository.save(plan)
        return self._map_to_response(plan)

    async def get_active_plan(self, user_id: UUID) -> Optional[NutritionPlanResponse]:
        plan = await self.repository.find_active_by_user_id(user_id)
        return self._map_to_response(plan) if plan else None

    def _map_to_response(self, p: NutritionPlan) -> NutritionPlanResponse:
        return NutritionPlanResponse(id=p.id, user_id=p.user_id, name=p.name, description=p.description, week_number=p.week_number, year=p.year, daily_plans=[DailyPlanDTO(day_of_week=dp.day_of_week, meals=[MealDTO(name=m.name, description=m.description, calories=m.calories, protein=m.protein, carbs=m.carbs, fats=m.fats) for m in dp.meals]) for dp in p.daily_plans], is_active=p.is_active, created_at=p.created_at)
