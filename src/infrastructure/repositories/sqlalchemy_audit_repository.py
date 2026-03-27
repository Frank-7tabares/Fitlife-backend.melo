from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.domain.entities.audit import ProfileAuditLog
from src.infrastructure.database.models.audit_model import ProfileAuditLogModel

class SQLAlchemyAuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_log(self, log: ProfileAuditLog) -> ProfileAuditLog:
        model = ProfileAuditLogModel(
            id=str(log.id),
            user_id=str(log.user_id),
            changed_by=str(log.changed_by),
            changes=log.changes,
            timestamp=log.timestamp
        )
        self.session.add(model)
        await self.session.commit()
        return log

    async def delete_logs_involving_user(self, user_id: UUID) -> None:
        """Elimina logs donde user_id o changed_by = user_id (para poder eliminar usuario)."""
        uid = str(user_id)
        stmt = delete(ProfileAuditLogModel).where(
            (ProfileAuditLogModel.user_id == uid) | (ProfileAuditLogModel.changed_by == uid)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_logs_by_user_id(self, user_id: UUID) -> list[ProfileAuditLog]:
        """Obtiene todos los registros de auditoría de un usuario ordenados por timestamp DESC."""
        stmt = select(ProfileAuditLogModel).where(
            ProfileAuditLogModel.user_id == str(user_id)
        ).order_by(ProfileAuditLogModel.timestamp.desc())
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [
            ProfileAuditLog(
                id=UUID(model.id),
                user_id=UUID(model.user_id),
                changed_by=UUID(model.changed_by),
                changes=model.changes,
                timestamp=model.timestamp
            )
            for model in models
        ]
