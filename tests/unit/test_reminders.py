import pytest
from uuid import uuid4
from datetime import datetime
from src.application.use_cases.reminder_use_cases import CreateReminder, GetRemindersByUser, GetReminderById, UpdateReminder, DeleteReminder
from src.application.dtos.reminder_dtos import CreateReminderRequest, UpdateReminderRequest, ReminderListResponse
from src.domain.entities.reminder import Reminder, ReminderType, ReminderFrequency
from src.domain.entities.user import User, UserRole
from unittest.mock import AsyncMock

@pytest.mark.asyncio
class TestCreateReminder:

    async def test_create_reminder_success(self):
        user_id = uuid4()
        user = User(id=user_id, email='user@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.save = AsyncMock(side_effect=lambda reminder: reminder)
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        use_case = CreateReminder(reminder_repo, user_repo)
        result = await use_case.execute(user_id, CreateReminderRequest(reminder_type=ReminderType.TRAINING, title='Morning Workout', description='Daily morning exercise routine', scheduled_time='07:00', timezone='America/Bogota', frequency=ReminderFrequency.DAILY))
        assert result.user_id == user_id
        assert result.title == 'Morning Workout'
        assert result.reminder_type == ReminderType.TRAINING
        assert result.scheduled_time == '07:00'
        assert result.timezone == 'America/Bogota'
        assert result.frequency == ReminderFrequency.DAILY
        assert result.is_active is True
        assert reminder_repo.save.called

    async def test_create_reminder_physical_record(self):
        user_id = uuid4()
        user = User(id=user_id, email='user@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.save = AsyncMock(side_effect=lambda reminder: reminder)
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        use_case = CreateReminder(reminder_repo, user_repo)
        result = await use_case.execute(user_id, CreateReminderRequest(reminder_type=ReminderType.PHYSICAL_RECORD, title='Weekly Measurements', scheduled_time='20:00', timezone='UTC', frequency=ReminderFrequency.WEEKLY))
        assert result.reminder_type == ReminderType.PHYSICAL_RECORD
        assert result.frequency == ReminderFrequency.WEEKLY

    async def test_create_reminder_instructor_followup(self):
        user_id = uuid4()
        user = User(id=user_id, email='user@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.save = AsyncMock(side_effect=lambda reminder: reminder)
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        use_case = CreateReminder(reminder_repo, user_repo)
        result = await use_case.execute(user_id, CreateReminderRequest(reminder_type=ReminderType.INSTRUCTOR_FOLLOWUP, title='Check-in with instructor', scheduled_time='19:00', timezone='UTC', frequency=ReminderFrequency.MONTHLY))
        assert result.reminder_type == ReminderType.INSTRUCTOR_FOLLOWUP
        assert result.frequency == ReminderFrequency.MONTHLY

    async def test_create_reminder_user_not_found(self):
        user_id = uuid4()
        reminder_repo = AsyncMock()
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = None
        use_case = CreateReminder(reminder_repo, user_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(user_id, CreateReminderRequest(reminder_type=ReminderType.TRAINING, title='Test', scheduled_time='10:00', timezone='UTC', frequency=ReminderFrequency.ONCE))
        assert 'not found' in str(exc.value).lower()

    async def test_create_reminder_once_frequency(self):
        user_id = uuid4()
        user = User(id=user_id, email='user@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.save = AsyncMock(side_effect=lambda reminder: reminder)
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        use_case = CreateReminder(reminder_repo, user_repo)
        result = await use_case.execute(user_id, CreateReminderRequest(reminder_type=ReminderType.TRAINING, title='One-time reminder', scheduled_time='18:00', timezone='UTC', frequency=ReminderFrequency.ONCE))
        assert result.frequency == ReminderFrequency.ONCE

@pytest.mark.asyncio
class TestGetRemindersByUser:

    async def test_get_reminders_success(self):
        user_id = uuid4()
        reminders = [Reminder(id=uuid4(), user_id=user_id, reminder_type=ReminderType.TRAINING, title='Morning Workout', description='Daily routine', scheduled_time='07:00', timezone='UTC', frequency=ReminderFrequency.DAILY, is_active=True, created_at=datetime.utcnow()), Reminder(id=uuid4(), user_id=user_id, reminder_type=ReminderType.PHYSICAL_RECORD, title='Weekly Check', scheduled_time='20:00', timezone='UTC', frequency=ReminderFrequency.WEEKLY, is_active=False, created_at=datetime.utcnow())]
        active_reminders = [reminders[0]]
        reminder_repo = AsyncMock()
        reminder_repo.get_by_user.return_value = reminders
        reminder_repo.get_active_by_user.return_value = active_reminders
        use_case = GetRemindersByUser(reminder_repo)
        result = await use_case.execute(user_id)
        assert result.total == 2
        assert result.active_count == 1
        assert len(result.reminders) == 2
        assert result.reminders[0].is_active is True
        assert result.reminders[1].is_active is False

    async def test_get_active_reminders_only(self):
        user_id = uuid4()
        active_reminders = [Reminder(id=uuid4(), user_id=user_id, reminder_type=ReminderType.TRAINING, title='Workout', scheduled_time='07:00', timezone='UTC', frequency=ReminderFrequency.DAILY, is_active=True, created_at=datetime.utcnow())]
        reminder_repo = AsyncMock()
        reminder_repo.get_by_user.return_value = active_reminders
        reminder_repo.get_active_by_user.return_value = active_reminders
        use_case = GetRemindersByUser(reminder_repo)
        result = await use_case.execute(user_id)
        assert result.active_count == 1
        assert all((r.is_active for r in result.reminders))

    async def test_get_reminders_empty(self):
        user_id = uuid4()
        reminder_repo = AsyncMock()
        reminder_repo.get_by_user.return_value = []
        reminder_repo.get_active_by_user.return_value = []
        use_case = GetRemindersByUser(reminder_repo)
        result = await use_case.execute(user_id)
        assert result.total == 0
        assert result.active_count == 0
        assert len(result.reminders) == 0

    async def test_get_reminders_with_pagination(self):
        user_id = uuid4()
        reminder_repo = AsyncMock()
        reminder_repo.get_by_user.return_value = []
        reminder_repo.get_active_by_user.return_value = []
        use_case = GetRemindersByUser(reminder_repo)
        result = await use_case.execute(user_id, skip=5, limit=25)
        reminder_repo.get_by_user.assert_called_with(user_id, 5, 25)

@pytest.mark.asyncio
class TestGetReminderById:

    async def test_get_reminder_by_id_success(self):
        reminder_id = uuid4()
        user_id = uuid4()
        reminder = Reminder(id=reminder_id, user_id=user_id, reminder_type=ReminderType.TRAINING, title='Morning Workout', scheduled_time='07:00', timezone='UTC', frequency=ReminderFrequency.DAILY, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.find_by_id.return_value = reminder
        use_case = GetReminderById(reminder_repo)
        result = await use_case.execute(reminder_id)
        assert result.id == reminder_id
        assert result.title == 'Morning Workout'
        assert result.user_id == user_id

    async def test_get_reminder_not_found(self):
        reminder_id = uuid4()
        reminder_repo = AsyncMock()
        reminder_repo.find_by_id.return_value = None
        use_case = GetReminderById(reminder_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(reminder_id)
        assert 'not found' in str(exc.value).lower()

@pytest.mark.asyncio
class TestUpdateReminder:

    async def test_update_reminder_success(self):
        reminder_id = uuid4()
        user_id = uuid4()
        existing_reminder = Reminder(id=reminder_id, user_id=user_id, reminder_type=ReminderType.TRAINING, title='Old Title', scheduled_time='07:00', timezone='UTC', frequency=ReminderFrequency.DAILY, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.find_by_id.return_value = existing_reminder
        reminder_repo.update = AsyncMock(side_effect=lambda reminder: reminder)
        use_case = UpdateReminder(reminder_repo)
        result = await use_case.execute(reminder_id, UpdateReminderRequest(title='New Title', scheduled_time='08:00'))
        assert result.title == 'New Title'
        assert result.scheduled_time == '08:00'
        assert reminder_repo.update.called

    async def test_update_reminder_partial(self):
        reminder_id = uuid4()
        user_id = uuid4()
        existing_reminder = Reminder(id=reminder_id, user_id=user_id, reminder_type=ReminderType.TRAINING, title='Original Title', description='Original description', scheduled_time='07:00', timezone='UTC', frequency=ReminderFrequency.DAILY, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.find_by_id.return_value = existing_reminder
        reminder_repo.update = AsyncMock(side_effect=lambda reminder: reminder)
        use_case = UpdateReminder(reminder_repo)
        result = await use_case.execute(reminder_id, UpdateReminderRequest(title='Updated Title'))
        assert result.title == 'Updated Title'
        assert result.description == 'Original description'

    async def test_update_reminder_deactivate(self):
        reminder_id = uuid4()
        user_id = uuid4()
        existing_reminder = Reminder(id=reminder_id, user_id=user_id, reminder_type=ReminderType.TRAINING, title='Workout', scheduled_time='07:00', timezone='UTC', frequency=ReminderFrequency.DAILY, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.find_by_id.return_value = existing_reminder
        reminder_repo.update = AsyncMock(side_effect=lambda reminder: reminder)
        use_case = UpdateReminder(reminder_repo)
        result = await use_case.execute(reminder_id, UpdateReminderRequest(is_active=False))
        assert result.is_active is False

    async def test_update_reminder_not_found(self):
        reminder_id = uuid4()
        reminder_repo = AsyncMock()
        reminder_repo.find_by_id.return_value = None
        use_case = UpdateReminder(reminder_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(reminder_id, UpdateReminderRequest(title='New Title'))
        assert 'not found' in str(exc.value).lower()

@pytest.mark.asyncio
class TestDeleteReminder:

    async def test_delete_reminder_success(self):
        reminder_id = uuid4()
        user_id = uuid4()
        existing_reminder = Reminder(id=reminder_id, user_id=user_id, reminder_type=ReminderType.TRAINING, title='Workout', scheduled_time='07:00', timezone='UTC', frequency=ReminderFrequency.DAILY, is_active=True, created_at=datetime.utcnow())
        reminder_repo = AsyncMock()
        reminder_repo.find_by_id.return_value = existing_reminder
        reminder_repo.delete = AsyncMock()
        use_case = DeleteReminder(reminder_repo)
        await use_case.execute(reminder_id)
        reminder_repo.delete.assert_called_once_with(reminder_id)

    async def test_delete_reminder_not_found(self):
        reminder_id = uuid4()
        reminder_repo = AsyncMock()
        reminder_repo.find_by_id.return_value = None
        use_case = DeleteReminder(reminder_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(reminder_id)
        assert 'not found' in str(exc.value).lower()
