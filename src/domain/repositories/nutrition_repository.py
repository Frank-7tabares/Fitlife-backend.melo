"""Puerto de salida: Repositorio de planes nutricionales (interfaz ABC)."""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.nutrition import NutritionPlan


class NutritionRepository(ABC):
    """Puerto de salida para persistencia de planes de nutrición."""

    @abstractmethod
    async def save(self, plan: NutritionPlan) -> NutritionPlan:
        """Persiste un plan de nutrición."""
        ...

    @abstractmethod
    async def find_active_by_user_id(self, user_id: UUID) -> Optional[NutritionPlan]:
        """Obtiene el plan de nutrición activo de un usuario."""
        ...
