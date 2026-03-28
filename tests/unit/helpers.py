from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

def make_user(role=None, is_active=True, full_name=None, version=1, user_id=None):
    from src.domain.entities.user import User, UserRole
    return User(id=user_id or uuid4(), email='user@example.com', password_hash='$2b$12$hashed', role=role or UserRole.USER, is_active=is_active, created_at=datetime.utcnow(), full_name=full_name, version=version)

def make_user_entity(user_id=None, email='u@e.com', full_name='User', version=1):
    from src.domain.entities.user import User, UserRole
    return User(id=user_id or uuid4(), email=email, password_hash='$2b$hashed', role=UserRole.USER, is_active=True, created_at=datetime.utcnow(), full_name=full_name, version=version)

def make_assessment_entity(user_id=None):
    from src.domain.entities.assessment import Assessment, AssessmentCategory, BodyAgeComparison
    return Assessment(id=uuid4(), user_id=user_id or uuid4(), fitness_score=75.0, category=AssessmentCategory.GOOD, body_age=28.0, comparison=BodyAgeComparison.BODY_YOUNGER, responses={'q1': 7}, created_at=datetime.utcnow())

def make_physical_record_entity(user_id=None):
    from src.domain.entities.physical_record import ActivityLevel, PhysicalRecord
    return PhysicalRecord(id=uuid4(), user_id=user_id or uuid4(), weight=70.0, height=175.0, body_fat_percentage=None, waist=None, hip=None, activity_level=ActivityLevel.MODERATE, recorded_at=datetime.utcnow())

def make_routine_entity():
    from src.domain.entities.training import Routine, RoutineExercise, FitnessLevel
    return Routine(id=uuid4(), name='Full Body', description='All muscles', goal='STRENGTH', level=FitnessLevel.BEGINNER, exercises=[RoutineExercise(exercise_id=uuid4(), sets=3, reps=10, rest_seconds=60)], creator_id=uuid4())

def make_nutrition_plan_entity(user_id=None):
    from src.domain.entities.nutrition import NutritionPlan, DailyPlan, Meal
    return NutritionPlan(id=uuid4(), user_id=user_id or uuid4(), name='Week 1', description='First plan', week_number=1, year=2026, daily_plans=[DailyPlan(0, [Meal('Oats', 'Breakfast', 300, 15.0, 50.0, 5.0)])], is_active=True, created_at=datetime.utcnow())

def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    return session

def result_with(scalar_value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_value
    return result

def result_with_scalars(values):
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = values
    result.scalars.return_value = scalars
    return result

def mock_user_model(user_id=None, email='u@e.com', password_hash='h', role='USER', is_active=True, full_name=None, created_at=None, updated_at=None, version=1):
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

def mock_assessment_model(assessment_id=None, user_id=None):
    m = MagicMock()
    m.id = str(assessment_id or uuid4())
    m.user_id = str(user_id or uuid4())
    m.fitness_score = 75.0
    m.category = 'GOOD'
    m.body_age = 28.0
    m.comparison = 'BODY_YOUNGER'
    m.responses = {'q1': 7}
    m.created_at = datetime.utcnow()
    return m

def mock_physical_record_model(record_id=None, user_id=None):
    m = MagicMock()
    m.id = str(record_id or uuid4())
    m.user_id = str(user_id or uuid4())
    m.weight = 70.0
    m.height = 175.0
    m.body_fat_percentage = None
    m.waist = None
    m.hip = None
    m.activity_level = 'MODERATE'
    m.recorded_at = datetime.utcnow()
    return m

def mock_routine_model(routine_id=None, creator_id=None):
    m = MagicMock()
    m.id = str(routine_id or uuid4())
    m.name = 'Full Body'
    m.description = 'All muscles'
    m.goal = 'STRENGTH'
    m.level = 'BEGINNER'
    m.exercises_data = [{'exercise_id': str(uuid4()), 'sets': 3, 'reps': 10, 'rest_seconds': 60}]
    m.creator_id = str(creator_id or uuid4())
    return m

def mock_assignment_model(user_id=None, routine_id=None):
    m = MagicMock()
    m.user_id = str(user_id or uuid4())
    m.routine_id = str(routine_id or uuid4())
    m.assigned_at = datetime.utcnow()
    m.is_active = True
    return m

def mock_nutrition_plan_model(plan_id=None, user_id=None):
    m = MagicMock()
    m.id = str(plan_id or uuid4())
    m.user_id = str(user_id or uuid4())
    m.name = 'Week 1'
    m.description = 'First week'
    m.week_number = 1
    m.year = 2026
    m.plans_data = [{'day_of_week': 0, 'meals': [{'name': 'Oats', 'description': 'Breakfast', 'calories': 300, 'protein': 15.0, 'carbs': 50.0, 'fats': 5.0}]}]
    m.is_active = True
    m.created_at = datetime.utcnow()
    return m
