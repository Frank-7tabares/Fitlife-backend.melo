"""Servicio de aplicación: Notificaciones del sistema."""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

from ...domain.entities.message import Message, MessageType
from ...domain.repositories.message_repository import MessageRepository


class NotificationService:
    """Envía notificaciones del sistema almacenadas como mensajes."""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def send_assignment_notification(
        self,
        user_id: UUID,
        assignment_type: str,
        details: Optional[dict] = None,
        sender_id: Optional[UUID] = None,
    ) -> Message:
        """Envía notificación de asignación (rutina, plan nutricional, instructor)."""
        content = f"Se te ha asignado un nuevo {assignment_type}"
        if details:
            name = details.get("name", "")
            if name:
                content = f"Se te ha asignado: {name}"

        message = Message(
            id=uuid4(),
            sender_id=sender_id or user_id,
            recipient_id=user_id,
            content=content,
            message_type=MessageType.SYSTEM_NOTIFICATION,
            is_read=False,
            created_at=datetime.utcnow(),
        )
        return await self.message_repository.save(message)

    async def send_welcome_notification(self, user_id: UUID) -> Message:
        """Envía notificación de bienvenida al registrarse."""
        message = Message(
            id=uuid4(),
            sender_id=user_id,
            recipient_id=user_id,
            content="¡Bienvenido a FitLife! Comienza tu evaluación física para obtener tu plan personalizado.",
            message_type=MessageType.SYSTEM_NOTIFICATION,
            is_read=False,
            created_at=datetime.utcnow(),
        )
        return await self.message_repository.save(message)
