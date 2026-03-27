"""Casos de uso para recordatorios (Historia 8 - Recordatorios, RF-095 a RF-100)."""
from uuid import uuid4, UUID
from datetime import datetime
from src.domain.entities.reminder import Reminder, ReminderType, ReminderFrequency
from src.domain.repositories.reminder_repository import ReminderRepository
from src.domain.repositories.user_repository import UserRepository
from src.application.dtos.reminder_dtos import (
    CreateReminderRequest,
    UpdateReminderRequest,
    ReminderResponse,
    ReminderListResponse
)


class CreateReminder:
    """Crea un nuevo recordatorio (RF-095 a RF-100)."""

    def __init__(self, reminder_repo: ReminderRepository, user_repo: UserRepository):
        self.reminder_repo = reminder_repo
        self.user_repo = user_repo

    async def execute(self, user_id: UUID, request: CreateReminderRequest) -> ReminderResponse:
        """Crea un recordatorio para el usuario.

        Args:
            user_id: ID del usuario
            request: DTO con datos del recordatorio

        Returns:
            ReminderResponse

        Raises:
            ValueError: Si usuario no existe
        """
        # Validar que usuario existe
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        reminder = Reminder(
            id=uuid4(),
            user_id=user_id,
            reminder_type=request.reminder_type,
            title=request.title,
            description=request.description,
            scheduled_time=request.scheduled_time,
            timezone=request.timezone,
            frequency=request.frequency,
            is_active=True,
            created_at=datetime.utcnow()
        )
        saved_reminder = await self.reminder_repo.save(reminder)
        return self._map_to_response(saved_reminder)

    def _map_to_response(self, reminder: Reminder) -> ReminderResponse:
        """Mapea entidad a DTO."""
        return ReminderResponse(
            id=reminder.id,
            user_id=reminder.user_id,
            reminder_type=reminder.reminder_type,
            title=reminder.title,
            description=reminder.description,
            scheduled_time=reminder.scheduled_time,
            timezone=reminder.timezone,
            frequency=reminder.frequency,
            is_active=reminder.is_active,
            last_sent_at=reminder.last_sent_at,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at
        )


class GetRemindersByUser:
    """Obtiene recordatorios de un usuario (RF-098)."""

    def __init__(self, reminder_repo: ReminderRepository):
        self.reminder_repo = reminder_repo

    async def execute(self, user_id: UUID, skip: int = 0, limit: int = 50) -> ReminderListResponse:
        """Obtiene recordatorios del usuario."""
        reminders = await self.reminder_repo.get_by_user(user_id, skip, limit)
        active_reminders = await self.reminder_repo.get_active_by_user(user_id)

        return ReminderListResponse(
            total=len(reminders),
            active_count=len(active_reminders),
            reminders=[self._map_to_response(r) for r in reminders]
        )

    def _map_to_response(self, reminder: Reminder) -> ReminderResponse:
        return ReminderResponse(
            id=reminder.id,
            user_id=reminder.user_id,
            reminder_type=reminder.reminder_type,
            title=reminder.title,
            description=reminder.description,
            scheduled_time=reminder.scheduled_time,
            timezone=reminder.timezone,
            frequency=reminder.frequency,
            is_active=reminder.is_active,
            last_sent_at=reminder.last_sent_at,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at
        )


class GetReminderById:
    """Obtiene un recordatorio específico por ID."""

    def __init__(self, reminder_repo: ReminderRepository):
        self.reminder_repo = reminder_repo

    async def execute(self, reminder_id: UUID) -> ReminderResponse:
        """Obtiene un recordatorio por su ID."""
        reminder = await self.reminder_repo.find_by_id(reminder_id)
        if not reminder:
            raise ValueError("Reminder not found")

        return self._map_to_response(reminder)

    def _map_to_response(self, reminder: Reminder) -> ReminderResponse:
        return ReminderResponse(
            id=reminder.id,
            user_id=reminder.user_id,
            reminder_type=reminder.reminder_type,
            title=reminder.title,
            description=reminder.description,
            scheduled_time=reminder.scheduled_time,
            timezone=reminder.timezone,
            frequency=reminder.frequency,
            is_active=reminder.is_active,
            last_sent_at=reminder.last_sent_at,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at
        )


class UpdateReminder:
    """Actualiza un recordatorio."""

    def __init__(self, reminder_repo: ReminderRepository):
        self.reminder_repo = reminder_repo

    async def execute(self, reminder_id: UUID, request: UpdateReminderRequest) -> ReminderResponse:
        """Actualiza un recordatorio existente."""
        reminder = await self.reminder_repo.find_by_id(reminder_id)
        if not reminder:
            raise ValueError("Reminder not found")

        # Actualizar solo campos proporcionados
        if request.title is not None:
            reminder.title = request.title
        if request.description is not None:
            reminder.description = request.description
        if request.scheduled_time is not None:
            reminder.scheduled_time = request.scheduled_time
        if request.timezone is not None:
            reminder.timezone = request.timezone
        if request.frequency is not None:
            reminder.frequency = request.frequency
        if request.is_active is not None:
            reminder.is_active = request.is_active

        reminder.updated_at = datetime.utcnow()
        updated_reminder = await self.reminder_repo.update(reminder)

        return self._map_to_response(updated_reminder)

    def _map_to_response(self, reminder: Reminder) -> ReminderResponse:
        return ReminderResponse(
            id=reminder.id,
            user_id=reminder.user_id,
            reminder_type=reminder.reminder_type,
            title=reminder.title,
            description=reminder.description,
            scheduled_time=reminder.scheduled_time,
            timezone=reminder.timezone,
            frequency=reminder.frequency,
            is_active=reminder.is_active,
            last_sent_at=reminder.last_sent_at,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at
        )


class DeleteReminder:
    """Elimina un recordatorio."""

    def __init__(self, reminder_repo: ReminderRepository):
        self.reminder_repo = reminder_repo

    async def execute(self, reminder_id: UUID) -> None:
        """Elimina un recordatorio."""
        reminder = await self.reminder_repo.find_by_id(reminder_id)
        if not reminder:
            raise ValueError("Reminder not found")
        await self.reminder_repo.delete(reminder_id)
