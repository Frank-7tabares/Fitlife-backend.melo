"""Interfaz de repositorio para Reminder."""
from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
from src.domain.entities.reminder import Reminder


class ReminderRepository(ABC):
    """Contrato de repositorio para recordatorios."""

    @abstractmethod
    async def save(self, reminder: Reminder) -> Reminder:
        """Guarda un nuevo recordatorio."""
        pass

    @abstractmethod
    async def find_by_id(self, reminder_id: UUID) -> Reminder | None:
        """Busca un recordatorio por ID."""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Reminder]:
        """Obtiene recordatorios de un usuario."""
        pass

    @abstractmethod
    async def update(self, reminder: Reminder) -> Reminder:
        """Actualiza un recordatorio existente."""
        pass

    @abstractmethod
    async def delete(self, reminder_id: UUID) -> None:
        """Elimina un recordatorio."""
        pass

    @abstractmethod
    async def get_active_by_user(self, user_id: UUID) -> List[Reminder]:
        """Obtiene recordatorios activos de un usuario (RF-098)."""
        pass

    @abstractmethod
    async def get_due_reminders(self) -> List[Reminder]:
        """Obtiene recordatorios que deben enviarse (para worker/cron)."""
        pass
