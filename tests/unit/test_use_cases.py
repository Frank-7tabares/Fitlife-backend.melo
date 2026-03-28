"""
Tests unitarios — Use Cases. Repositorios mockeados (AsyncMock).
Reutiliza helpers y parametrización para minimizar código.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime

from tests.unit.helpers import make_user


# ----- Fixtures compartidos por clase -----

@pytest.fixture
def user_repo():
    return AsyncMock()

@pytest.fixture
def refresh_repo():
    m = AsyncMock()
    m.save.return_value = None
    return m

@pytest.fixture
def audit_repo():
    return AsyncMock()


# ----- RegisterUser -----

class TestRegisterUser:
    @pytest.fixture
    def repo(self):
        m = AsyncMock()
        m.exists_by_email.return_value = False
        m.save.return_value = None
        return m

    @pytest.mark.asyncio
    async def test_register_success_returns_tokens(self, repo, refresh_repo):
        from src.application.use_cases.register_user import RegisterUser
        from src.application.dtos.auth_dtos import RegisterUserRequest
        uc = RegisterUser(repo, refresh_repo)
        req = RegisterUserRequest(email="new@example.com", password="Pass1234!", full_name="Nuevo")
        result = await uc.execute(req)
        assert result.email == "new@example.com" and result.full_name == "Nuevo"
        assert result.access_token and result.refresh_token and result.token_type == "bearer"
        repo.save.assert_awaited_once()
        refresh_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises(self, repo, refresh_repo):
        from src.application.use_cases.register_user import RegisterUser
        from src.application.dtos.auth_dtos import RegisterUserRequest
        from src.application.exceptions import EmailAlreadyRegisteredError
        repo.exists_by_email.return_value = True
        uc = RegisterUser(repo, refresh_repo)
        with pytest.raises(EmailAlreadyRegisteredError, match="already registered"):
            await uc.execute(RegisterUserRequest(email="dup@example.com", password="Pass1234!"))
        repo.save.assert_not_awaited()
        refresh_repo.save.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("email,password,full_name,expected_full_name,expected_role", [
        ("noname@example.com", "Secret99!", None, None, "USER"),
        ("x@x.com", "Abcde123!", "Name", "Name", "USER"),
    ])
    async def test_register_optional_fields_and_role(self, repo, refresh_repo, email, password, full_name, expected_full_name, expected_role):
        from src.application.use_cases.register_user import RegisterUser
        from src.application.dtos.auth_dtos import RegisterUserRequest
        from src.domain.entities.user import UserRole
        uc = RegisterUser(repo, refresh_repo)
        result = await uc.execute(RegisterUserRequest(email=email, password=password, full_name=full_name))
        assert result.full_name == expected_full_name and result.role == UserRole.USER
        assert result.access_token

    @pytest.mark.asyncio
    async def test_register_generates_unique_ids(self, repo, refresh_repo):
        from src.application.use_cases.register_user import RegisterUser
        from src.application.dtos.auth_dtos import RegisterUserRequest
        uc = RegisterUser(repo, refresh_repo)
        r1 = await uc.execute(RegisterUserRequest(email="a@x.com", password="Abc123!"))
        repo.exists_by_email.return_value = False
        r2 = await uc.execute(RegisterUserRequest(email="b@x.com", password="Abc123!"))
        assert r1.id != r2.id


# ----- LoginUser -----

class TestLoginUser:
    @pytest.mark.asyncio
    async def test_login_success_returns_tokens(self, user_repo, refresh_repo):
        from src.application.use_cases.login_user import LoginUser
        from src.application.dtos.auth_dtos import LoginUserRequest
        from src.infrastructure.security.password_hasher import PasswordHasher
        user = make_user()
        user.password_hash = PasswordHasher.hash("correct_pass")
        user_repo.find_by_email.return_value = user
        uc = LoginUser(user_repo, refresh_repo)
        result = await uc.execute(LoginUserRequest(email="user@example.com", password="correct_pass"))
        assert result.access_token and result.refresh_token and result.token_type == "bearer"
        refresh_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("find_by_email_val,password,match_msg", [
        (None, "any_pass", "Invalid credentials"),
        ("wrong_pass", "wrong_pass", "Invalid credentials"),
        ("inactive", "pass123", "inactive"),
    ])
    async def test_login_failures_raise(self, user_repo, refresh_repo, find_by_email_val, password, match_msg):
        from src.application.use_cases.login_user import LoginUser
        from src.application.dtos.auth_dtos import LoginUserRequest
        from src.infrastructure.security.password_hasher import PasswordHasher
        if find_by_email_val is None:
            user_repo.find_by_email.return_value = None
        else:
            user = make_user(is_active=(find_by_email_val != "inactive"))
            user.password_hash = PasswordHasher.hash("pass123" if find_by_email_val == "inactive" else "correct_pass")
            user_repo.find_by_email.return_value = user
        uc = LoginUser(user_repo, refresh_repo)
        req = LoginUserRequest(email="u@e.com", password=password)
        with pytest.raises(ValueError, match=match_msg):
            await uc.execute(req)
        refresh_repo.save.assert_not_awaited()


# ----- RefreshToken -----

class TestRefreshToken:
    @pytest.mark.asyncio
    async def test_refresh_success_returns_tokens(self, user_repo, refresh_repo):
        from src.application.use_cases.refresh_token import RefreshToken
        from src.application.dtos.auth_dtos import RefreshTokenRequest
        user = make_user()
        user_repo.find_by_id.return_value = user
        refresh_repo.find_valid_user_id.return_value = user.id
        refresh_repo.revoke.return_value = None
        refresh_repo.save.return_value = None
        uc = RefreshToken(user_repo, refresh_repo)
        result = await uc.execute(RefreshTokenRequest(refresh_token="valid.jwt.token"))
        assert result.access_token and result.refresh_token
        refresh_repo.revoke.assert_awaited_once_with("valid.jwt.token")
        refresh_repo.save.assert_awaited_once()

class TestRefreshTokenFailures:
    @pytest.mark.asyncio
    async def test_refresh_invalid_token_raises(self, user_repo, refresh_repo):
        from src.application.use_cases.refresh_token import RefreshToken
        from src.application.dtos.auth_dtos import RefreshTokenRequest
        refresh_repo.find_valid_user_id.return_value = None
        with pytest.raises(ValueError, match="Invalid or expired"):
            await RefreshToken(user_repo, refresh_repo).execute(RefreshTokenRequest(refresh_token="invalid"))
        refresh_repo.revoke.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_refresh_user_inactive_raises(self, user_repo, refresh_repo):
        from src.application.use_cases.refresh_token import RefreshToken
        from src.application.dtos.auth_dtos import RefreshTokenRequest
        user = make_user(is_active=False)
        user_repo.find_by_id.return_value = user
        refresh_repo.find_valid_user_id.return_value = user.id
        with pytest.raises(ValueError, match="inactive"):
            await RefreshToken(user_repo, refresh_repo).execute(RefreshTokenRequest(refresh_token="t"))

    @pytest.mark.asyncio
    async def test_refresh_user_not_found_raises(self, user_repo, refresh_repo):
        from src.application.use_cases.refresh_token import RefreshToken
        from src.application.dtos.auth_dtos import RefreshTokenRequest
        refresh_repo.find_valid_user_id.return_value = uuid4()
        user_repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            await RefreshToken(user_repo, refresh_repo).execute(RefreshTokenRequest(refresh_token="t"))


# ----- UpdateProfile -----

class TestUpdateProfile:
    @pytest.mark.asyncio
    async def test_update_full_name_success(self, user_repo, audit_repo):
        from src.application.use_cases.update_profile import UpdateProfile
        from src.application.dtos.user_dtos import UpdateProfileRequest
        user = make_user(full_name="Old Name", version=1)
        updated = make_user(full_name="New Name", version=2)
        user_repo.find_by_id.return_value = user
        user_repo.update.return_value = updated
        audit_repo.save_log.return_value = None
        result = await UpdateProfile(user_repo, audit_repo).execute(user.id, user.id, UpdateProfileRequest(full_name="New Name", version=1))
        assert result.full_name == "New Name"
        user_repo.update.assert_awaited_once()
        audit_repo.save_log.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("full_name_req,version,expected_name,expect_update", [
        ("Same Name", 1, "Same Name", False),
        (None, 1, "Existing", False),
    ])
    async def test_update_no_change_does_not_call_update(self, user_repo, audit_repo, full_name_req, version, expected_name, expect_update):
        from src.application.use_cases.update_profile import UpdateProfile
        from src.application.dtos.user_dtos import UpdateProfileRequest
        user = make_user(full_name=expected_name, version=version)
        user_repo.find_by_id.return_value = user
        uc = UpdateProfile(user_repo, audit_repo)
        result = await uc.execute(user.id, user.id, UpdateProfileRequest(full_name=full_name_req, version=version))
        assert result.full_name == expected_name
        assert user_repo.update.await_count == (1 if expect_update else 0)

    @pytest.mark.asyncio
    async def test_update_user_not_found_raises(self, user_repo, audit_repo):
        from src.application.use_cases.update_profile import UpdateProfile
        from src.application.dtos.user_dtos import UpdateProfileRequest
        user_repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            await UpdateProfile(user_repo, audit_repo).execute(uuid4(), uuid4(), UpdateProfileRequest(full_name="N", version=1))


# ----- SubmitAssessment -----

class TestSubmitAssessment:
    @pytest.fixture
    def repo(self):
        m = AsyncMock()
        m.save.return_value = None
        return m

    @pytest.fixture
    def user_repo(self):
        m = AsyncMock()
        m.find_by_id.return_value = make_user()
        return m

    @pytest.mark.asyncio
    async def test_submit_returns_assessment_response(self, repo, user_repo):
        from src.application.use_cases.submit_assessment import SubmitAssessment
        from src.application.dtos.assessment_dtos import SubmitAssessmentRequest
        uc = SubmitAssessment(repo, user_repo)
        req = SubmitAssessmentRequest(user_id=uuid4(), real_age=30, responses={"q1": 8, "q2": 7})
        result = await uc.execute(req)
        assert result.fitness_score >= 0 and result.category and result.body_age and result.comparison
        repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("responses,real_age,expected_score,expected_category", [
        ({}, 25, 0.0, "POOR"),
        ({f"q{i}": 10 for i in range(5)}, 30, None, "EXCELLENT"),
    ])
    async def test_submit_responses_category(self, repo, user_repo, responses, real_age, expected_score, expected_category):
        from src.application.use_cases.submit_assessment import SubmitAssessment
        from src.application.dtos.assessment_dtos import SubmitAssessmentRequest
        from src.domain.entities.assessment import AssessmentCategory
        result = await SubmitAssessment(repo, user_repo).execute(SubmitAssessmentRequest(user_id=uuid4(), real_age=real_age, responses=responses))
        if expected_score is not None:
            assert result.fitness_score == expected_score
        assert result.category == getattr(AssessmentCategory, expected_category)

    @pytest.mark.asyncio
    async def test_submit_persists_responses_and_unique_id(self, repo, user_repo):
        from src.application.use_cases.submit_assessment import SubmitAssessment
        from src.application.dtos.assessment_dtos import SubmitAssessmentRequest
        uc = SubmitAssessment(repo, user_repo)
        responses = {"pushups": 5, "run": 3}
        req = SubmitAssessmentRequest(user_id=uuid4(), real_age=28, responses=responses)
        result = await uc.execute(req)
        assert result.responses == responses
        r2 = await uc.execute(SubmitAssessmentRequest(user_id=req.user_id, real_age=28, responses=responses))
        assert result.id != r2.id

    @pytest.mark.asyncio
    async def test_submit_user_not_found_raises(self, repo, user_repo):
        from src.application.use_cases.submit_assessment import SubmitAssessment
        from src.application.dtos.assessment_dtos import SubmitAssessmentRequest
        from src.domain.exceptions.user_exceptions import UserNotFoundException
        user_repo.find_by_id.return_value = None
        uc = SubmitAssessment(repo, user_repo)
        req = SubmitAssessmentRequest(user_id=uuid4(), real_age=30, responses={})
        with pytest.raises(UserNotFoundException, match="Usuario no encontrado"):
            await uc.execute(req)
        repo.save.assert_not_awaited()


# ----- GetAssessmentHistory -----

class TestGetAssessmentHistory:
    @pytest.fixture
    def repo(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_history(self, repo):
        from src.application.use_cases.get_assessment_history import GetAssessmentHistory
        repo.find_by_user_id.return_value = []
        assert await GetAssessmentHistory(repo).execute(uuid4()) == []

    @pytest.mark.asyncio
    async def test_returns_mapped_with_disclaimer(self, repo):
        from src.application.use_cases.get_assessment_history import GetAssessmentHistory
        from src.domain.entities.assessment import Assessment, AssessmentCategory, BodyAgeComparison
        from src.application.dtos.assessment_dtos import BODY_AGE_DISCLAIMER
        uid = uuid4()
        repo.find_by_user_id.return_value = [
            Assessment(id=uuid4(), user_id=uid, fitness_score=75.0, category=AssessmentCategory.GOOD,
                       body_age=28.0, comparison=BodyAgeComparison.BODY_YOUNGER, responses={"q": 7}, created_at=datetime.utcnow()),
            Assessment(id=uuid4(), user_id=uid, fitness_score=40.0, category=AssessmentCategory.POOR,
                       body_age=35.0, comparison=BodyAgeComparison.BODY_OLDER, responses={"q": 3}, created_at=datetime.utcnow()),
        ]
        result = await GetAssessmentHistory(repo).execute(uid)
        assert len(result) == 2 and result[0].fitness_score == 75.0 and result[1].fitness_score == 40.0
        assert result[0].body_age_disclaimer == BODY_AGE_DISCLAIMER

    @pytest.mark.asyncio
    async def test_calls_repo_with_user_id(self, repo):
        from src.application.use_cases.get_assessment_history import GetAssessmentHistory
        repo.find_by_user_id.return_value = []
        uid = uuid4()
        await GetAssessmentHistory(repo).execute(uid)
        repo.find_by_user_id.assert_awaited_once_with(uid)


# ----- PhysicalRecordUseCases -----

class TestPhysicalRecordUseCases:
    @pytest.fixture
    def repo(self):
        m = AsyncMock()
        m.save.return_value = None
        m.find_by_user_id.return_value = []
        return m

    @pytest.mark.asyncio
    @pytest.mark.parametrize("weight,height,activity", [(70.0, 175.0, "MODERATE"), (73.5, 168.0, "SEDENTARY")])
    async def test_create_record_bmi(self, repo, weight, height, activity):
        from src.application.use_cases.physical_record_use_cases import PhysicalRecordUseCases
        from src.application.dtos.physical_record_dtos import PhysicalRecordRequest
        result = await PhysicalRecordUseCases(repo).create_record(uuid4(), PhysicalRecordRequest(weight=weight, height=height, activity_level=activity))
        assert result.bmi == round(weight / (height / 100) ** 2, 2)
        assert result.weight == weight and result.height == height
        repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_record_optional_fields(self, repo):
        from src.application.use_cases.physical_record_use_cases import PhysicalRecordUseCases
        from src.application.dtos.physical_record_dtos import PhysicalRecordRequest
        req = PhysicalRecordRequest(weight=80.0, height=180.0, body_fat_percentage=20.0, waist=85.0, hip=95.0, activity_level="ACTIVE")
        result = await PhysicalRecordUseCases(repo).create_record(uuid4(), req)
        assert result.body_fat_percentage == 20.0 and result.waist == 85.0 and result.hip == 95.0

    @pytest.mark.asyncio
    async def test_get_history_empty_and_mapped(self, repo):
        from src.application.use_cases.physical_record_use_cases import PhysicalRecordUseCases
        from src.domain.entities.physical_record import ActivityLevel, PhysicalRecord
        uc = PhysicalRecordUseCases(repo)
        assert (await uc.get_history(uuid4())).records == [] and (await uc.get_history(uuid4())).total == 0
        uid = uuid4()
        repo.find_by_user_id.return_value = [
            PhysicalRecord(id=uuid4(), user_id=uid, weight=70.0, height=170.0, body_fat_percentage=None, waist=None, hip=None, activity_level=ActivityLevel.LIGHT, recorded_at=datetime.utcnow())
        ]
        result = await uc.get_history(uid)
        assert result.total == 1 and result.records[0].weight == 70.0


# ----- TrainingUseCases -----

class TestTrainingUseCases:
    @pytest.fixture
    def routine_repo(self):
        return AsyncMock()

    @pytest.fixture
    def assignment_repo(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_create_routine_returns_response(self, routine_repo, assignment_repo):
        from src.application.use_cases.training_use_cases import TrainingUseCases
        from src.application.dtos.training_dtos import CreateRoutineRequest, RoutineExerciseDTO
        from src.domain.entities.training import FitnessLevel
        routine_repo.save_routine.return_value = None
        req = CreateRoutineRequest(name="Upper Body", description="Chest and back", goal="HYPERTROPHY", level=FitnessLevel.INTERMEDIATE,
                                   exercises=[RoutineExerciseDTO(exercise_id=uuid4(), sets=3, reps=10, rest_seconds=60)], creator_id=uuid4())
        result = await TrainingUseCases(routine_repo, assignment_repo).create_routine(req)
        assert result.name == "Upper Body" and len(result.exercises) == 1
        routine_repo.save_routine.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_assign_routine_returns_true(self, routine_repo, assignment_repo):
        from src.application.use_cases.training_use_cases import TrainingUseCases
        from src.application.dtos.training_dtos import AssignRoutineRequest
        assignment_repo.save_assignment.return_value = None
        result = await TrainingUseCases(routine_repo, assignment_repo).assign_routine(uuid4(), AssignRoutineRequest(routine_id=uuid4()))
        assert result is True
        assignment_repo.save_assignment.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_active_routine_none_or_routine(self, routine_repo, assignment_repo):
        from src.application.use_cases.training_use_cases import TrainingUseCases
        from src.domain.entities.training import RoutineAssignment, Routine, FitnessLevel
        uc = TrainingUseCases(routine_repo, assignment_repo)
        assignment_repo.find_active_assignment.return_value = None
        assert await uc.get_active_routine(uuid4()) is None
        rid, uid = uuid4(), uuid4()
        assignment_repo.find_active_assignment.return_value = RoutineAssignment(user_id=uid, routine_id=rid, assigned_at=datetime.utcnow(), is_active=True)
        routine_repo.find_routine_by_id.return_value = Routine(id=rid, name="Full Body", description="All muscles", goal="STRENGTH", level=FitnessLevel.BEGINNER, exercises=[], creator_id=uuid4())
        result = await uc.get_active_routine(uid)
        assert result is not None and result.name == "Full Body"

    @pytest.mark.asyncio
    async def test_get_active_routine_not_found_returns_none(self, routine_repo, assignment_repo):
        from src.application.use_cases.training_use_cases import TrainingUseCases
        from src.domain.entities.training import RoutineAssignment
        assignment = RoutineAssignment(user_id=uuid4(), routine_id=uuid4(), assigned_at=datetime.utcnow(), is_active=True)
        assignment_repo.find_active_assignment.return_value = assignment
        routine_repo.find_routine_by_id.return_value = None
        assert await TrainingUseCases(routine_repo, assignment_repo).get_active_routine(assignment.user_id) is None

    @pytest.mark.asyncio
    async def test_complete_workout_success_and_no_assignment_raises(self, routine_repo, assignment_repo):
        from src.application.use_cases.training_use_cases import TrainingUseCases
        from src.application.dtos.training_dtos import CompleteWorkoutRequest
        from src.domain.entities.training import RoutineAssignment
        uc = TrainingUseCases(routine_repo, assignment_repo)
        assignment_repo.find_active_assignment.return_value = None
        with pytest.raises(ValueError, match="No active routine"):
            await uc.complete_workout(uuid4(), CompleteWorkoutRequest(effort_level=5))
        assignment = RoutineAssignment(user_id=uuid4(), routine_id=uuid4(), assigned_at=datetime.utcnow(), is_active=True)
        assignment_repo.find_active_assignment.return_value = assignment
        assignment_repo.save_completion.return_value = None
        assert await uc.complete_workout(assignment.user_id, CompleteWorkoutRequest(effort_level=7, notes="Great")) is True
        assignment_repo.save_completion.assert_awaited_once()


# ----- NutritionUseCases -----

class TestNutritionUseCases:
    @pytest.fixture
    def repo(self):
        m = AsyncMock()
        m.save.return_value = None
        return m

    @pytest.mark.asyncio
    async def test_create_plan_returns_response(self, repo):
        from src.application.use_cases.nutrition_use_cases import NutritionUseCases
        from src.application.dtos.nutrition_dtos import CreateNutritionPlanRequest, DailyPlanDTO, MealDTO
        req = CreateNutritionPlanRequest(name="Cutting Plan", description="Reduce body fat", week_number=10, year=2026,
                                        daily_plans=[DailyPlanDTO(day_of_week=0, meals=[MealDTO(name="Oats", description="Breakfast", calories=300, protein=15.0, carbs=50.0, fats=5.0)])], is_active=True)
        result = await NutritionUseCases(repo).create_plan(uuid4(), req)
        assert result.name == "Cutting Plan" and result.week_number == 10 and result.is_active and len(result.daily_plans) == 1
        repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_plan_optional_macros_and_daily_plans(self, repo):
        from src.application.use_cases.nutrition_use_cases import NutritionUseCases
        from src.application.dtos.nutrition_dtos import CreateNutritionPlanRequest, DailyPlanDTO, MealDTO
        req = CreateNutritionPlanRequest(name="Basic", description="Simple", week_number=1, year=2026,
                                        daily_plans=[DailyPlanDTO(day_of_week=1, meals=[MealDTO(name="Apple", description="Snack")])], is_active=False)
        result = await NutritionUseCases(repo).create_plan(uuid4(), req)
        assert result.daily_plans[0].meals[0].calories is None
        daily_plans = [DailyPlanDTO(day_of_week=i, meals=[MealDTO(name=f"M{i}", description="d")]) for i in range(7)]
        result2 = await NutritionUseCases(repo).create_plan(uuid4(), CreateNutritionPlanRequest(name="Full Week", description="7 days", week_number=20, year=2026, daily_plans=daily_plans))
        assert len(result2.daily_plans) == 7

    @pytest.mark.asyncio
    async def test_get_active_plan_none_and_found(self, repo):
        from src.application.use_cases.nutrition_use_cases import NutritionUseCases
        from src.domain.entities.nutrition import NutritionPlan, DailyPlan, Meal
        uc = NutritionUseCases(repo)
        repo.find_active_by_user_id.return_value = None
        assert await uc.get_active_plan(uuid4()) is None
        uid = uuid4()
        repo.find_active_by_user_id.return_value = NutritionPlan(id=uuid4(), user_id=uid, name="Active Plan", description="Current", week_number=5, year=2026,
                                                                 daily_plans=[DailyPlan(0, [Meal("Rice", "Lunch", 500, 30.0, 80.0, 8.0)])], is_active=True, created_at=datetime.utcnow())
        result = await uc.get_active_plan(uid)
        assert result.name == "Active Plan" and result.is_active


# ----- InstructorUseCases -----

class TestInstructorUseCases:
    @pytest.fixture
    def instructor_repo(self):
        return AsyncMock()

    @pytest.fixture
    def assignment_repo(self):
        return AsyncMock()

    @pytest.fixture
    def rating_repo(self):
        return AsyncMock()

    @pytest.fixture
    def use_cases(self, instructor_repo, assignment_repo, rating_repo):
        from src.application.use_cases.instructor_use_cases import InstructorUseCases
        return InstructorUseCases(instructor_repo, assignment_repo, rating_repo)

    @pytest.mark.asyncio
    async def test_list_instructors_empty_and_with_items(self, use_cases, instructor_repo, assignment_repo):
        from src.infrastructure.database.models.instructor_models import InstructorModel
        instructor_repo.find_all.return_value = []
        assert await use_cases.list_instructors() == []
        mid = uuid4()
        instructor_repo.find_all.return_value = [
            InstructorModel(
                id=str(mid),
                name="Ana",
                certifications=["ACE"],
                specializations="Fuerza",
                rating_avg=4.5,
                certificate_status="verified",
            )
        ]
        assignment_repo.count_active_by_instructor.return_value = 3
        result = await use_cases.list_instructors()
        assert len(result) == 1 and result[0].name == "Ana" and result[0].rating_avg == 4.5 and result[0].active_users_count == 3

    @pytest.mark.asyncio
    async def test_list_instructors_skips_non_verified_by_default(self, use_cases, instructor_repo, assignment_repo):
        from src.infrastructure.database.models.instructor_models import InstructorModel
        v, p = uuid4(), uuid4()
        instructor_repo.find_all.return_value = [
            InstructorModel(id=str(v), name="Veri", certifications=[], specializations="", rating_avg=0.0, certificate_status="verified"),
            InstructorModel(id=str(p), name="Pend", certifications=[], specializations="", rating_avg=0.0, certificate_status="pending"),
        ]
        assignment_repo.count_active_by_instructor.return_value = 0
        out = await use_cases.list_instructors()
        assert len(out) == 1 and out[0].name == "Veri"
        out_all = await use_cases.list_instructors(verified_only=False)
        assert len(out_all) == 2

    @pytest.mark.asyncio
    async def test_get_instructor_by_id_found_and_not_found(self, use_cases, instructor_repo, assignment_repo):
        from src.infrastructure.database.models.instructor_models import InstructorModel
        instructor_repo.find_by_id.return_value = None
        assert await use_cases.get_instructor_by_id(uuid4()) is None
        mid = uuid4()
        instructor_repo.find_by_id.return_value = InstructorModel(id=str(mid), name="Bob", certifications=[], specializations="", rating_avg=0.0)
        assignment_repo.count_active_by_instructor.return_value = 0
        result = await use_cases.get_instructor_by_id(mid)
        assert result.name == "Bob" and result.active_users_count == 0

    @pytest.mark.asyncio
    async def test_assign_instructor_success_and_not_found(self, use_cases, instructor_repo, assignment_repo):
        from src.application.dtos.instructor_dtos import AssignInstructorRequest
        from src.infrastructure.database.models.instructor_models import InstructorModel
        instructor_repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            await use_cases.assign_instructor(uuid4(), AssignInstructorRequest(instructor_id=uuid4()))
        uid, iid = uuid4(), uuid4()
        instructor_repo.find_by_id.return_value = InstructorModel(
            id=str(iid),
            name="Coach",
            certifications=[],
            specializations="",
            rating_avg=0.0,
            certificate_status="verified",
        )
        assignment_repo.deactivate_active_for_user.return_value = None
        assignment_repo.save.return_value = None
        await use_cases.assign_instructor(uid, AssignInstructorRequest(instructor_id=iid))
        assignment_repo.deactivate_active_for_user.assert_awaited_once_with(uid)
        assignment_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_assign_instructor_rejects_not_verified(self, use_cases, instructor_repo, assignment_repo):
        from src.application.dtos.instructor_dtos import AssignInstructorRequest
        from src.infrastructure.database.models.instructor_models import InstructorModel
        uid, iid = uuid4(), uuid4()
        instructor_repo.find_by_id.return_value = InstructorModel(
            id=str(iid),
            name="Coach",
            certifications=[],
            specializations="",
            rating_avg=0.0,
            certificate_status="pending",
        )
        with pytest.raises(ValueError, match="verified"):
            await use_cases.assign_instructor(uid, AssignInstructorRequest(instructor_id=iid))

    @pytest.mark.asyncio
    async def test_rate_instructor_not_found_and_success(self, use_cases, instructor_repo, rating_repo):
        from src.application.dtos.instructor_dtos import RateInstructorRequest
        from src.infrastructure.database.models.instructor_models import InstructorModel
        instructor_repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            await use_cases.rate_instructor(uuid4(), uuid4(), RateInstructorRequest(rating=5))
        uid, iid = uuid4(), uuid4()
        instructor_repo.find_by_id.return_value = InstructorModel(id=str(iid), name="C", certifications=[], specializations="", rating_avg=0.0)
        rating_repo.save.return_value = None
        rating_repo.get_average_rating.return_value = 4.0
        instructor_repo.update_rating_avg.return_value = None
        await use_cases.rate_instructor(uid, iid, RateInstructorRequest(rating=4))
        rating_repo.save.assert_awaited_once()
        instructor_repo.update_rating_avg.assert_awaited_once_with(iid, 4.0)
