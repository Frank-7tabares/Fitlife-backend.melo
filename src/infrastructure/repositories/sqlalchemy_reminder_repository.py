from uuid import UUID
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories.reminder_repository import ReminderRepository
from src.domain.entities.reminder import Reminder, ReminderType, ReminderFrequency
from src.infrastructure.database.models.reminder_model import ReminderModel

class SQLAlchemyReminderRepository(ReminderRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, reminder: Reminder) -> Reminder:
        model = ReminderModel(id=str(reminder.id), user_id=str(reminder.user_id), reminder_type=reminder.reminder_type.value, title=reminder.title, description=reminder.description, scheduled_time=reminder.scheduled_time, timezone=reminder.timezone, frequency=reminder.frequency.value, is_active=reminder.is_active, last_sent_at=reminder.last_sent_at, created_at=reminder.created_at, updated_at=reminder.updated_at)
        self.session.add(model)
        await self.session.commit()
        return reminder

    async def find_by_id(self, reminder_id: UUID) -> Optional[Reminder]:
        stmt = select(ReminderModel).where(ReminderModel.id == str(reminder_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            return self._map_to_entity(model)
        return None

    async def get_by_user(self, user_id: UUID, skip: int=0, limit: int=50) -> List[Reminder]:
        stmt = select(ReminderModel).where(ReminderModel.user_id == str(user_id)).order_by(desc(ReminderModel.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(model) for model in models]

    async def update(self, reminder: Reminder) -> Reminder:
        stmt = select(ReminderModel).where(ReminderModel.id == str(reminder.id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.title = reminder.title
            model.description = reminder.description
            model.scheduled_time = reminder.scheduled_time
            model.timezone = reminder.timezone
            model.frequency = reminder.frequency.value
            model.is_active = reminder.is_active
            model.last_sent_at = reminder.last_sent_at
            model.updated_at = datetime.utcnow()
            await self.session.commit()
        return reminder

    async def delete(self, reminder_id: UUID) -> None:
        stmt = select(ReminderModel).where(ReminderModel.id == str(reminder_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def get_active_by_user(self, user_id: UUID) -> List[Reminder]:
        stmt = select(ReminderModel).where(and_(ReminderModel.user_id == str(user_id), ReminderModel.is_active == True)).order_by(ReminderModel.scheduled_time)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(model) for model in models]

    async def get_due_reminders(self) -> List[Reminder]:
        stmt = select(ReminderModel).where(ReminderModel.is_active == True).order_by(ReminderModel.scheduled_time)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(model) for model in models]

    def _map_to_entity(self, model: ReminderModel) -> Reminder:
        return Reminder(id=UUID(model.id), user_id=UUID(model.user_id), reminder_type=ReminderType(model.reminder_type), title=model.title, description=model.description, scheduled_time=model.scheduled_time, timezone=model.timezone, frequency=ReminderFrequency(model.frequency), is_active=model.is_active, last_sent_at=model.last_sent_at, created_at=model.created_at, updated_at=model.updated_at)
