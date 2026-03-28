from uuid import UUID
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
from src.application.dtos.user_dtos import ProfileAuditHistoryResponse, ProfileAuditLogResponse

class GetProfileAudit:

    def __init__(self, user_repo: UserRepository, audit_repo: SQLAlchemyAuditRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def execute(self, user_id: UUID) -> ProfileAuditHistoryResponse:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        logs = await self.audit_repo.get_logs_by_user_id(user_id)
        audit_responses = [ProfileAuditLogResponse(id=log.id, user_id=log.user_id, changed_by=log.changed_by, changes=log.changes, timestamp=log.timestamp) for log in logs]
        return ProfileAuditHistoryResponse(user_id=user_id, total=len(audit_responses), logs=audit_responses)
