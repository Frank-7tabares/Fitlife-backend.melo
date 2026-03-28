from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime
from src.domain.entities.message import Message, MessageType
from src.domain.entities.user import User, UserRole
from src.domain.repositories.message_repository import MessageRepository
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRepository, SQLAlchemyInstructorAssignmentRepository
from src.application.dtos.message_dtos import SendMessageRequest, MessageResponse, MessageListResponse, ConversationResponse, InboxThreadItem, CoachInboxResponse

def _norm_name(value: Optional[str]) -> str:
    return (value or '').strip().lower()

def _uuid_in(member: UUID, candidates: set[UUID]) -> bool:
    ms = str(member).lower()
    return any((str(c).lower() == ms for c in candidates))

async def resolve_coach_user_id_for_profile(profile_instructor_id: UUID, user_repo: UserRepository, instructor_repo: SQLAlchemyInstructorRepository) -> UUID:
    linked = await user_repo.find_by_id(profile_instructor_id)
    if linked:
        return linked.id
    prof = await instructor_repo.find_by_id(profile_instructor_id)
    if not prof or not prof.name:
        return profile_instructor_id
    target = _norm_name(prof.name)
    candidates = await user_repo.find_by_role(UserRole.INSTRUCTOR.value)
    for cand in candidates:
        cn = _norm_name(cand.full_name)
        if cn == target:
            return cand.id
    for cand in candidates:
        cn = _norm_name(cand.full_name)
        if target and cn and (target in cn or cn in target):
            return cand.id
    return profile_instructor_id

async def allowed_coach_ids_for_assignment(profile_instructor_id: UUID, user_repo: UserRepository, instructor_repo: SQLAlchemyInstructorRepository) -> set[UUID]:
    uid = await resolve_coach_user_id_for_profile(profile_instructor_id, user_repo, instructor_repo)
    return {profile_instructor_id, uid}

async def coach_owns_assignment(profile_instructor_id: UUID, coach_user_id: UUID, user_repo: UserRepository, instructor_repo: SQLAlchemyInstructorRepository) -> bool:
    if str(profile_instructor_id).lower() == str(coach_user_id).lower():
        return True
    allowed = await allowed_coach_ids_for_assignment(profile_instructor_id, user_repo, instructor_repo)
    return _uuid_in(coach_user_id, allowed)

async def assert_can_converse_async(current_user: User, peer_id: UUID, user_repo: UserRepository, instructor_repo: SQLAlchemyInstructorRepository, assignment_repo: SQLAlchemyInstructorAssignmentRepository, message_repo: MessageRepository | None=None) -> None:
    if peer_id == current_user.id:
        raise ValueError('Usuario inválido en la conversación')
    peer = await user_repo.find_by_id(peer_id)
    if not peer:
        resolved = await resolve_coach_user_id_for_profile(peer_id, user_repo, instructor_repo)
        peer = await user_repo.find_by_id(resolved)
    if not peer:
        raise ValueError('Usuario no encontrado')
    canonical_peer_id = peer.id
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.USER:
        asn = await instructor_repo.find_active_assignment(current_user.id)
        if asn:
            allowed = await allowed_coach_ids_for_assignment(asn.instructor_id, user_repo, instructor_repo)
            if not _uuid_in(peer_id, allowed) and (not _uuid_in(canonical_peer_id, allowed)):
                raise ValueError('No puedes ver esta conversación')
        else:
            if not message_repo:
                raise ValueError('No puedes ver esta conversación')
            convo = await message_repo.get_by_sender_and_recipient(canonical_peer_id, current_user.id, limit=1)
            if not convo:
                convo = await message_repo.get_by_sender_and_recipient(peer_id, current_user.id, limit=1)
            if not convo:
                raise ValueError('No puedes ver esta conversación')
    elif current_user.role == UserRole.INSTRUCTOR:
        if peer.role != UserRole.USER:
            raise ValueError('No puedes ver esta conversación')
    else:
        raise ValueError('No puedes ver esta conversación')

class SendMessage:

    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository, instructor_repo: SQLAlchemyInstructorRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo
        self.instructor_repo = instructor_repo

    async def execute(self, sender_id: UUID, request: SendMessageRequest) -> MessageResponse:
        recipient = await self.user_repo.find_by_id(request.recipient_id)
        if not recipient:
            resolved_uid = await resolve_coach_user_id_for_profile(request.recipient_id, self.user_repo, self.instructor_repo)
            recipient = await self.user_repo.find_by_id(resolved_uid)
        if not recipient:
            raise ValueError('Recipient user not found')
        recipient_user_id = recipient.id
        sender_user = await self.user_repo.find_by_id(sender_id)
        if not sender_user:
            raise ValueError('Usuario remitente no encontrado')
        if request.message_type == MessageType.INSTRUCTOR_MESSAGE:
            if sender_user.role not in (UserRole.INSTRUCTOR, UserRole.ADMIN):
                raise ValueError('Solo instructores pueden enviar este tipo de mensaje')
            if sender_user.role == UserRole.INSTRUCTOR:
                if recipient.role != UserRole.USER:
                    raise ValueError('Solo puedes escribir a usuarios atleta')
        elif request.message_type == MessageType.USER_MESSAGE:
            if sender_user.role != UserRole.USER:
                raise ValueError('Solo los atletas pueden enviar este tipo de mensaje')
            assignment = await self.instructor_repo.find_active_assignment(sender_id)
            if not assignment:
                if recipient.role not in (UserRole.INSTRUCTOR, UserRole.ADMIN):
                    raise ValueError('Solo puedes escribir a tu instructor asignado')
                prior = await self.message_repo.get_by_sender_and_recipient(recipient_user_id, sender_id, skip=0, limit=1)
                if not prior:
                    raise ValueError('No tienes un instructor asignado')
            else:
                allowed = await allowed_coach_ids_for_assignment(assignment.instructor_id, self.user_repo, self.instructor_repo)
                if not _uuid_in(recipient_user_id, allowed) and (not _uuid_in(request.recipient_id, allowed)):
                    raise ValueError('Solo puedes escribir a tu instructor asignado')
        elif request.message_type == MessageType.SYSTEM_NOTIFICATION:
            pass
        else:
            raise ValueError('Tipo de mensaje no soportado')
        message = Message(id=uuid4(), sender_id=sender_id, recipient_id=recipient_user_id, subject=request.subject, content=request.content, message_type=request.message_type, is_read=False, created_at=datetime.utcnow())
        saved_message = await self.message_repo.save(message)
        return self._map_to_response(saved_message)

    def _map_to_response(self, message: Message) -> MessageResponse:
        return MessageResponse(id=message.id, sender_id=message.sender_id, recipient_id=message.recipient_id, subject=message.subject, content=message.content, message_type=message.message_type, is_read=message.is_read, created_at=message.created_at, read_at=message.read_at)

class GetMessagesByUser:

    def __init__(self, message_repo: MessageRepository):
        self.message_repo = message_repo

    async def execute(self, user_id: UUID, skip: int=0, limit: int=50) -> MessageListResponse:
        messages = await self.message_repo.get_by_recipient(user_id, skip, limit)
        unread_count = await self.message_repo.count_unread_by_recipient(user_id)
        return MessageListResponse(total=len(messages), unread_count=unread_count, messages=[self._map_to_response(msg) for msg in messages])

    def _map_to_response(self, message: Message) -> MessageResponse:
        return MessageResponse(id=message.id, sender_id=message.sender_id, recipient_id=message.recipient_id, subject=message.subject, content=message.content, message_type=message.message_type, is_read=message.is_read, created_at=message.created_at, read_at=message.read_at)

class GetConversation:

    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository, instructor_repo: SQLAlchemyInstructorRepository, assignment_repo: SQLAlchemyInstructorAssignmentRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo
        self.instructor_repo = instructor_repo
        self.assignment_repo = assignment_repo

    async def execute(self, current_user: User, peer_id: UUID) -> ConversationResponse:
        await assert_can_converse_async(current_user, peer_id, self.user_repo, self.instructor_repo, self.assignment_repo, self.message_repo)
        if current_user.role == UserRole.USER:
            asn = await self.instructor_repo.find_active_assignment(current_user.id)
            if asn:
                coach_ids = await allowed_coach_ids_for_assignment(asn.instructor_id, self.user_repo, self.instructor_repo)
                msgs = await self.message_repo.get_conversation_with_peers(current_user.id, list(coach_ids))
            else:
                msgs = await self.message_repo.get_conversation_between(current_user.id, peer_id)
        else:
            msgs = await self.message_repo.get_conversation_between(current_user.id, peer_id)
        return ConversationResponse(peer_id=peer_id, messages=[self._map_to_response(m) for m in msgs])

    def _map_to_response(self, message: Message) -> MessageResponse:
        return MessageResponse(id=message.id, sender_id=message.sender_id, recipient_id=message.recipient_id, subject=message.subject, content=message.content, message_type=message.message_type, is_read=message.is_read, created_at=message.created_at, read_at=message.read_at)

class MarkThreadRead:

    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository, instructor_repo: SQLAlchemyInstructorRepository, assignment_repo: SQLAlchemyInstructorAssignmentRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo
        self.instructor_repo = instructor_repo
        self.assignment_repo = assignment_repo

    async def execute(self, current_user: User, peer_id: UUID) -> None:
        await assert_can_converse_async(current_user, peer_id, self.user_repo, self.instructor_repo, self.assignment_repo, self.message_repo)
        if current_user.role == UserRole.USER:
            asn = await self.instructor_repo.find_active_assignment(current_user.id)
            if asn:
                coach_ids = await allowed_coach_ids_for_assignment(asn.instructor_id, self.user_repo, self.instructor_repo)
                for cid in coach_ids:
                    await self.message_repo.mark_thread_read_for_recipient(current_user.id, cid)
            else:
                recent = await self.message_repo.get_by_recipient(current_user.id, limit=50)
                unread_senders = {m.sender_id for m in recent if not m.is_read and m.sender_id != current_user.id}
                for sender in unread_senders:
                    await self.message_repo.mark_thread_read_for_recipient(current_user.id, sender)
        else:
            await self.message_repo.mark_thread_read_for_recipient(current_user.id, peer_id)

class MarkMessageAsRead:

    def __init__(self, message_repo: MessageRepository):
        self.message_repo = message_repo

    async def execute(self, message_id: UUID) -> None:
        await self.message_repo.mark_as_read(message_id)

class GetCoachInbox:

    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def execute(self, current_user: User) -> CoachInboxResponse:
        if current_user.role not in (UserRole.INSTRUCTOR, UserRole.ADMIN):
            raise ValueError('Solo instructores o administradores pueden ver esta bandeja')
        coach_id = current_user.id
        msgs = await self.message_repo.get_messages_involving_user(coach_id)
        unread_map = await self.message_repo.count_unread_by_sender_for_recipient(coach_id)
        last_by_peer: dict[UUID, Message] = {}
        for m in msgs:
            peer = m.recipient_id if m.sender_id == coach_id else m.sender_id
            if peer not in last_by_peer:
                last_by_peer[peer] = m
        items: list[InboxThreadItem] = []
        for peer_id, last in last_by_peer.items():
            peer_user = await self.user_repo.find_by_id(peer_id)
            if not peer_user:
                continue
            if current_user.role == UserRole.INSTRUCTOR and peer_user.role != UserRole.USER:
                continue
            raw = last.content or ''
            preview = raw[:120] + ('…' if len(raw) > 120 else '')
            items.append(InboxThreadItem(peer_id=peer_id, peer_name=(peer_user.full_name or '').strip() or (peer_user.email or 'Usuario'), peer_email=peer_user.email, last_message_preview=preview, last_message_at=last.created_at, last_message_from_me=last.sender_id == coach_id, unread_count=unread_map.get(peer_id, 0)))
        items.sort(key=lambda x: (0 if x.unread_count > 0 else 1, -x.last_message_at.timestamp()))
        return CoachInboxResponse(threads=items)
