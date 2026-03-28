import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.application.use_cases.password_reset_request import PasswordResetRequest
from src.application.use_cases.password_reset import PasswordReset
from src.application.use_cases.password_change import PasswordChange
from src.domain.entities.user import User, UserRole
from src.domain.entities.password_reset_token import PasswordResetToken, ResetTokenStatus
from src.domain.entities.password_history import PasswordHistory
from src.application.dtos.auth_dtos import PasswordResetDto, PasswordChangeDto
from src.infrastructure.security.password_validator import PasswordValidator
from src.infrastructure.security.password_hasher import PasswordHasher
from unittest.mock import AsyncMock, MagicMock

class TestPasswordValidator:

    def test_valid_password(self):
        is_valid, msg = PasswordValidator.validate('SecurePass123!')
        assert is_valid is True
        assert msg == ''

    def test_password_too_short(self):
        is_valid, msg = PasswordValidator.validate('Pass1!')
        assert is_valid is False
        assert 'Mínimo' in msg

    def test_password_no_uppercase(self):
        is_valid, msg = PasswordValidator.validate('securepass123!')
        assert is_valid is False
        assert 'mayúscula' in msg

    def test_password_no_lowercase(self):
        is_valid, msg = PasswordValidator.validate('SECUREPASS123!')
        assert is_valid is False
        assert 'minúscula' in msg

    def test_password_no_digit(self):
        is_valid, msg = PasswordValidator.validate('SecurePass!')
        assert is_valid is False
        assert 'número' in msg

    def test_password_no_special_char(self):
        is_valid, msg = PasswordValidator.validate('SecurePass123')
        assert is_valid is False
        assert 'especial' in msg

@pytest.mark.asyncio
class TestPasswordResetRequest:

    async def test_reset_request_user_exists(self):
        user_id = uuid4()
        user = User(id=user_id, email='test@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow(), full_name='Test User')
        user_repo = AsyncMock()
        user_repo.find_by_email.return_value = user
        reset_repo = AsyncMock()
        reset_repo.save = AsyncMock(return_value=None)
        use_case = PasswordResetRequest(user_repo, reset_repo)
        from src.application.dtos.auth_dtos import PasswordResetRequestDto
        result = await use_case.execute(PasswordResetRequestDto(email='test@example.com'))
        assert 'email' in result.get('message', '').lower() or 'contraseña' in result.get('message', '').lower()
        assert reset_repo.save.called

    async def test_reset_request_user_not_exists(self):
        user_repo = AsyncMock()
        user_repo.find_by_email.return_value = None
        reset_repo = AsyncMock()
        use_case = PasswordResetRequest(user_repo, reset_repo)
        from src.application.dtos.auth_dtos import PasswordResetRequestDto
        result = await use_case.execute(PasswordResetRequestDto(email='nonexistent@example.com'))
        assert 'message' in result
        assert not reset_repo.save.called

@pytest.mark.asyncio
class TestPasswordReset:

    async def test_reset_with_valid_token(self):
        user_id = uuid4()
        token_id = uuid4()
        user = User(id=user_id, email='test@example.com', password_hash=PasswordHasher.hash('OldPassword123!'), role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        reset_token = PasswordResetToken(id=token_id, user_id=user_id, token='valid_token_123', expires_at=datetime.utcnow() + timedelta(hours=1), status=ResetTokenStatus.PENDING, created_at=datetime.utcnow())
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        user_repo.update = AsyncMock(return_value=user)
        reset_repo = AsyncMock()
        reset_repo.find_by_token.return_value = reset_token
        reset_repo.mark_as_used = AsyncMock()
        reset_repo.delete_expired_tokens = AsyncMock()
        history_repo = AsyncMock()
        history_repo.get_last_n_hashes.return_value = []
        history_repo.save = AsyncMock()
        use_case = PasswordReset(user_repo, reset_repo, history_repo)
        result = await use_case.execute(PasswordResetDto(token='valid_token_123', new_password='NewPassword456!'))
        assert result.message
        assert reset_repo.mark_as_used.called

    async def test_reset_with_expired_token(self):
        token_id = uuid4()
        reset_token = PasswordResetToken(id=token_id, user_id=uuid4(), token='expired_token', expires_at=datetime.utcnow() - timedelta(hours=1), status=ResetTokenStatus.EXPIRED, created_at=datetime.utcnow())
        user_repo = AsyncMock()
        reset_repo = AsyncMock()
        reset_repo.find_by_token.return_value = reset_token
        history_repo = AsyncMock()
        use_case = PasswordReset(user_repo, reset_repo, history_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(PasswordResetDto(token='expired_token', new_password='NewPassword456!'))
        assert 'expirado' in str(exc.value).lower()

    async def test_reset_with_weak_password(self):
        reset_token = PasswordResetToken(id=uuid4(), user_id=uuid4(), token='valid_token', expires_at=datetime.utcnow() + timedelta(hours=1), status=ResetTokenStatus.PENDING, created_at=datetime.utcnow())
        user = User(id=uuid4(), email='test@example.com', password_hash='hash', role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        reset_repo = AsyncMock()
        reset_repo.find_by_token.return_value = reset_token
        history_repo = AsyncMock()
        history_repo.get_last_n_hashes.return_value = []
        use_case = PasswordReset(user_repo, reset_repo, history_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(PasswordResetDto(token='valid_token', new_password='weak'))
        assert 'débil' in str(exc.value).lower()

@pytest.mark.asyncio
class TestPasswordChange:

    async def test_change_password_success(self):
        user_id = uuid4()
        old_password = 'OldPassword123!'
        new_password = 'NewPassword456!'
        user = User(id=user_id, email='test@example.com', password_hash=PasswordHasher.hash(old_password), role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        user_repo.update = AsyncMock(return_value=user)
        history_repo = AsyncMock()
        history_repo.get_last_n_hashes.return_value = []
        history_repo.save = AsyncMock()
        history_repo.delete_old_entries = AsyncMock()
        use_case = PasswordChange(user_repo, history_repo)
        result = await use_case.execute(str(user_id), PasswordChangeDto(current_password=old_password, new_password=new_password))
        assert any((w in result.message.lower() for w in ('exitoso', 'actualizado', 'actualizada', 'exitosamente')))
        assert user_repo.update.called

    async def test_change_password_wrong_current(self):
        user_id = uuid4()
        user = User(id=user_id, email='test@example.com', password_hash=PasswordHasher.hash('OldPassword123!'), role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        history_repo = AsyncMock()
        use_case = PasswordChange(user_repo, history_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(str(user_id), PasswordChangeDto(current_password='WrongPassword123!', new_password='NewPassword456!'))
        assert 'actual' in str(exc.value).lower() or 'incorrecto' in str(exc.value).lower()

    async def test_change_password_weak_new(self):
        user_id = uuid4()
        old_password = 'OldPassword123!'
        user = User(id=user_id, email='test@example.com', password_hash=PasswordHasher.hash(old_password), role=UserRole.USER, is_active=True, created_at=datetime.utcnow())
        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user
        history_repo = AsyncMock()
        use_case = PasswordChange(user_repo, history_repo)
        with pytest.raises(ValueError) as exc:
            await use_case.execute(str(user_id), PasswordChangeDto(current_password=old_password, new_password='weak'))
        assert 'débil' in str(exc.value).lower()
