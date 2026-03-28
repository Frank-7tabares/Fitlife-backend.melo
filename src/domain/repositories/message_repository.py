from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Sequence, Dict
from src.domain.entities.message import Message

class MessageRepository(ABC):

    @abstractmethod
    async def save(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def find_by_id(self, message_id: UUID) -> Message | None:
        pass

    @abstractmethod
    async def get_by_recipient(self, recipient_id: UUID, skip: int=0, limit: int=50) -> List[Message]:
        pass

    @abstractmethod
    async def get_by_sender_and_recipient(self, sender_id: UUID, recipient_id: UUID, skip: int=0, limit: int=50) -> List[Message]:
        pass

    @abstractmethod
    async def get_conversation_between(self, user_a: UUID, user_b: UUID, limit: int=200) -> List[Message]:
        pass

    @abstractmethod
    async def get_conversation_with_peers(self, user_id: UUID, peer_ids: Sequence[UUID], limit: int=200) -> List[Message]:
        pass

    @abstractmethod
    async def mark_as_read(self, message_id: UUID) -> None:
        pass

    @abstractmethod
    async def count_unread_by_recipient(self, recipient_id: UUID) -> int:
        pass

    @abstractmethod
    async def mark_thread_read_for_recipient(self, recipient_id: UUID, sender_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_messages_involving_user(self, user_id: UUID, limit: int=2000) -> List[Message]:
        pass

    @abstractmethod
    async def count_unread_by_sender_for_recipient(self, recipient_id: UUID) -> Dict[UUID, int]:
        pass
