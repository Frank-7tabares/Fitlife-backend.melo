from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
from src.domain.entities.reminder import Reminder

class ReminderRepository(ABC):

    @abstractmethod
    async def save(self, reminder: Reminder) -> Reminder:
        pass

    @abstractmethod
    async def find_by_id(self, reminder_id: UUID) -> Reminder | None:
        pass

    @abstractmethod
    async def get_by_user(self, user_id: UUID, skip: int=0, limit: int=50) -> List[Reminder]:
        pass

    @abstractmethod
    async def update(self, reminder: Reminder) -> Reminder:
        pass

    @abstractmethod
    async def delete(self, reminder_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_active_by_user(self, user_id: UUID) -> List[Reminder]:
        pass

    @abstractmethod
    async def get_due_reminders(self) -> List[Reminder]:
        pass
