"""Puerto de salida: Repositorio de evaluaciones físicas (interfaz ABC)."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.assessment import Assessment


class AssessmentRepository(ABC):
    """Puerto de salida para persistencia de evaluaciones físicas."""

    @abstractmethod
    async def save(self, assessment: Assessment) -> Assessment:
        """Persiste una evaluación nueva."""
        ...

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> List[Assessment]:
        """Obtiene el historial de evaluaciones de un usuario."""
        ...

    @abstractmethod
    async def find_latest_by_user(self, user_id: UUID) -> Optional[Assessment]:
        """Obtiene la evaluación más reciente de un usuario."""
        ...
