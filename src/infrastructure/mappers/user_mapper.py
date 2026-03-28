from uuid import UUID
from ...domain.entities.user import User, UserRole, Gender, FitnessGoal
from ..database.models.user_model import UserModel

class UserMapper:

    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(id=UUID(model.id), email=model.email, password_hash=model.password_hash, role=UserRole(model.role), is_active=model.is_active, created_at=model.created_at, updated_at=getattr(model, 'updated_at', None), full_name=getattr(model, 'full_name', None), version=getattr(model, 'version', 1), age=getattr(model, 'age', None), gender=Gender(model.gender) if getattr(model, 'gender', None) else None, height=getattr(model, 'height', None), fitness_goal=FitnessGoal(model.fitness_goal) if getattr(model, 'fitness_goal', None) else None, activity_level=getattr(model, 'activity_level', None))

    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(id=str(user.id), email=user.email, password_hash=user.password_hash, role=user.role.value if hasattr(user.role, 'value') else user.role, is_active=user.is_active, created_at=user.created_at, updated_at=user.updated_at, full_name=user.full_name, version=user.version, age=user.age, gender=user.gender.value if user.gender and hasattr(user.gender, 'value') else user.gender, height=user.height, fitness_goal=user.fitness_goal.value if user.fitness_goal and hasattr(user.fitness_goal, 'value') else user.fitness_goal, activity_level=user.activity_level)
