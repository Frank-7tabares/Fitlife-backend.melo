"""Repositorio SQLAlchemy para Message."""
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Sequence, Dict
from sqlalchemy import select, and_, or_, desc, asc, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories.message_repository import MessageRepository
from src.domain.entities.message import Message, MessageType
from src.infrastructure.database.models.message_model import MessageModel


class SQLAlchemyMessageRepository(MessageRepository):
    """Implementación de MessageRepository con SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message: Message) -> Message:
        """Guarda un nuevo mensaje."""
        model = MessageModel(
            id=str(message.id),
            sender_id=str(message.sender_id),
            recipient_id=str(message.recipient_id),
            subject=message.subject,
            content=message.content,
            message_type=message.message_type.value,
            is_read=message.is_read,
            created_at=message.created_at,
            read_at=message.read_at
        )
        self.session.add(model)
        await self.session.commit()
        return message

    async def find_by_id(self, message_id: UUID) -> Optional[Message]:
        """Busca un mensaje por ID."""
        stmt = select(MessageModel).where(MessageModel.id == str(message_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            return self._map_to_entity(model)
        return None

    async def get_by_recipient(self, recipient_id: UUID, skip: int = 0, limit: int = 50) -> List[Message]:
        """Obtiene mensajes recibidos ordenados por fecha reciente primero (RF-092)."""
        stmt = (
            select(MessageModel)
            .where(MessageModel.recipient_id == str(recipient_id))
            .order_by(desc(MessageModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(model) for model in models]

    async def get_by_sender_and_recipient(
        self, sender_id: UUID, recipient_id: UUID, skip: int = 0, limit: int = 50
    ) -> List[Message]:
        """Obtiene conversación entre dos usuarios."""
        stmt = (
            select(MessageModel)
            .where(
                and_(
                    MessageModel.sender_id == str(sender_id),
                    MessageModel.recipient_id == str(recipient_id)
                )
            )
            .order_by(desc(MessageModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(model) for model in models]

    async def get_conversation_between(self, user_a: UUID, user_b: UUID, limit: int = 200) -> List[Message]:
        """Mensajes entre dos usuarios en orden cronológico (más antiguo primero)."""
        sa, sb = str(user_a), str(user_b)
        stmt = (
            select(MessageModel)
            .where(
                or_(
                    and_(MessageModel.sender_id == sa, MessageModel.recipient_id == sb),
                    and_(MessageModel.sender_id == sb, MessageModel.recipient_id == sa),
                )
            )
            .order_by(asc(MessageModel.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(model) for model in models]

    async def get_conversation_with_peers(
        self, user_id: UUID, peer_ids: Sequence[UUID], limit: int = 200
    ) -> List[Message]:
        if not peer_ids:
            return []
        uid = str(user_id)
        peers = list({str(p) for p in peer_ids})
        stmt = (
            select(MessageModel)
            .where(
                or_(
                    and_(MessageModel.sender_id == uid, MessageModel.recipient_id.in_(peers)),
                    and_(MessageModel.sender_id.in_(peers), MessageModel.recipient_id == uid),
                )
            )
            .order_by(asc(MessageModel.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(model) for model in models]

    async def mark_as_read(self, message_id: UUID) -> None:
        """Marca un mensaje como leído (RF-091)."""
        stmt = select(MessageModel).where(MessageModel.id == str(message_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.is_read = True
            model.read_at = datetime.utcnow()
            await self.session.commit()

    async def count_unread_by_recipient(self, recipient_id: UUID) -> int:
        """Cuenta mensajes no leídos para un usuario."""
        stmt = select(MessageModel).where(
            and_(
                MessageModel.recipient_id == str(recipient_id),
                MessageModel.is_read == False
            )
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def mark_thread_read_for_recipient(self, recipient_id: UUID, sender_id: UUID) -> None:
        """Marca como leídos los mensajes recibidos de sender_id hacia recipient_id."""
        stmt = (
            update(MessageModel)
            .where(
                and_(
                    MessageModel.recipient_id == str(recipient_id),
                    MessageModel.sender_id == str(sender_id),
                    MessageModel.is_read == False,
                )
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_messages_involving_user(self, user_id: UUID, limit: int = 2000) -> List[Message]:
        uid = str(user_id)
        stmt = (
            select(MessageModel)
            .where(
                or_(MessageModel.sender_id == uid, MessageModel.recipient_id == uid),
            )
            .order_by(desc(MessageModel.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(model) for model in models]

    async def count_unread_by_sender_for_recipient(self, recipient_id: UUID) -> Dict[UUID, int]:
        stmt = (
            select(MessageModel.sender_id, func.count(MessageModel.id))
            .where(
                and_(
                    MessageModel.recipient_id == str(recipient_id),
                    MessageModel.is_read == False,
                )
            )
            .group_by(MessageModel.sender_id)
        )
        result = await self.session.execute(stmt)
        return {UUID(sid): int(cnt) for sid, cnt in result.all()}

    def _map_to_entity(self, model: MessageModel) -> Message:
        """Mapea modelo de BD a entidad de dominio."""
        return Message(
            id=UUID(model.id),
            sender_id=UUID(model.sender_id),
            recipient_id=UUID(model.recipient_id),
            subject=model.subject,
            content=model.content,
            message_type=MessageType(model.message_type),
            is_read=model.is_read,
            created_at=model.created_at,
            read_at=model.read_at
        )
