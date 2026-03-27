from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from ....infrastructure.database.connection import get_db
from ....infrastructure.repositories.sqlalchemy_nutrition_repository import SQLAlchemyNutritionRepository
from ....application.use_cases.nutrition_use_cases import NutritionUseCases
from ....application.dtos.nutrition_dtos import CreateNutritionPlanRequest, NutritionPlanResponse
from ..dependencies import get_current_instructor

router = APIRouter(prefix="", tags=["Nutrition Plans"])

async def get_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyNutritionRepository(db)

@router.post("/nutrition/plans", response_model=NutritionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    user_id: UUID,
    request: CreateNutritionPlanRequest,
    _current_user = Depends(get_current_instructor),
    repo: SQLAlchemyNutritionRepository = Depends(get_repo),
):
    """Crea un plan nutricional para un atleta. Solo instructor o admin."""
    use_cases = NutritionUseCases(repo)
    return await use_cases.create_plan(user_id, request)

@router.get("/users/{user_id}/nutrition/active", response_model=Optional[NutritionPlanResponse])
async def get_active_plan(
    user_id: UUID, 
    repo: SQLAlchemyNutritionRepository = Depends(get_repo)
):
    use_cases = NutritionUseCases(repo)
    plan = await use_cases.get_active_plan(user_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active nutrition plan found")
    return plan
