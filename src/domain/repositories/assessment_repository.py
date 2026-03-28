from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.assessment import Assessment

class AssessmentRepository(ABC):

    @abstractmethod
    async def save(self, assessment: Assessment) -> Assessment:
        ...

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> List[Assessment]:
        ...

    @abstractmethod
    async def find_latest_by_user(self, user_id: UUID) -> Optional[Assessment]:
        ...
