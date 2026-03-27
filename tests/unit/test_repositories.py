"""
Tests unitarios — Repositorios SQLAlchemy.
La sesión de base de datos es un AsyncMock completo; los modelos
se simulan con MagicMock para evitar depender de la DB real.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers para crear mock-models que simulan los ORM models
# ---------------------------------------------------------------------------

def _mock_user_model(user_id=None, email="u@e.com", password_hash="h",
                     role="USER", is_active=True, full_name=None,
                     created_at=None, updated_at=None, version=1):
    m = MagicMock()
    m.id = str(user_id or uuid4())
    m.email = email
    m.password_hash = password_hash
    m.role = role
    m.is_active = is_active
    m.full_name = full_name
    m.created_at = created_at or datetime.utcnow()
    m.updated_at = updated_at
    m.version = version
    return m


def _mock_assessment_model(assessment_id=None, user_id=None):
    m = MagicMock()
    m.id = str(assessment_id or uuid4())
    m.user_id = str(user_id or uuid4())
    m.fitness_score = 75.0
    m.category = "GOOD"
    m.body_age = 28.0
    m.comparison = "BODY_YOUNGER"
    m.responses = {"q1": 7}
    m.created_at = datetime.utcnow()
    return m


def _mock_physical_record_model(record_id=None, user_id=None):
    m = MagicMock()
    m.id = str(record_id or uuid4())
    m.user_id = str(user_id or uuid4())
    m.weight = 70.0
    m.height = 175.0
    m.body_fat_percentage = None
    m.waist = None
    m.hip = None
    m.activity_level = "MODERATE"
    m.recorded_at = datetime.utcnow()
    return m


def _mock_routine_model(routine_id=None, creator_id=None):
    m = MagicMock()
    m.id = str(routine_id or uuid4())
    m.name = "Full Body"
    m.description = "All muscles"
    m.goal = "STRENGTH"
    m.level = "BEGINNER"
    m.exercises_data = [
        {"exercise_id": str(uuid4()), "sets": 3, "reps": 10, "rest_seconds": 60}
    ]
    m.creator_id = str(creator_id or uuid4())
    return m


def _mock_assignment_model(user_id=None, routine_id=None):
    m = MagicMock()
    m.user_id = str(user_id or uuid4())
    m.routine_id = str(routine_id or uuid4())
    m.assigned_at = datetime.utcnow()
    m.is_active = True
    return m


def _mock_nutrition_plan_model(plan_id=None, user_id=None):
    m = MagicMock()
    m.id = str(plan_id or uuid4())
    m.user_id = str(user_id or uuid4())
    m.name = "Week 1"
    m.description = "First week"
    m.week_number = 1
    m.year = 2026
    m.plans_data = [
        {
            "day_of_week": 0,
            "meals": [{"name": "Oats", "description": "Breakfast",
                       "calories": 300, "protein": 15.0, "carbs": 50.0, "fats": 5.0}]
        }
    ]
    m.is_active = True
    m.created_at = datetime.utcnow()
    return m


def _make_session():
    """Crea un AsyncMock que simula AsyncSession de SQLAlchemy."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    return session


def _result_with(scalar_value):
    """Crea un mock de result que devuelve scalar_one_or_none()."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_value
    return result


def _result_with_scalars(values):
    """Crea un mock de result que devuelve scalars().all()."""
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = values
    result.scalars.return_value = scalars
    return result


# ---------------------------------------------------------------------------
# SQLAlchemyUserRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyUserRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        from src.domain.entities.user import User, UserRole
        session = _make_session()
        repo = SQLAlchemyUserRepository(session)
        user = User(
            id=uuid4(), email="a@b.com", password_hash="h",
            role=UserRole.USER, is_active=True, created_at=datetime.utcnow()
        )
        result = await repo.save(user)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is user

    @pytest.mark.asyncio
    async def test_find_by_id_returns_user_when_found(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        uid = uuid4()
        model = _mock_user_model(user_id=uid, email="found@x.com")
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyUserRepository(session)
        user = await repo.find_by_id(uid)
        assert user is not None
        assert user.email == "found@x.com"
        from uuid import UUID
        assert user.id == UUID(model.id)

    @pytest.mark.asyncio
    async def test_find_by_id_returns_none_when_not_found(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyUserRepository(session)
        user = await repo.find_by_id(uuid4())
        assert user is None

    @pytest.mark.asyncio
    async def test_find_by_email_returns_user(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        model = _mock_user_model(email="test@x.com", full_name="Ana")
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyUserRepository(session)
        user = await repo.find_by_email("test@x.com")
        assert user is not None
        assert user.full_name == "Ana"

    @pytest.mark.asyncio
    async def test_find_by_email_returns_none(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyUserRepository(session)
        user = await repo.find_by_email("ghost@x.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_exists_by_email_returns_true(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        model = _mock_user_model()
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyUserRepository(session)
        exists = await repo.exists_by_email("exists@x.com")
        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_by_email_returns_false(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyUserRepository(session)
        exists = await repo.exists_by_email("nope@x.com")
        assert exists is False

    @pytest.mark.asyncio
    async def test_update_success_increments_version(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        from src.domain.entities.user import User, UserRole
        model = _mock_user_model(version=1)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyUserRepository(session)
        uid_str = model.id
        from uuid import UUID
        user = User(
            id=UUID(uid_str), email="u@x.com", password_hash="h",
            role=UserRole.USER, is_active=True, created_at=datetime.utcnow(),
            version=1
        )
        result = await repo.update(user)
        assert model.version == 2
        session.commit.assert_awaited_once()
        assert result.version == 2

    @pytest.mark.asyncio
    async def test_update_version_conflict_raises(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        from src.domain.entities.user import User, UserRole
        model = _mock_user_model(version=2)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyUserRepository(session)
        from uuid import UUID
        user = User(
            id=UUID(model.id), email="u@x.com", password_hash="h",
            role=UserRole.USER, is_active=True, created_at=datetime.utcnow(),
            version=1  # stale version
        )
        with pytest.raises(ValueError, match="Concurrency conflict"):
            await repo.update(user)

    @pytest.mark.asyncio
    async def test_update_user_not_found_returns_user(self):
        from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
        from src.domain.entities.user import User, UserRole
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyUserRepository(session)
        user = User(
            id=uuid4(), email="ghost@x.com", password_hash="h",
            role=UserRole.USER, is_active=True, created_at=datetime.utcnow()
        )
        result = await repo.update(user)
        assert result is user
        session.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# SQLAlchemyAssessmentRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyAssessmentRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_assessment_repository import SQLAlchemyAssessmentRepository
        from src.domain.entities.assessment import Assessment, AssessmentCategory, BodyAgeComparison
        session = _make_session()
        repo = SQLAlchemyAssessmentRepository(session)
        a = Assessment(
            id=uuid4(), user_id=uuid4(), fitness_score=80.0,
            category=AssessmentCategory.GOOD, body_age=27.0,
            comparison=BodyAgeComparison.BODY_YOUNGER,
            responses={"q": 8}, created_at=datetime.utcnow()
        )
        result = await repo.save(a)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is a

    @pytest.mark.asyncio
    async def test_find_by_user_id_returns_list(self):
        from src.infrastructure.repositories.sqlalchemy_assessment_repository import SQLAlchemyAssessmentRepository
        uid = uuid4()
        models = [_mock_assessment_model(user_id=uid), _mock_assessment_model(user_id=uid)]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(models)
        repo = SQLAlchemyAssessmentRepository(session)
        result = await repo.find_by_user_id(uid)
        assert len(result) == 2
        assert result[0].fitness_score == 75.0

    @pytest.mark.asyncio
    async def test_find_by_user_id_empty_list(self):
        from src.infrastructure.repositories.sqlalchemy_assessment_repository import SQLAlchemyAssessmentRepository
        session = _make_session()
        session.execute.return_value = _result_with_scalars([])
        repo = SQLAlchemyAssessmentRepository(session)
        result = await repo.find_by_user_id(uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_map_to_entity_sets_all_fields(self):
        from src.infrastructure.repositories.sqlalchemy_assessment_repository import SQLAlchemyAssessmentRepository
        uid = uuid4()
        model = _mock_assessment_model(user_id=uid)
        model.fitness_score = 90.0
        model.category = "EXCELLENT"
        session = _make_session()
        session.execute.return_value = _result_with_scalars([model])
        repo = SQLAlchemyAssessmentRepository(session)
        result = await repo.find_by_user_id(uid)
        assert result[0].fitness_score == 90.0


# ---------------------------------------------------------------------------
# SQLAlchemyPhysicalRecordRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyPhysicalRecordRepository:
    @pytest.mark.asyncio
    async def test_save_persists_record(self):
        from src.infrastructure.repositories.sqlalchemy_physical_record_repository import SQLAlchemyPhysicalRecordRepository
        from src.domain.entities.physical_record import PhysicalRecord
        session = _make_session()
        repo = SQLAlchemyPhysicalRecordRepository(session)
        from src.domain.entities.physical_record import ActivityLevel
        record = PhysicalRecord(
            id=uuid4(), user_id=uuid4(), weight=70.0, height=170.0,
            body_fat_percentage=None, waist=None, hip=None,
            activity_level=ActivityLevel.LIGHT, recorded_at=datetime.utcnow()
        )
        result = await repo.save(record)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is record

    @pytest.mark.asyncio
    async def test_find_by_user_id_returns_records(self):
        from src.infrastructure.repositories.sqlalchemy_physical_record_repository import SQLAlchemyPhysicalRecordRepository
        uid = uuid4()
        models = [_mock_physical_record_model(user_id=uid)]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(models)
        repo = SQLAlchemyPhysicalRecordRepository(session)
        result = await repo.find_by_user_id(uid)
        assert len(result) == 1
        assert result[0].weight == 70.0

    @pytest.mark.asyncio
    async def test_find_by_user_id_empty(self):
        from src.infrastructure.repositories.sqlalchemy_physical_record_repository import SQLAlchemyPhysicalRecordRepository
        session = _make_session()
        session.execute.return_value = _result_with_scalars([])
        repo = SQLAlchemyPhysicalRecordRepository(session)
        result = await repo.find_by_user_id(uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_find_maps_optional_fields(self):
        from src.infrastructure.repositories.sqlalchemy_physical_record_repository import SQLAlchemyPhysicalRecordRepository
        uid = uuid4()
        model = _mock_physical_record_model(user_id=uid)
        model.body_fat_percentage = 22.5
        model.waist = 85.0
        model.hip = 100.0
        session = _make_session()
        session.execute.return_value = _result_with_scalars([model])
        repo = SQLAlchemyPhysicalRecordRepository(session)
        result = await repo.find_by_user_id(uid)
        assert result[0].body_fat_percentage == 22.5
        assert result[0].waist == 85.0
        assert result[0].hip == 100.0


# ---------------------------------------------------------------------------
# SQLAlchemyAuditRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyAuditRepository:
    @pytest.mark.asyncio
    async def test_save_log_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
        from src.domain.entities.audit import ProfileAuditLog
        session = _make_session()
        repo = SQLAlchemyAuditRepository(session)
        log = ProfileAuditLog(
            id=uuid4(), user_id=uuid4(), changed_by=uuid4(),
            changes={"full_name": {"old": "A", "new": "B"}},
            timestamp=datetime.utcnow()
        )
        result = await repo.save_log(log)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is log

    @pytest.mark.asyncio
    async def test_save_log_empty_changes(self):
        from src.infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
        from src.domain.entities.audit import ProfileAuditLog
        session = _make_session()
        repo = SQLAlchemyAuditRepository(session)
        log = ProfileAuditLog(
            id=uuid4(), user_id=uuid4(), changed_by=uuid4(),
            changes={}, timestamp=datetime.utcnow()
        )
        result = await repo.save_log(log)
        assert result.changes == {}


# ---------------------------------------------------------------------------
# SQLAlchemyTrainingRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyTrainingRepository:
    @pytest.mark.asyncio
    async def test_save_routine_persists(self):
        from src.infrastructure.repositories.sqlalchemy_training_repository import SQLAlchemyTrainingRepository
        from src.domain.entities.training import Routine, RoutineExercise, FitnessLevel
        session = _make_session()
        repo = SQLAlchemyTrainingRepository(session)
        routine = Routine(
            id=uuid4(), name="Push Day", description="Chest/Shoulders/Triceps",
            goal="HYPERTROPHY", level=FitnessLevel.INTERMEDIATE,
            exercises=[RoutineExercise(exercise_id=uuid4(), sets=4, reps=8, rest_seconds=90)],
            creator_id=uuid4()
        )
        result = await repo.save_routine(routine)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is routine

    @pytest.mark.asyncio
    async def test_find_routine_by_id_returns_routine(self):
        from src.infrastructure.repositories.sqlalchemy_training_repository import SQLAlchemyTrainingRepository
        rid = uuid4()
        model = _mock_routine_model(routine_id=rid)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyTrainingRepository(session)
        result = await repo.find_routine_by_id(rid)
        assert result is not None
        assert result.name == "Full Body"
        assert len(result.exercises) == 1

    @pytest.mark.asyncio
    async def test_find_routine_by_id_returns_none(self):
        from src.infrastructure.repositories.sqlalchemy_training_repository import SQLAlchemyTrainingRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyTrainingRepository(session)
        result = await repo.find_routine_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_save_routine_with_no_exercises(self):
        from src.infrastructure.repositories.sqlalchemy_training_repository import SQLAlchemyTrainingRepository
        from src.domain.entities.training import Routine, FitnessLevel
        session = _make_session()
        repo = SQLAlchemyTrainingRepository(session)
        routine = Routine(
            id=uuid4(), name="Rest", description="Active recovery",
            goal="RECOVERY", level=FitnessLevel.BEGINNER,
            exercises=[], creator_id=uuid4()
        )
        result = await repo.save_routine(routine)
        assert result.exercises == []


# ---------------------------------------------------------------------------
# SQLAlchemyTrainingAssignmentRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyTrainingAssignmentRepository:
    @pytest.mark.asyncio
    async def test_save_assignment_deactivates_previous_and_saves(self):
        from src.infrastructure.repositories.sqlalchemy_training_assignment_repository import SQLAlchemyTrainingAssignmentRepository
        from src.domain.entities.training import RoutineAssignment
        session = _make_session()
        repo = SQLAlchemyTrainingAssignmentRepository(session)
        assignment = RoutineAssignment(
            user_id=uuid4(), routine_id=uuid4(),
            assigned_at=datetime.utcnow(), is_active=True
        )
        result = await repo.save_assignment(assignment)
        assert session.execute.await_count >= 1
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is assignment

    @pytest.mark.asyncio
    async def test_find_active_assignment_returns_assignment(self):
        from src.infrastructure.repositories.sqlalchemy_training_assignment_repository import SQLAlchemyTrainingAssignmentRepository
        uid = uuid4()
        model = _mock_assignment_model(user_id=uid)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyTrainingAssignmentRepository(session)
        result = await repo.find_active_assignment(uid)
        assert result is not None
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_find_active_assignment_returns_none(self):
        from src.infrastructure.repositories.sqlalchemy_training_assignment_repository import SQLAlchemyTrainingAssignmentRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyTrainingAssignmentRepository(session)
        result = await repo.find_active_assignment(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_save_completion_persists(self):
        from src.infrastructure.repositories.sqlalchemy_training_assignment_repository import SQLAlchemyTrainingAssignmentRepository
        from src.domain.entities.training import WorkoutCompletion
        session = _make_session()
        repo = SQLAlchemyTrainingAssignmentRepository(session)
        completion = WorkoutCompletion(
            id=uuid4(), user_id=uuid4(), routine_id=uuid4(),
            completed_at=datetime.utcnow(), effort_level=8, notes="Felt good"
        )
        result = await repo.save_completion(completion)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is completion


# ---------------------------------------------------------------------------
# SQLAlchemyNutritionRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyNutritionRepository:
    @pytest.mark.asyncio
    async def test_save_active_plan_deactivates_previous(self):
        from src.infrastructure.repositories.sqlalchemy_nutrition_repository import SQLAlchemyNutritionRepository
        from src.domain.entities.nutrition import NutritionPlan, DailyPlan, Meal
        session = _make_session()
        repo = SQLAlchemyNutritionRepository(session)
        plan = NutritionPlan(
            id=uuid4(), user_id=uuid4(), name="Week 1", description="Plan",
            week_number=1, year=2026,
            daily_plans=[DailyPlan(0, [Meal("Rice", "Lunch", 500, 30.0, 80.0, 8.0)])],
            is_active=True, created_at=datetime.utcnow()
        )
        result = await repo.save(plan)
        assert session.execute.await_count >= 1
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is plan

    @pytest.mark.asyncio
    async def test_save_inactive_plan_does_not_deactivate(self):
        from src.infrastructure.repositories.sqlalchemy_nutrition_repository import SQLAlchemyNutritionRepository
        from src.domain.entities.nutrition import NutritionPlan
        session = _make_session()
        repo = SQLAlchemyNutritionRepository(session)
        plan = NutritionPlan(
            id=uuid4(), user_id=uuid4(), name="Old Plan", description="",
            week_number=50, year=2025, daily_plans=[], is_active=False,
            created_at=datetime.utcnow()
        )
        await repo.save(plan)
        session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_active_by_user_id_returns_plan(self):
        from src.infrastructure.repositories.sqlalchemy_nutrition_repository import SQLAlchemyNutritionRepository
        uid = uuid4()
        model = _mock_nutrition_plan_model(user_id=uid)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyNutritionRepository(session)
        result = await repo.find_active_by_user_id(uid)
        assert result is not None
        assert result.name == "Week 1"
        assert result.is_active is True
        assert len(result.daily_plans) == 1
        assert result.daily_plans[0].meals[0].name == "Oats"

    @pytest.mark.asyncio
    async def test_find_active_by_user_id_returns_none(self):
        from src.infrastructure.repositories.sqlalchemy_nutrition_repository import SQLAlchemyNutritionRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyNutritionRepository(session)
        result = await repo.find_active_by_user_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_map_to_entity_with_optional_meal_fields(self):
        from src.infrastructure.repositories.sqlalchemy_nutrition_repository import SQLAlchemyNutritionRepository
        uid = uuid4()
        model = _mock_nutrition_plan_model(user_id=uid)
        model.plans_data = [
            {"day_of_week": 0, "meals": [
                {"name": "Salad", "description": "Lunch",
                 "calories": None, "protein": None, "carbs": None, "fats": None}
            ]}
        ]
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyNutritionRepository(session)
        result = await repo.find_active_by_user_id(uid)
        meal = result.daily_plans[0].meals[0]
        assert meal.calories is None
        assert meal.name == "Salad"


# ---------------------------------------------------------------------------
# SQLAlchemyRefreshTokenRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyRefreshTokenRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
        from datetime import timedelta
        session = _make_session()
        repo = SQLAlchemyRefreshTokenRepository(session)
        uid = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=30)
        await repo.save(uid, "jwt.refresh.token.value", expires_at)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_find_valid_user_id_returns_user_id_when_valid(self):
        from src.infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
        from datetime import timedelta
        uid = uuid4()
        row = MagicMock()
        row.user_id = str(uid)
        row.expires_at = datetime.utcnow() + timedelta(days=1)
        row.revoked_at = None
        session = _make_session()
        session.execute.return_value = _result_with(row)
        repo = SQLAlchemyRefreshTokenRepository(session)
        result = await repo.find_valid_user_id("valid.token")
        assert result == uid

    @pytest.mark.asyncio
    async def test_find_valid_user_id_returns_none_when_not_found(self):
        from src.infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyRefreshTokenRepository(session)
        result = await repo.find_valid_user_id("unknown.token")
        assert result is None

    @pytest.mark.asyncio
    async def test_find_valid_user_id_returns_none_when_expired(self):
        from src.infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
        from datetime import timedelta
        row = MagicMock()
        row.user_id = str(uuid4())
        row.expires_at = datetime.utcnow() - timedelta(hours=1)
        row.revoked_at = None
        session = _make_session()
        session.execute.return_value = _result_with(row)
        repo = SQLAlchemyRefreshTokenRepository(session)
        result = await repo.find_valid_user_id("expired.token")
        assert result is None

    @pytest.mark.asyncio
    async def test_revoke_updates_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
        session = _make_session()
        repo = SQLAlchemyRefreshTokenRepository(session)
        await repo.revoke("token.to.revoke")
        session.execute.assert_awaited_once()
        session.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# Instructor repositories (Historia 3)
# ---------------------------------------------------------------------------

def _mock_instructor_model(iid=None, name="Coach", certifications=None, specializations="", rating_avg=0.0):
    m = MagicMock()
    m.id = str(iid or uuid4())
    m.name = name
    m.certifications = certifications or []
    m.specializations = specializations
    m.rating_avg = rating_avg
    return m


def _mock_instructor_assignment_model(aid=None, user_id=None, instructor_id=None, is_active=True):
    m = MagicMock()
    m.id = str(aid or uuid4())
    m.user_id = str(user_id or uuid4())
    m.instructor_id = str(instructor_id or uuid4())
    m.started_at = datetime.utcnow()
    m.ended_at = None
    m.is_active = is_active
    return m


class TestSQLAlchemyInstructorRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRepository
        from src.domain.entities.instructor import Instructor
        iid = uuid4()
        inst = Instructor(
            id=iid, name="C", certifications=["ACE"], specializations="Fuerza",
            rating_avg=0.0, active_users_count=0,
        )
        session = _make_session()
        repo = SQLAlchemyInstructorRepository(session)
        result = await repo.save(inst)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is inst

    @pytest.mark.asyncio
    async def test_find_all_returns_models(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRepository
        models = [_mock_instructor_model(name="A"), _mock_instructor_model(name="B")]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(models)
        repo = SQLAlchemyInstructorRepository(session)
        result = await repo.find_all()
        assert len(result) == 2
        assert result[0].name == "A"

    @pytest.mark.asyncio
    async def test_find_by_id_returns_model(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRepository
        iid = uuid4()
        m = _mock_instructor_model(iid=iid, name="X")
        session = _make_session()
        session.execute.return_value = _result_with(m)
        repo = SQLAlchemyInstructorRepository(session)
        result = await repo.find_by_id(iid)
        assert result is m
        assert result.name == "X"


class TestSQLAlchemyInstructorAssignmentRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorAssignmentRepository
        from src.domain.entities.instructor import InstructorAssignment
        uid, iid = uuid4(), uuid4()
        a = InstructorAssignment(
            id=uuid4(), user_id=uid, instructor_id=iid,
            started_at=datetime.utcnow(), ended_at=None, is_active=True,
        )
        session = _make_session()
        repo = SQLAlchemyInstructorAssignmentRepository(session)
        result = await repo.save(a)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is a

    @pytest.mark.asyncio
    async def test_find_active_by_user_returns_entity(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorAssignmentRepository
        uid, iid = uuid4(), uuid4()
        m = _mock_instructor_assignment_model(user_id=uid, instructor_id=iid, is_active=True)
        session = _make_session()
        session.execute.return_value = _result_with(m)
        repo = SQLAlchemyInstructorAssignmentRepository(session)
        result = await repo.find_active_by_user(uid)
        assert result is not None
        assert result.user_id == uid
        assert result.instructor_id == iid
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_find_active_by_user_returns_none(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorAssignmentRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyInstructorAssignmentRepository(session)
        result = await repo.find_active_by_user(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_count_active_by_instructor_returns_int(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorAssignmentRepository
        session = _make_session()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 5
        session.execute.return_value = result_mock
        repo = SQLAlchemyInstructorAssignmentRepository(session)
        count = await repo.count_active_by_instructor(uuid4())
        assert count == 5

    @pytest.mark.asyncio
    async def test_deactivate_active_for_user_executes_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorAssignmentRepository
        session = _make_session()
        repo = SQLAlchemyInstructorAssignmentRepository(session)
        await repo.deactivate_active_for_user(uuid4())
        session.execute.assert_awaited_once()
        session.commit.assert_awaited_once()


class TestSQLAlchemyInstructorRatingRepository:
    @pytest.mark.asyncio
    async def test_save_rating_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRatingRepository
        from src.domain.entities.instructor import InstructorRating
        session = _make_session()
        repo = SQLAlchemyInstructorRatingRepository(session)
        rating = InstructorRating(
            id=uuid4(), user_id=uuid4(), instructor_id=uuid4(),
            rating=4.5, created_at=datetime.utcnow(), comment="Excellent!"
        )
        result = await repo.save(rating)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is rating

    @pytest.mark.asyncio
    async def test_save_rating_without_comment(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRatingRepository
        from src.domain.entities.instructor import InstructorRating
        session = _make_session()
        repo = SQLAlchemyInstructorRatingRepository(session)
        rating = InstructorRating(
            id=uuid4(), user_id=uuid4(), instructor_id=uuid4(),
            rating=3.0, created_at=datetime.utcnow(), comment=None
        )
        result = await repo.save(rating)
        assert result is rating

    @pytest.mark.asyncio
    async def test_get_average_rating_returns_float(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRatingRepository
        session = _make_session()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 4.333333
        session.execute.return_value = result_mock
        repo = SQLAlchemyInstructorRatingRepository(session)
        avg = await repo.get_average_rating(uuid4())
        assert avg == 4.33

    @pytest.mark.asyncio
    async def test_get_average_rating_returns_none_when_no_ratings(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRatingRepository
        session = _make_session()
        result_mock = MagicMock()
        result_mock.scalar.return_value = None
        session.execute.return_value = result_mock
        repo = SQLAlchemyInstructorRatingRepository(session)
        avg = await repo.get_average_rating(uuid4())
        assert avg is None


class TestSQLAlchemyInstructorUpdateRating:
    @pytest.mark.asyncio
    async def test_update_rating_avg_executes_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRepository
        session = _make_session()
        repo = SQLAlchemyInstructorRepository(session)
        await repo.update_rating_avg(uuid4(), 4.7)
        session.execute.assert_awaited_once()
        session.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# SQLAlchemyAuditRepository — get_logs_by_user_id
# ---------------------------------------------------------------------------

class TestSQLAlchemyAuditRepositoryFull:
    @pytest.mark.asyncio
    async def test_get_logs_by_user_id_returns_list(self):
        from src.infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
        from src.domain.entities.audit import ProfileAuditLog

        uid = uuid4()
        m1 = MagicMock()
        m1.id = str(uuid4())
        m1.user_id = str(uid)
        m1.changed_by = str(uuid4())
        m1.changes = {"full_name": {"old": "A", "new": "B"}}
        m1.timestamp = datetime.utcnow()

        m2 = MagicMock()
        m2.id = str(uuid4())
        m2.user_id = str(uid)
        m2.changed_by = str(uuid4())
        m2.changes = {}
        m2.timestamp = datetime.utcnow()

        session = _make_session()
        session.execute.return_value = _result_with_scalars([m1, m2])
        repo = SQLAlchemyAuditRepository(session)
        logs = await repo.get_logs_by_user_id(uid)
        assert len(logs) == 2
        assert isinstance(logs[0], ProfileAuditLog)
        assert logs[0].user_id == uid

    @pytest.mark.asyncio
    async def test_get_logs_by_user_id_returns_empty_list(self):
        from src.infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
        session = _make_session()
        session.execute.return_value = _result_with_scalars([])
        repo = SQLAlchemyAuditRepository(session)
        logs = await repo.get_logs_by_user_id(uuid4())
        assert logs == []


# ---------------------------------------------------------------------------
# SQLAlchemyPasswordHistoryRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyPasswordHistoryRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_password_history_repository import SQLAlchemyPasswordHistoryRepository
        from src.domain.entities.password_history import PasswordHistory
        session = _make_session()
        repo = SQLAlchemyPasswordHistoryRepository(session)
        history = PasswordHistory(
            id=uuid4(), user_id=uuid4(),
            password_hash="$2b$12$somehash", changed_at=datetime.utcnow()
        )
        await repo.save(history)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_last_n_hashes_returns_list(self):
        from src.infrastructure.repositories.sqlalchemy_password_history_repository import SQLAlchemyPasswordHistoryRepository
        uid = uuid4()
        row1, row2 = MagicMock(), MagicMock()
        row1.password_hash = "hash1"
        row2.password_hash = "hash2"
        session = _make_session()
        session.execute.return_value = _result_with_scalars([row1, row2])
        repo = SQLAlchemyPasswordHistoryRepository(session)
        hashes = await repo.get_last_n_hashes(uid, n=5)
        assert hashes == ["hash1", "hash2"]

    @pytest.mark.asyncio
    async def test_get_last_n_hashes_returns_empty(self):
        from src.infrastructure.repositories.sqlalchemy_password_history_repository import SQLAlchemyPasswordHistoryRepository
        session = _make_session()
        session.execute.return_value = _result_with_scalars([])
        repo = SQLAlchemyPasswordHistoryRepository(session)
        hashes = await repo.get_last_n_hashes(uuid4())
        assert hashes == []

    @pytest.mark.asyncio
    async def test_delete_old_entries_executes_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_password_history_repository import SQLAlchemyPasswordHistoryRepository
        uid = uuid4()
        result_mock = MagicMock()
        result_mock.fetchall.return_value = [("id1",), ("id2",)]
        session = _make_session()
        session.execute.return_value = result_mock
        repo = SQLAlchemyPasswordHistoryRepository(session)
        await repo.delete_old_entries(uid, keep=5)
        assert session.execute.await_count >= 2
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_old_entries_with_no_existing_records(self):
        from src.infrastructure.repositories.sqlalchemy_password_history_repository import SQLAlchemyPasswordHistoryRepository
        uid = uuid4()
        result_mock = MagicMock()
        result_mock.fetchall.return_value = []
        session = _make_session()
        session.execute.return_value = result_mock
        repo = SQLAlchemyPasswordHistoryRepository(session)
        await repo.delete_old_entries(uid, keep=5)
        session.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# SQLAlchemyPasswordResetTokenRepository
# ---------------------------------------------------------------------------

class TestSQLAlchemyPasswordResetTokenRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_password_reset_token_repository import SQLAlchemyPasswordResetTokenRepository
        from src.domain.entities.password_reset_token import PasswordResetToken, ResetTokenStatus
        from datetime import timedelta
        session = _make_session()
        repo = SQLAlchemyPasswordResetTokenRepository(session)
        token = PasswordResetToken(
            id=uuid4(), user_id=uuid4(), token="abc123",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            status=ResetTokenStatus.PENDING,
            created_at=datetime.utcnow(), used_at=None
        )
        await repo.save(token)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_find_by_token_returns_token_when_valid(self):
        from src.infrastructure.repositories.sqlalchemy_password_reset_token_repository import SQLAlchemyPasswordResetTokenRepository
        from src.domain.entities.password_reset_token import ResetTokenStatus
        from datetime import timedelta
        uid = uuid4()
        row = MagicMock()
        row.id = str(uuid4())
        row.user_id = str(uid)
        row.token = "valid_token"
        row.expires_at = datetime.utcnow() + timedelta(hours=1)
        row.status = ResetTokenStatus.PENDING
        row.created_at = datetime.utcnow()
        row.used_at = None
        session = _make_session()
        session.execute.return_value = _result_with(row)
        repo = SQLAlchemyPasswordResetTokenRepository(session)
        result = await repo.find_by_token("valid_token")
        assert result is not None
        assert result.token == "valid_token"
        assert result.user_id == uid

    @pytest.mark.asyncio
    async def test_find_by_token_returns_none_when_not_found(self):
        from src.infrastructure.repositories.sqlalchemy_password_reset_token_repository import SQLAlchemyPasswordResetTokenRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyPasswordResetTokenRepository(session)
        result = await repo.find_by_token("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_token_returns_none_when_expired(self):
        from src.infrastructure.repositories.sqlalchemy_password_reset_token_repository import SQLAlchemyPasswordResetTokenRepository
        from src.domain.entities.password_reset_token import ResetTokenStatus
        from datetime import timedelta
        row = MagicMock()
        row.id = str(uuid4())
        row.user_id = str(uuid4())
        row.token = "expired"
        row.expires_at = datetime.utcnow() - timedelta(hours=2)
        row.status = ResetTokenStatus.PENDING
        row.created_at = datetime.utcnow() - timedelta(hours=3)
        row.used_at = None
        session = _make_session()
        session.execute.return_value = _result_with(row)
        repo = SQLAlchemyPasswordResetTokenRepository(session)
        result = await repo.find_by_token("expired")
        assert result is None

    @pytest.mark.asyncio
    async def test_mark_as_used_executes_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_password_reset_token_repository import SQLAlchemyPasswordResetTokenRepository
        session = _make_session()
        repo = SQLAlchemyPasswordResetTokenRepository(session)
        await repo.mark_as_used(uuid4())
        session.execute.assert_awaited_once()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_expired_tokens_executes_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_password_reset_token_repository import SQLAlchemyPasswordResetTokenRepository
        session = _make_session()
        repo = SQLAlchemyPasswordResetTokenRepository(session)
        await repo.delete_expired_tokens(uuid4())
        session.execute.assert_awaited_once()
        session.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# SQLAlchemyMessageRepository
# ---------------------------------------------------------------------------

def _mock_message_model(msg_id=None, sender_id=None, recipient_id=None):
    m = MagicMock()
    m.id = str(msg_id or uuid4())
    m.sender_id = str(sender_id or uuid4())
    m.recipient_id = str(recipient_id or uuid4())
    m.subject = "Hello"
    m.content = "Test message content"
    m.message_type = "INSTRUCTOR_MESSAGE"
    m.is_read = False
    m.created_at = datetime.utcnow()
    m.read_at = None
    return m


class TestSQLAlchemyMessageRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        from src.domain.entities.message import Message, MessageType
        session = _make_session()
        repo = SQLAlchemyMessageRepository(session)
        msg = Message(
            id=uuid4(), sender_id=uuid4(), recipient_id=uuid4(),
            content="Hello there", message_type=MessageType.INSTRUCTOR_MESSAGE,
            is_read=False, created_at=datetime.utcnow()
        )
        result = await repo.save(msg)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is msg

    @pytest.mark.asyncio
    async def test_find_by_id_returns_message_when_found(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        mid = uuid4()
        model = _mock_message_model(msg_id=mid)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyMessageRepository(session)
        result = await repo.find_by_id(mid)
        assert result is not None
        assert result.content == "Test message content"

    @pytest.mark.asyncio
    async def test_find_by_id_returns_none_when_not_found(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyMessageRepository(session)
        result = await repo.find_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_recipient_returns_list(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        rid = uuid4()
        models = [_mock_message_model(recipient_id=rid), _mock_message_model(recipient_id=rid)]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(models)
        repo = SQLAlchemyMessageRepository(session)
        result = await repo.get_by_recipient(rid)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_by_recipient_empty(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        session = _make_session()
        session.execute.return_value = _result_with_scalars([])
        repo = SQLAlchemyMessageRepository(session)
        result = await repo.get_by_recipient(uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_sender_and_recipient_returns_list(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        sid, rid = uuid4(), uuid4()
        models = [_mock_message_model(sender_id=sid, recipient_id=rid)]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(models)
        repo = SQLAlchemyMessageRepository(session)
        result = await repo.get_by_sender_and_recipient(sid, rid)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_mark_as_read_updates_model_when_found(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        model = _mock_message_model()
        model.is_read = False
        model.read_at = None
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyMessageRepository(session)
        await repo.mark_as_read(uuid4())
        assert model.is_read is True
        assert model.read_at is not None
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_mark_as_read_does_nothing_when_not_found(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyMessageRepository(session)
        await repo.mark_as_read(uuid4())
        session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_count_unread_by_recipient_returns_count(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        rid = uuid4()
        unread = [_mock_message_model(recipient_id=rid), _mock_message_model(recipient_id=rid)]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(unread)
        repo = SQLAlchemyMessageRepository(session)
        count = await repo.count_unread_by_recipient(rid)
        assert count == 2

    @pytest.mark.asyncio
    async def test_count_unread_by_recipient_returns_zero(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        session = _make_session()
        session.execute.return_value = _result_with_scalars([])
        repo = SQLAlchemyMessageRepository(session)
        count = await repo.count_unread_by_recipient(uuid4())
        assert count == 0

    @pytest.mark.asyncio
    async def test_map_to_entity_includes_read_at(self):
        from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
        model = _mock_message_model()
        model.read_at = datetime.utcnow()
        model.is_read = True
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyMessageRepository(session)
        result = await repo.find_by_id(uuid4())
        assert result.is_read is True
        assert result.read_at is not None


# ---------------------------------------------------------------------------
# SQLAlchemyReminderRepository
# ---------------------------------------------------------------------------

def _mock_reminder_model(rid=None, user_id=None):
    m = MagicMock()
    m.id = str(rid or uuid4())
    m.user_id = str(user_id or uuid4())
    m.reminder_type = "TRAINING"
    m.title = "Go to gym"
    m.description = "Don't skip leg day"
    m.scheduled_time = "07:00"
    m.timezone = "America/Bogota"
    m.frequency = "DAILY"
    m.is_active = True
    m.last_sent_at = None
    m.created_at = datetime.utcnow()
    m.updated_at = None
    return m


class TestSQLAlchemyReminderRepository:
    @pytest.mark.asyncio
    async def test_save_adds_and_commits(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        from src.domain.entities.reminder import Reminder, ReminderType, ReminderFrequency
        session = _make_session()
        repo = SQLAlchemyReminderRepository(session)
        reminder = Reminder(
            id=uuid4(), user_id=uuid4(),
            reminder_type=ReminderType.TRAINING,
            title="Morning run", scheduled_time="06:30",
            timezone="America/Bogota", frequency=ReminderFrequency.DAILY,
            is_active=True, created_at=datetime.utcnow()
        )
        result = await repo.save(reminder)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        assert result is reminder

    @pytest.mark.asyncio
    async def test_find_by_id_returns_reminder_when_found(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        rid = uuid4()
        model = _mock_reminder_model(rid=rid)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyReminderRepository(session)
        result = await repo.find_by_id(rid)
        assert result is not None
        assert result.title == "Go to gym"

    @pytest.mark.asyncio
    async def test_find_by_id_returns_none_when_not_found(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyReminderRepository(session)
        result = await repo.find_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_returns_list(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        uid = uuid4()
        models = [_mock_reminder_model(user_id=uid), _mock_reminder_model(user_id=uid)]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(models)
        repo = SQLAlchemyReminderRepository(session)
        result = await repo.get_by_user(uid)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_by_user_empty(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        session = _make_session()
        session.execute.return_value = _result_with_scalars([])
        repo = SQLAlchemyReminderRepository(session)
        result = await repo.get_by_user(uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_update_modifies_model_when_found(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        from src.domain.entities.reminder import Reminder, ReminderType, ReminderFrequency
        rid = uuid4()
        model = _mock_reminder_model(rid=rid)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyReminderRepository(session)
        reminder = Reminder(
            id=rid, user_id=uuid4(),
            reminder_type=ReminderType.PHYSICAL_RECORD,
            title="Updated title", scheduled_time="08:00",
            timezone="America/Bogota", frequency=ReminderFrequency.WEEKLY,
            is_active=False, created_at=datetime.utcnow()
        )
        result = await repo.update(reminder)
        assert model.title == "Updated title"
        assert model.is_active is False
        session.commit.assert_awaited_once()
        assert result is reminder

    @pytest.mark.asyncio
    async def test_update_does_nothing_when_not_found(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        from src.domain.entities.reminder import Reminder, ReminderType, ReminderFrequency
        session = _make_session()
        session.execute.return_value = _result_with(None)
        repo = SQLAlchemyReminderRepository(session)
        reminder = Reminder(
            id=uuid4(), user_id=uuid4(),
            reminder_type=ReminderType.TRAINING,
            title="Ghost", scheduled_time="09:00",
            timezone="UTC", frequency=ReminderFrequency.ONCE,
            is_active=True, created_at=datetime.utcnow()
        )
        result = await repo.update(reminder)
        session.commit.assert_not_awaited()
        assert result is reminder

    @pytest.mark.asyncio
    async def test_delete_removes_model_when_found(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        rid = uuid4()
        model = _mock_reminder_model(rid=rid)
        session = _make_session()
        session.execute.return_value = _result_with(model)
        session.delete = AsyncMock()
        repo = SQLAlchemyReminderRepository(session)
        await repo.delete(rid)
        session.delete.assert_awaited_once_with(model)
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_does_nothing_when_not_found(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        session = _make_session()
        session.execute.return_value = _result_with(None)
        session.delete = AsyncMock()
        repo = SQLAlchemyReminderRepository(session)
        await repo.delete(uuid4())
        session.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_active_by_user_returns_active_reminders(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        uid = uuid4()
        models = [_mock_reminder_model(user_id=uid)]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(models)
        repo = SQLAlchemyReminderRepository(session)
        result = await repo.get_active_by_user(uid)
        assert len(result) == 1
        assert result[0].is_active is True

    @pytest.mark.asyncio
    async def test_get_due_reminders_returns_all_active(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        models = [_mock_reminder_model(), _mock_reminder_model()]
        session = _make_session()
        session.execute.return_value = _result_with_scalars(models)
        repo = SQLAlchemyReminderRepository(session)
        result = await repo.get_due_reminders()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_map_to_entity_with_optional_fields(self):
        from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
        model = _mock_reminder_model()
        model.description = None
        model.last_sent_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()
        session = _make_session()
        session.execute.return_value = _result_with(model)
        repo = SQLAlchemyReminderRepository(session)
        result = await repo.find_by_id(uuid4())
        assert result.description is None
        assert result.last_sent_at is not None
