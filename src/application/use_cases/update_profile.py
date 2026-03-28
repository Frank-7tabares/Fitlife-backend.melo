from uuid import uuid4, UUID
from datetime import datetime
from src.domain.entities.audit import ProfileAuditLog
from src.domain.entities.user import User
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
from src.application.dtos.user_dtos import UpdateProfileRequest, UserProfileResponse

class UpdateProfile:

    def __init__(self, user_repo: SQLAlchemyUserRepository, audit_repo: SQLAlchemyAuditRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def execute(self, user_id: UUID, changed_by: UUID, request: UpdateProfileRequest) -> UserProfileResponse:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        changes = {}
        if request.full_name is not None and request.full_name != user.full_name:
            changes['full_name'] = {'old': user.full_name, 'new': request.full_name}
            user.full_name = request.full_name
        if request.gender is not None and request.gender != user.gender:
            changes['gender'] = {'old': user.gender.value if user.gender else None, 'new': request.gender.value}
            user.gender = request.gender
        if request.age is not None and request.age != user.age:
            changes['age'] = {'old': user.age, 'new': request.age}
            user.age = request.age
        if request.height is not None and request.height != user.height:
            changes['height'] = {'old': user.height, 'new': request.height}
            user.height = request.height
        if request.fitness_goal is not None and request.fitness_goal != user.fitness_goal:
            changes['fitness_goal'] = {'old': user.fitness_goal.value if user.fitness_goal else None, 'new': request.fitness_goal.value}
            user.fitness_goal = request.fitness_goal
        if request.activity_level is not None and request.activity_level != user.activity_level:
            changes['activity_level'] = {'old': user.activity_level, 'new': request.activity_level}
            user.activity_level = request.activity_level
        if not changes:
            return self._map_to_response(user)
        user.version = request.version
        updated_user = await self.user_repo.update(user)
        audit_log = ProfileAuditLog(id=uuid4(), user_id=user_id, changed_by=changed_by, changes=changes, timestamp=datetime.utcnow())
        await self.audit_repo.save_log(audit_log)
        return self._map_to_response(updated_user)

    def _map_to_response(self, user: User) -> UserProfileResponse:
        return UserProfileResponse(id=user.id, email=user.email, full_name=user.full_name, role=user.role, version=user.version, created_at=user.created_at, age=user.age, gender=user.gender, height=user.height, fitness_goal=user.fitness_goal, activity_level=user.activity_level)
