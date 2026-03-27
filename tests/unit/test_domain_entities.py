"""
Tests unitarios — Entidades del dominio
Cubre: User, UserRole, PhysicalRecord (bmi), Assessment, enums,
       Training (Routine, RoutineExercise, RoutineAssignment, WorkoutCompletion, FitnessLevel),
       Nutrition (NutritionPlan, DailyPlan, Meal), ProfileAuditLog.
"""
import pytest
from uuid import uuid4
from datetime import datetime


# ---------------------------------------------------------------------------
# User & UserRole
# ---------------------------------------------------------------------------

class TestUserRole:
    @pytest.mark.parametrize("role,value", [("USER", "USER"), ("INSTRUCTOR", "INSTRUCTOR"), ("ADMIN", "ADMIN")])
    def test_user_role_values_and_membership(self, role, value):
        from src.domain.entities.user import UserRole
        r = getattr(UserRole, role)
        assert r == value and UserRole(value) is r
        assert isinstance(r, str)

    def test_user_role_invalid_raises(self):
        from src.domain.entities.user import UserRole
        with pytest.raises(ValueError):
            UserRole("SUPERADMIN")


class TestUserEntity:
    def _make_user(self, **kwargs):
        from src.domain.entities.user import User, UserRole
        defaults = dict(
            id=uuid4(),
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        defaults.update(kwargs)
        return User(**defaults)

    def test_user_creation_defaults(self):
        from src.domain.entities.user import UserRole
        user = self._make_user()
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.full_name is None
        assert user.version == 1
        assert user.updated_at is None

    def test_user_with_full_name(self):
        user = self._make_user(full_name="Ana López")
        assert user.full_name == "Ana López"

    def test_user_with_admin_role(self):
        from src.domain.entities.user import UserRole
        user = self._make_user(role=UserRole.ADMIN)
        assert user.role == UserRole.ADMIN

    def test_user_version_increments_manually(self):
        user = self._make_user()
        user.version += 1
        assert user.version == 2

    def test_user_email_field(self):
        user = self._make_user(email="coach@gym.com")
        assert user.email == "coach@gym.com"

    def test_user_inactive(self):
        user = self._make_user(is_active=False)
        assert user.is_active is False


# ---------------------------------------------------------------------------
# PhysicalRecord — bmi property
# ---------------------------------------------------------------------------

class TestPhysicalRecordBmi:
    def _make_record(self, weight: float, height: float, **kwargs):
        from src.domain.entities.physical_record import ActivityLevel, PhysicalRecord
        defaults = dict(id=uuid4(), user_id=uuid4(), body_fat_percentage=None, waist=None, hip=None,
                        activity_level=ActivityLevel.MODERATE, recorded_at=datetime.utcnow())
        defaults.update(kwargs)
        return PhysicalRecord(weight=weight, height=height, **defaults)

    @pytest.mark.parametrize("weight,height,expected_bmi", [
        (70.0, 175.0, 70.0 / (1.75 ** 2)),
        (80.0, 180.0, 80 / (1.80 ** 2)),
        (75.0, 170.0, 75.0 / (1.70 ** 2)),
    ])
    def test_bmi_formula(self, weight, height, expected_bmi):
        record = self._make_record(weight, height)
        assert record.bmi == pytest.approx(expected_bmi, rel=1e-6)

    @pytest.mark.parametrize("weight,height,predicate", [
        (45.0, 170.0, lambda b: b < 18.5),
        (65.0, 170.0, lambda b: 18.5 <= b < 25.0),
        (90.0, 170.0, lambda b: b >= 25.0),
    ])
    def test_bmi_ranges(self, weight, height, predicate):
        record = self._make_record(weight, height)
        assert predicate(record.bmi)

    def test_bmi_with_optional_fields(self):
        from src.domain.entities.physical_record import ActivityLevel, PhysicalRecord
        record = PhysicalRecord(
            id=uuid4(), user_id=uuid4(), weight=75.0, height=170.0,
            body_fat_percentage=20.5, waist=85.0, hip=95.0,
            activity_level=ActivityLevel.ACTIVE, recorded_at=datetime.utcnow(),
        )
        assert record.bmi == pytest.approx(75.0 / (1.70 ** 2), rel=1e-6)
        assert record.body_fat_percentage == 20.5 and record.waist == 85.0 and record.hip == 95.0


# ---------------------------------------------------------------------------
# Assessment enums & entity
# ---------------------------------------------------------------------------

class TestAssessmentEnums:
    def test_assessment_category_values(self):
        from src.domain.entities.assessment import AssessmentCategory
        assert AssessmentCategory.EXCELLENT == "EXCELLENT"
        assert AssessmentCategory.GOOD == "GOOD"
        assert AssessmentCategory.FAIR == "FAIR"
        assert AssessmentCategory.POOR == "POOR"

    def test_body_age_comparison_values(self):
        from src.domain.entities.assessment import BodyAgeComparison
        assert BodyAgeComparison.BODY_OLDER == "BODY_OLDER"
        assert BodyAgeComparison.BODY_YOUNGER == "BODY_YOUNGER"
        assert BodyAgeComparison.BODY_EQUAL == "BODY_EQUAL"

    def test_assessment_category_is_str(self):
        from src.domain.entities.assessment import AssessmentCategory
        assert isinstance(AssessmentCategory.GOOD, str)


class TestAssessmentEntity:
    def test_assessment_construction(self):
        from src.domain.entities.assessment import Assessment, AssessmentCategory, BodyAgeComparison
        uid = uuid4()
        now = datetime.utcnow()
        a = Assessment(
            id=uid,
            user_id=uuid4(),
            fitness_score=75.0,
            category=AssessmentCategory.GOOD,
            body_age=28.0,
            comparison=BodyAgeComparison.BODY_YOUNGER,
            responses={"q1": 7},
            created_at=now,
        )
        assert a.fitness_score == 75.0
        assert a.category == AssessmentCategory.GOOD
        assert a.body_age == 28.0
        assert a.comparison == BodyAgeComparison.BODY_YOUNGER
        assert a.responses == {"q1": 7}
        assert a.created_at == now


# ---------------------------------------------------------------------------
# Training entities
# ---------------------------------------------------------------------------

class TestFitnessLevel:
    def test_fitness_level_values(self):
        from src.domain.entities.training import FitnessLevel
        assert FitnessLevel.BEGINNER == "BEGINNER"
        assert FitnessLevel.INTERMEDIATE == "INTERMEDIATE"
        assert FitnessLevel.ADVANCED == "ADVANCED"

    def test_fitness_level_is_str(self):
        from src.domain.entities.training import FitnessLevel
        assert isinstance(FitnessLevel.BEGINNER, str)

    def test_fitness_level_invalid_raises(self):
        from src.domain.entities.training import FitnessLevel
        with pytest.raises(ValueError):
            FitnessLevel("EXPERT")


class TestRoutineExerciseEntity:
    def test_routine_exercise_fields(self):
        from src.domain.entities.training import RoutineExercise
        ex = RoutineExercise(exercise_id=uuid4(), sets=3, reps=10, rest_seconds=60)
        assert ex.sets == 3
        assert ex.reps == 10
        assert ex.rest_seconds == 60

    def test_routine_exercise_zero_rest(self):
        from src.domain.entities.training import RoutineExercise
        ex = RoutineExercise(exercise_id=uuid4(), sets=5, reps=5, rest_seconds=0)
        assert ex.rest_seconds == 0


class TestRoutineEntity:
    def test_routine_creation(self):
        from src.domain.entities.training import Routine, RoutineExercise, FitnessLevel
        r = Routine(
            id=uuid4(),
            name="Full Body",
            description="Full body workout",
            goal="STRENGTH",
            level=FitnessLevel.INTERMEDIATE,
            exercises=[RoutineExercise(exercise_id=uuid4(), sets=3, reps=12, rest_seconds=45)],
            creator_id=uuid4(),
        )
        assert r.name == "Full Body"
        assert r.level == FitnessLevel.INTERMEDIATE
        assert len(r.exercises) == 1

    def test_routine_empty_exercises(self):
        from src.domain.entities.training import Routine, FitnessLevel
        r = Routine(
            id=uuid4(), name="Rest", description="Rest day", goal="RECOVERY",
            level=FitnessLevel.BEGINNER, exercises=[], creator_id=uuid4()
        )
        assert r.exercises == []


class TestRoutineAssignmentEntity:
    def test_routine_assignment_fields(self):
        from src.domain.entities.training import RoutineAssignment
        now = datetime.utcnow()
        a = RoutineAssignment(
            user_id=uuid4(), routine_id=uuid4(), assigned_at=now, is_active=True
        )
        assert a.is_active is True
        assert a.assigned_at == now

    def test_routine_assignment_inactive(self):
        from src.domain.entities.training import RoutineAssignment
        a = RoutineAssignment(
            user_id=uuid4(), routine_id=uuid4(), assigned_at=datetime.utcnow(), is_active=False
        )
        assert a.is_active is False


class TestWorkoutCompletionEntity:
    def test_workout_completion_fields(self):
        from src.domain.entities.training import WorkoutCompletion
        now = datetime.utcnow()
        wc = WorkoutCompletion(
            id=uuid4(), user_id=uuid4(), routine_id=uuid4(),
            completed_at=now, effort_level=8, notes="Felt great"
        )
        assert wc.effort_level == 8
        assert wc.notes == "Felt great"
        assert wc.completed_at == now

    def test_workout_completion_no_notes(self):
        from src.domain.entities.training import WorkoutCompletion
        wc = WorkoutCompletion(
            id=uuid4(), user_id=uuid4(), routine_id=uuid4(),
            completed_at=datetime.utcnow(), effort_level=5, notes=None
        )
        assert wc.notes is None


# ---------------------------------------------------------------------------
# Nutrition entities
# ---------------------------------------------------------------------------

class TestMealEntity:
    def test_meal_with_all_fields(self):
        from src.domain.entities.nutrition import Meal
        m = Meal(name="Oatmeal", description="Breakfast", calories=350, protein=12.0, carbs=60.0, fats=5.0)
        assert m.name == "Oatmeal"
        assert m.calories == 350
        assert m.protein == 12.0

    def test_meal_with_none_optionals(self):
        from src.domain.entities.nutrition import Meal
        m = Meal(name="Salad", description="Light lunch", calories=None, protein=None, carbs=None, fats=None)
        assert m.calories is None
        assert m.fats is None


class TestDailyPlanEntity:
    def test_daily_plan_construction(self):
        from src.domain.entities.nutrition import DailyPlan, Meal
        dp = DailyPlan(
            day_of_week=0,
            meals=[Meal("Eggs", "Breakfast", 200, 20.0, 2.0, 10.0)]
        )
        assert dp.day_of_week == 0
        assert len(dp.meals) == 1

    def test_daily_plan_empty_meals(self):
        from src.domain.entities.nutrition import DailyPlan
        dp = DailyPlan(day_of_week=6, meals=[])
        assert dp.meals == []


class TestNutritionPlanEntity:
    def test_nutrition_plan_construction(self):
        from src.domain.entities.nutrition import NutritionPlan, DailyPlan, Meal
        now = datetime.utcnow()
        plan = NutritionPlan(
            id=uuid4(),
            user_id=uuid4(),
            name="Week 1 Plan",
            description="Bulking plan",
            week_number=1,
            year=2026,
            daily_plans=[DailyPlan(0, [Meal("Rice", "Lunch", 500, 30.0, 80.0, 8.0)])],
            is_active=True,
            created_at=now,
        )
        assert plan.name == "Week 1 Plan"
        assert plan.week_number == 1
        assert plan.is_active is True
        assert len(plan.daily_plans) == 1

    def test_nutrition_plan_inactive(self):
        from src.domain.entities.nutrition import NutritionPlan
        plan = NutritionPlan(
            id=uuid4(), user_id=uuid4(), name="Old Plan", description="Outdated",
            week_number=50, year=2025, daily_plans=[], is_active=False, created_at=datetime.utcnow()
        )
        assert plan.is_active is False


# ---------------------------------------------------------------------------
# ProfileAuditLog
# ---------------------------------------------------------------------------

class TestProfileAuditLog:
    def test_audit_log_construction(self):
        from src.domain.entities.audit import ProfileAuditLog
        now = datetime.utcnow()
        uid = uuid4()
        log = ProfileAuditLog(
            id=uuid4(),
            user_id=uid,
            changed_by=uid,
            changes={"full_name": {"old": "Ana", "new": "Ana López"}},
            timestamp=now,
        )
        assert log.user_id == uid
        assert "full_name" in log.changes
        assert log.changes["full_name"]["new"] == "Ana López"
        assert log.timestamp == now

    def test_audit_log_empty_changes(self):
        from src.domain.entities.audit import ProfileAuditLog
        log = ProfileAuditLog(
            id=uuid4(), user_id=uuid4(), changed_by=uuid4(), changes={}, timestamp=datetime.utcnow()
        )
        assert log.changes == {}


# ---------------------------------------------------------------------------
# Instructor (Historia 3)
# ---------------------------------------------------------------------------

class TestInstructorEntities:
    def test_instructor_construction(self):
        from src.domain.entities.instructor import Instructor
        iid = uuid4()
        inst = Instructor(
            id=iid,
            name="Coach Ana",
            certifications=["ACE", "NASM"],
            specializations="Fuerza",
            rating_avg=4.5,
            active_users_count=3,
        )
        assert inst.id == iid
        assert inst.name == "Coach Ana"
        assert inst.certifications == ["ACE", "NASM"]
        assert inst.rating_avg == 4.5
        assert inst.active_users_count == 3

    def test_instructor_assignment_construction(self):
        from src.domain.entities.instructor import InstructorAssignment
        uid, iid = uuid4(), uuid4()
        now = datetime.utcnow()
        a = InstructorAssignment(
            id=uuid4(), user_id=uid, instructor_id=iid,
            started_at=now, ended_at=None, is_active=True,
        )
        assert a.user_id == uid
        assert a.instructor_id == iid
        assert a.is_active is True
        assert a.ended_at is None

    def test_instructor_rating_construction(self):
        from src.domain.entities.instructor import InstructorRating
        r = InstructorRating(
            id=uuid4(), user_id=uuid4(), instructor_id=uuid4(),
            rating=4, created_at=datetime.utcnow(), comment="Muy bueno",
        )
        assert r.rating == 4
        assert r.comment == "Muy bueno"
