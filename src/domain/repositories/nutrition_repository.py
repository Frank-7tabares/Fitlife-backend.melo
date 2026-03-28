from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from ..entities.nutrition import NutritionPlan

class NutritionRepository(ABC):

    @abstractmethod
    async def save(self, plan: NutritionPlan) -> NutritionPlan:
        ...

    @abstractmethod
    async def find_active_by_user_id(self, user_id: UUID) -> Optional[NutritionPlan]:
        ...
