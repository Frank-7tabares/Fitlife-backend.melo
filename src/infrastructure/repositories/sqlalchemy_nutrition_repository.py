from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.entities.nutrition import NutritionPlan, DailyPlan, Meal
from ..database.models.nutrition_models import NutritionPlanModel

class SQLAlchemyNutritionRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, plan: NutritionPlan) -> NutritionPlan:
        if plan.is_active:
            stmt = update(NutritionPlanModel).where(NutritionPlanModel.user_id == str(plan.user_id), NutritionPlanModel.is_active == True).values(is_active=False)
            await self.session.execute(stmt)
        model = NutritionPlanModel(id=str(plan.id), user_id=str(plan.user_id), name=plan.name, description=plan.description, week_number=plan.week_number, year=plan.year, plans_data=[{'day_of_week': dp.day_of_week, 'meals': [{'name': m.name, 'description': m.description, 'calories': m.calories, 'protein': m.protein, 'carbs': m.carbs, 'fats': m.fats} for m in dp.meals]} for dp in plan.daily_plans], is_active=plan.is_active, created_at=plan.created_at)
        self.session.add(model)
        await self.session.commit()
        return plan

    async def delete_plans_by_user_id(self, user_id: UUID) -> int:
        stmt = delete(NutritionPlanModel).where(NutritionPlanModel.user_id == str(user_id))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def find_active_by_user_id(self, user_id: UUID) -> Optional[NutritionPlan]:
        stmt = select(NutritionPlanModel).where(NutritionPlanModel.user_id == str(user_id), NutritionPlanModel.is_active == True)
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        if not m:
            return None
        return self._map_to_entity(m)

    def _map_to_entity(self, m: NutritionPlanModel) -> NutritionPlan:
        return NutritionPlan(id=UUID(m.id), user_id=UUID(m.user_id), name=m.name, description=m.description, week_number=m.week_number, year=m.year, daily_plans=[DailyPlan(day_of_week=dp['day_of_week'], meals=[Meal(name=meal['name'], description=meal['description'], calories=meal.get('calories'), protein=meal.get('protein'), carbs=meal.get('carbs'), fats=meal.get('fats')) for meal in dp['meals']]) for dp in m.plans_data], is_active=m.is_active, created_at=m.created_at)
