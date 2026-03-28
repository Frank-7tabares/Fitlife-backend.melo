import pytest
from uuid import uuid4
from datetime import datetime
from src.application.use_cases.message_use_cases import SendMessage, GetMessagesByUser, MarkMessageAsRead
from src.application.dtos.message_dtos import SendMessageRequest, MessageListResponse
from src.domain.entities.message import Message, MessageType
from src.domain.entities.user import User, UserRole
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
class TestSendMessage:

    async def test_send_message_success(self):
        sender_id = uuid4()
        recipient_id = uuid4()
        recipient = User(id=recipient_id, email='recipient@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        instructor_user = User(id=sender_id, email='coach@example.com', password_hash='hash', role=UserRole.INSTRUCTOR, is_active=True, created_at=datetime.utcnow())
        assignment = MagicMock()
        assignment.instructor_id = sender_id
        message_repo = AsyncMock()
        message_repo.save = AsyncMock(side_effect=lambda msg: msg)
        user_repo = AsyncMock()

        async def find_by_id_side(uid):
            if uid == recipient_id:
                return recipient
            if uid == sender_id:
                return instructor_user
            return None
        user_repo.find_by_id.side_effect = find_by_id_side
        instructor_repo = AsyncMock()
        instructor_repo.find_active_assignment.return_value = assignment
        use_case = SendMessage(message_repo, user_repo, instructor_repo)
        result = await use_case.execute(sender_id, SendMessageRequest(recipient_id=recipient_id, subject='Test Message', content='Hello, this is a test message', message_type=MessageType.INSTRUCTOR_MESSAGE))
        assert result.recipient_id == recipient_id
        assert result.sender_id == sender_id
        assert result.content == 'Hello, this is a test message'
        assert result.message_type == MessageType.INSTRUCTOR_MESSAGE
        assert message_repo.save.called

    async def test_send_message_recipient_not_found(self):
        sender_id = uuid4()
        recipient_id = uuid4()
        message_repo = AsyncMock()
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = None
        instructor_repo = AsyncMock()
        instructor_repo.find_by_id.return_value = None
        use_case = SendMessage(message_repo, user_repo, instructor_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(sender_id, SendMessageRequest(recipient_id=recipient_id, content='Test', message_type=MessageType.INSTRUCTOR_MESSAGE))
        assert 'not found' in str(exc.value).lower()

    async def test_send_message_instructor_to_athlete_without_assignment(self):
        sender_id = uuid4()
        recipient_id = uuid4()
        recipient = User(id=recipient_id, email='recipient@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        instructor_user = User(id=sender_id, email='coach@example.com', password_hash='hash', role=UserRole.INSTRUCTOR, is_active=True, created_at=datetime.utcnow())
        message_repo = AsyncMock()
        message_repo.save = AsyncMock(side_effect=lambda msg: msg)
        user_repo = AsyncMock()

        async def find_by_id_side(uid):
            if uid == recipient_id:
                return recipient
            if uid == sender_id:
                return instructor_user
            return None
        user_repo.find_by_id.side_effect = find_by_id_side
        instructor_repo = AsyncMock()
        use_case = SendMessage(message_repo, user_repo, instructor_repo)
        result = await use_case.execute(sender_id, SendMessageRequest(recipient_id=recipient_id, content='Test', message_type=MessageType.INSTRUCTOR_MESSAGE))
        assert result.recipient_id == recipient_id
        assert message_repo.save.called

    async def test_send_message_user_to_instructor_without_assignment_if_prior_message_exists(self):
        sender_id = uuid4()
        recipient_id = uuid4()
        athlete = User(id=sender_id, email='athlete@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        coach_user = User(id=recipient_id, email='coach@example.com', password_hash='hash', role=UserRole.INSTRUCTOR, is_active=True, created_at=datetime.utcnow())
        prior_msg = Message(id=uuid4(), sender_id=recipient_id, recipient_id=sender_id, subject=None, content='hola', message_type=MessageType.INSTRUCTOR_MESSAGE, is_read=False, created_at=datetime.utcnow())
        message_repo = AsyncMock()
        message_repo.save = AsyncMock(side_effect=lambda msg: msg)
        message_repo.get_by_sender_and_recipient = AsyncMock(return_value=[prior_msg])
        user_repo = AsyncMock()

        async def find_by_id_side(uid):
            if uid == sender_id:
                return athlete
            if uid == recipient_id:
                return coach_user
            return None
        user_repo.find_by_id.side_effect = find_by_id_side
        instructor_repo = AsyncMock()
        instructor_repo.find_active_assignment.return_value = None
        use_case = SendMessage(message_repo, user_repo, instructor_repo)
        result = await use_case.execute(sender_id, SendMessageRequest(recipient_id=recipient_id, content='respondo', message_type=MessageType.USER_MESSAGE))
        assert result.recipient_id == recipient_id
        assert message_repo.save.called

    async def test_send_system_notification(self):
        sender_id = uuid4()
        recipient_id = uuid4()
        recipient = User(id=recipient_id, email='recipient@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        message_repo = AsyncMock()
        message_repo.save = AsyncMock(side_effect=lambda msg: msg)
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = recipient
        instructor_repo = AsyncMock()
        use_case = SendMessage(message_repo, user_repo, instructor_repo)
        result = await use_case.execute(sender_id, SendMessageRequest(recipient_id=recipient_id, content='New routine assigned', message_type=MessageType.SYSTEM_NOTIFICATION))
        assert result.message_type == MessageType.SYSTEM_NOTIFICATION
        assert result.is_read is False

@pytest.mark.asyncio
class TestGetMessagesByUser:

    async def test_get_messages_success(self):
        user_id = uuid4()
        sender_id = uuid4()
        messages = [Message(id=uuid4(), sender_id=sender_id, recipient_id=user_id, subject='Mensaje 1', content='Contenido 1', message_type=MessageType.INSTRUCTOR_MESSAGE, is_read=False, created_at=datetime.utcnow()), Message(id=uuid4(), sender_id=sender_id, recipient_id=user_id, subject='Mensaje 2', content='Contenido 2', message_type=MessageType.INSTRUCTOR_MESSAGE, is_read=True, created_at=datetime.utcnow())]
        message_repo = AsyncMock()
        message_repo.get_by_recipient.return_value = messages
        message_repo.count_unread_by_recipient.return_value = 1
        use_case = GetMessagesByUser(message_repo)
        result = await use_case.execute(user_id)
        assert result.total == 2
        assert result.unread_count == 1
        assert len(result.messages) == 2
        assert result.messages[0].is_read is False
        assert result.messages[1].is_read is True

    async def test_get_messages_empty(self):
        user_id = uuid4()
        message_repo = AsyncMock()
        message_repo.get_by_recipient.return_value = []
        message_repo.count_unread_by_recipient.return_value = 0
        use_case = GetMessagesByUser(message_repo)
        result = await use_case.execute(user_id)
        assert result.total == 0
        assert result.unread_count == 0
        assert len(result.messages) == 0

    async def test_get_messages_with_pagination(self):
        user_id = uuid4()
        message_repo = AsyncMock()
        message_repo.get_by_recipient.return_value = []
        message_repo.count_unread_by_recipient.return_value = 0
        use_case = GetMessagesByUser(message_repo)
        result = await use_case.execute(user_id, skip=10, limit=20)
        message_repo.get_by_recipient.assert_called_with(user_id, 10, 20)

@pytest.mark.asyncio
class TestMarkMessageAsRead:

    async def test_mark_as_read_success(self):
        message_id = uuid4()
        message_repo = AsyncMock()
        message_repo.mark_as_read = AsyncMock()
        use_case = MarkMessageAsRead(message_repo)
        await use_case.execute(message_id)
        message_repo.mark_as_read.assert_called_once_with(message_id)
