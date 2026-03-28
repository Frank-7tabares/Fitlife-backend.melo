"""Interfaz de repositorio para Message."""
from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Sequence, Dict
from src.domain.entities.message import Message


class MessageRepository(ABC):
    """Contrato de repositorio para mensajes."""

    @abstractmethod
    async def save(self, message: Message) -> Message:
        """Guarda un nuevo mensaje."""
        pass

    @abstractmethod
    async def find_by_id(self, message_id: UUID) -> Message | None:
        """Busca un mensaje por ID."""
        pass

    @abstractmethod
    async def get_by_recipient(self, recipient_id: UUID, skip: int = 0, limit: int = 50) -> List[Message]:
        """Obtiene mensajes recibidos ordenados por fecha reciente primero (RF-092)."""
        pass

    @abstractmethod
    async def get_by_sender_and_recipient(self, sender_id: UUID, recipient_id: UUID, skip: int = 0, limit: int = 50) -> List[Message]:
        """Obtiene conversación entre dos usuarios."""
        pass

    @abstractmethod
    async def get_conversation_between(self, user_a: UUID, user_b: UUID, limit: int = 200) -> List[Message]:
        """Mensajes entre dos usuarios (orden cronológico ascendente)."""
        pass

    @abstractmethod
    async def get_conversation_with_peers(
        self, user_id: UUID, peer_ids: Sequence[UUID], limit: int = 200
    ) -> List[Message]:
        """Mensajes entre user_id y cualquiera de peer_ids (orden cronológico ascendente)."""
        pass

    @abstractmethod
    async def mark_as_read(self, message_id: UUID) -> None:
        """Marca un mensaje como leído (RF-091)."""
        pass

    @abstractmethod
    async def count_unread_by_recipient(self, recipient_id: UUID) -> int:
        """Cuenta mensajes no leídos para un usuario."""
        pass

    @abstractmethod
    async def mark_thread_read_for_recipient(self, recipient_id: UUID, sender_id: UUID) -> None:
        """Marca como leídos todos los mensajes de sender_id hacia recipient_id."""
        pass

    @abstractmethod
    async def get_messages_involving_user(self, user_id: UUID, limit: int = 2000) -> List[Message]:
        """Mensajes donde user_id es remitente o destinatario, más recientes primero."""
        pass

    @abstractmethod
    async def count_unread_by_sender_for_recipient(self, recipient_id: UUID) -> Dict[UUID, int]:
        """Por cada remitente, cuántos mensajes no leídos tiene recipient_id."""
        pass
