from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from ..entities.physical_record import PhysicalRecord


class PhysicalRecordRepository(ABC):
    @abstractmethod
    async def save(self, record: PhysicalRecord) -> PhysicalRecord:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> List[PhysicalRecord]:
        pass
