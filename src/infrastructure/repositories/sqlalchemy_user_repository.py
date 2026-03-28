from typing import Optional
from uuid import UUID
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.repositories.user_repository import UserRepository
from ...domain.entities.user import User, UserRole
from ..database.models.user_model import UserModel

class SQLAlchemyUserRepository(UserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: User) -> User:
        user_model = UserModel(id=str(user.id), email=user.email, password_hash=user.password_hash, role=user.role, is_active=user.is_active, full_name=user.full_name, age=user.age, gender=user.gender, height=user.height, fitness_goal=user.fitness_goal, activity_level=user.activity_level, created_at=user.created_at)
        self.session.add(user_model)
        await self.session.commit()
        return user

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == str(user_id))
        result = await self.session.execute(stmt)
        user_model = result.scalars().first()
        if user_model:
            return self._map_to_entity(user_model)
        return None

    async def find_by_email(self, email: str) -> Optional[User]:
        email_norm = (email or '').strip().lower()
        stmt = select(UserModel).where(func.lower(UserModel.email) == email_norm)
        result = await self.session.execute(stmt)
        user_model = result.scalars().first()
        if user_model:
            return self._map_to_entity(user_model)
        return None

    async def update(self, user: User) -> User:
        stmt = select(UserModel).where(UserModel.id == str(user.id))
        result = await self.session.execute(stmt)
        user_model = result.scalars().first()
        if user_model:
            if user_model.version != user.version:
                raise ValueError('Concurrency conflict: The user profile has been updated by another process.')
            user_model.email = user.email
            user_model.password_hash = user.password_hash
            user_model.role = user.role
            user_model.is_active = user.is_active
            user_model.full_name = user.full_name
            user_model.age = user.age
            user_model.gender = user.gender
            user_model.height = user.height
            user_model.fitness_goal = user.fitness_goal
            user_model.activity_level = user.activity_level
            user_model.version += 1
            await self.session.commit()
            user.version = user_model.version
        return user

    async def exists_by_email(self, email: str) -> bool:
        email_norm = (email or '').strip().lower()
        stmt = select(UserModel).where(func.lower(UserModel.email) == email_norm)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def find_all(self) -> list[User]:
        stmt = select(UserModel).order_by(UserModel.created_at.desc())
        result = await self.session.execute(stmt)
        return [self._map_to_entity(m) for m in result.scalars().all()]

    async def find_by_role(self, role: str) -> list[User]:
        role_enum = UserRole(role) if isinstance(role, str) else role
        stmt = select(UserModel).where(UserModel.role == role_enum).order_by(UserModel.created_at.desc())
        result = await self.session.execute(stmt)
        return [self._map_to_entity(m) for m in result.scalars().all()]

    async def delete_by_id(self, user_id: UUID) -> bool:
        stmt = delete(UserModel).where(UserModel.id == str(user_id))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    def _map_to_entity(self, model: UserModel) -> User:
        return User(id=UUID(model.id), email=model.email, password_hash=model.password_hash, role=model.role, is_active=model.is_active, created_at=model.created_at, updated_at=model.updated_at, full_name=model.full_name, version=model.version, age=model.age, gender=model.gender, height=model.height, fitness_goal=model.fitness_goal, activity_level=model.activity_level)
