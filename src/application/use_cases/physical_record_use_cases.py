from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from ...domain.entities.physical_record import PhysicalRecord
from ...domain.repositories.physical_record_repository import PhysicalRecordRepository
from ..dtos.physical_record_dtos import (
    PhysicalRecordListResponse,
    PhysicalRecordRequest,
    PhysicalRecordResponse,
)


class PhysicalRecordUseCases:
    def __init__(self, repository: PhysicalRecordRepository):
        self.repository = repository

    async def create_record(self, user_id: UUID, request: PhysicalRecordRequest) -> PhysicalRecordResponse:
        recorded_at = request.recorded_at or datetime.now(timezone.utc)
        record = PhysicalRecord(
            id=uuid4(),
            user_id=user_id,
            weight=request.weight,
            height=request.height,
            body_fat_percentage=request.body_fat_percentage,
            waist=request.waist,
            hip=request.hip,
            activity_level=request.activity_level,
            recorded_at=recorded_at,
        )
        await self.repository.save(record)
        return self._map_to_response(record)

    async def get_history(self, user_id: UUID) -> PhysicalRecordListResponse:
        records = await self.repository.find_by_user_id(user_id)
        responses = [self._map_to_response(r) for r in records]
        return PhysicalRecordListResponse(records=responses, total=len(responses))

    @staticmethod
    def _map_to_response(r: PhysicalRecord) -> PhysicalRecordResponse:
        return PhysicalRecordResponse(
            id=r.id,
            user_id=r.user_id,
            weight=r.weight,
            height=r.height,
            bmi=round(r.bmi, 2),
            body_fat_percentage=r.body_fat_percentage,
            waist=r.waist,
            hip=r.hip,
            activity_level=r.activity_level,
            recorded_at=r.recorded_at,
        )
