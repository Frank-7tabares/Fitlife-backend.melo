"""Mock fixtures reutilizables para tests unitarios."""
from datetime import datetime
from uuid import uuid4
from unittest.mock import MagicMock, AsyncMock

from src.domain.entities.user import User, UserRole
from src.domain.entities.assessment import Assessment, AssessmentCategory, BodyAgeComparison
from src.domain.entities.instructor import Instructor, InstructorAssignment
from src.domain.entities.training import Routine, FitnessLevel, RoutineAssignment
from src.domain.entities.nutrition import NutritionPlan


def make_user(
    user_id=None,
    email="test@fitlife.com",
    role=UserRole.USER,
    is_active=True,
    full_name="Test User",
) -> User:
    """Crea un usuario de dominio para tests."""
    return User(
        id=user_id or uuid4(),
        email=email,
        password_hash="$2b$12$fakehash_for_testing_only",
        role=role,
        is_active=is_active,
        created_at=datetime.utcnow(),
        full_name=full_name,
    )


def make_assessment(user_id=None) -> Assessment:
    """Crea una evaluación física para tests."""
    return Assessment(
        id=uuid4(),
        user_id=user_id or uuid4(),
        fitness_score=75.0,
        category=AssessmentCategory.GOOD,
        body_age=28.0,
        comparison=BodyAgeComparison.BODY_YOUNGER,
        responses={"q1": 7, "q2": 3},
        created_at=datetime.utcnow(),
    )


def make_instructor(instructor_id=None) -> Instructor:
    """Crea un instructor para tests."""
    return Instructor(
        id=instructor_id or uuid4(),
        name="Coach Test",
        certifications=["ACE", "NSCA"],
        specializations="Fuerza y acondicionamiento",
        rating_avg=4.5,
        active_users_count=3,
    )


def make_routine(creator_id=None) -> Routine:
    """Crea una rutina de entrenamiento para tests."""
    from src.domain.entities.training import RoutineExercise
    return Routine(
        id=uuid4(),
        name="Full Body Workout",
        description="Entrenamiento completo",
        goal="STRENGTH",
        level=FitnessLevel.INTERMEDIATE,
        exercises=[
            RoutineExercise(exercise_id=uuid4(), sets=3, reps=10, rest_seconds=60)
        ],
        creator_id=creator_id or uuid4(),
    )


def make_nutrition_plan(user_id=None) -> NutritionPlan:
    """Crea un plan de nutrición para tests."""
    from src.domain.entities.nutrition import DailyPlan, Meal
    return NutritionPlan(
        id=uuid4(),
        user_id=user_id or uuid4(),
        name="Plan Semana 1",
        description="Plan inicial",
        week_number=1,
        year=2026,
        daily_plans=[
            DailyPlan(
                day_of_week=0,
                meals=[Meal("Avena", "Desayuno", 350, 15.0, 60.0, 6.0)],
            )
        ],
        is_active=True,
        created_at=datetime.utcnow(),
    )


def make_mock_session() -> AsyncMock:
    """Crea un mock de AsyncSession de SQLAlchemy."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.delete = AsyncMock()
    return session
