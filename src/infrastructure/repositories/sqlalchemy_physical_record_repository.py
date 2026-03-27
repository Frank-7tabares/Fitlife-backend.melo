from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.physical_record import ActivityLevel, PhysicalRecord
from ...domain.repositories.physical_record_repository import PhysicalRecordRepository
from ..database.models.physical_record_model import PhysicalRecordModel


class SQLAlchemyPhysicalRecordRepository(PhysicalRecordRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, record: PhysicalRecord) -> PhysicalRecord:
        model = PhysicalRecordModel(
            id=str(record.id),
            user_id=str(record.user_id),
            weight=record.weight,
            height=record.height,
            body_fat_percentage=record.body_fat_percentage,
            waist=record.waist,
            hip=record.hip,
            activity_level=record.activity_level.value,
            recorded_at=record.recorded_at,
        )
        self.session.add(model)
        await self.session.commit()
        return record

    async def find_by_user_id(self, user_id: UUID) -> List[PhysicalRecord]:
        stmt = (
            select(PhysicalRecordModel)
            .where(PhysicalRecordModel.user_id == str(user_id))
            .order_by(PhysicalRecordModel.recorded_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_entity(m: PhysicalRecordModel) -> PhysicalRecord:
        return PhysicalRecord(
            id=UUID(m.id),
            user_id=UUID(m.user_id),
            weight=m.weight,
            height=m.height,
            body_fat_percentage=m.body_fat_percentage,
            waist=m.waist,
            hip=m.hip,
            activity_level=ActivityLevel(m.activity_level),
            recorded_at=m.recorded_at,
        )
