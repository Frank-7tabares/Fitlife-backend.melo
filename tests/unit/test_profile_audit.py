"""Tests para auditoría de perfil."""
import pytest
from uuid import uuid4
from datetime import datetime
from src.application.use_cases.get_profile_audit import GetProfileAudit
from src.domain.entities.user import User, UserRole, Gender, FitnessGoal
from src.domain.entities.audit import ProfileAuditLog
from unittest.mock import AsyncMock


@pytest.mark.asyncio
class TestGetProfileAudit:
    """Tests para obtener historial de auditoría del perfil."""

    async def test_get_audit_history_success(self):
        """Obtiene historial de auditoría exitosamente."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hash",
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.utcnow()
        )

        audit_logs = [
            ProfileAuditLog(
                id=uuid4(),
                user_id=user_id,
                changed_by=user_id,
                changes={"full_name": {"old": None, "new": "John Doe"}},
                timestamp=datetime.utcnow()
            ),
            ProfileAuditLog(
                id=uuid4(),
                user_id=user_id,
                changed_by=user_id,
                changes={"age": {"old": None, "new": 30}},
                timestamp=datetime.utcnow()
            ),
        ]

        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user

        audit_repo = AsyncMock()
        audit_repo.get_logs_by_user_id.return_value = audit_logs

        use_case = GetProfileAudit(user_repo, audit_repo)
        result = await use_case.execute(user_id)

        assert result.user_id == user_id
        assert result.total == 2
        assert len(result.logs) == 2
        assert result.logs[0].changes["full_name"]["new"] == "John Doe"
        assert result.logs[1].changes["age"]["new"] == 30

    async def test_get_audit_history_empty(self):
        """Devuelve historial vacío si no hay cambios."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hash",
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.utcnow()
        )

        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user

        audit_repo = AsyncMock()
        audit_repo.get_logs_by_user_id.return_value = []

        use_case = GetProfileAudit(user_repo, audit_repo)
        result = await use_case.execute(user_id)

        assert result.user_id == user_id
        assert result.total == 0
        assert len(result.logs) == 0

    async def test_get_audit_history_user_not_found(self):
        """Falla si usuario no existe."""
        user_id = uuid4()

        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = None

        audit_repo = AsyncMock()

        use_case = GetProfileAudit(user_repo, audit_repo)

        with pytest.raises(ValueError) as exc:
            await use_case.execute(user_id)

        assert "not found" in str(exc.value).lower()

    async def test_get_audit_history_multiple_field_changes(self):
        """Obtiene historial con cambios en múltiples campos."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hash",
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.utcnow()
        )

        audit_log = ProfileAuditLog(
            id=uuid4(),
            user_id=user_id,
            changed_by=user_id,
            changes={
                "full_name": {"old": "John", "new": "John Doe"},
                "age": {"old": 25, "new": 30},
                "gender": {"old": None, "new": "MALE"},
                "height": {"old": 175.0, "new": 180.0},
                "fitness_goal": {"old": None, "new": "WEIGHT_LOSS"}
            },
            timestamp=datetime.utcnow()
        )

        user_repo = AsyncMock()
        user_repo.find_by_id.return_value = user

        audit_repo = AsyncMock()
        audit_repo.get_logs_by_user_id.return_value = [audit_log]

        use_case = GetProfileAudit(user_repo, audit_repo)
        result = await use_case.execute(user_id)

        assert result.total == 1
        changes = result.logs[0].changes
        assert changes["full_name"]["new"] == "John Doe"
        assert changes["age"]["new"] == 30
        assert changes["gender"]["new"] == "MALE"
        assert changes["height"]["new"] == 180.0
        assert changes["fitness_goal"]["new"] == "WEIGHT_LOSS"
