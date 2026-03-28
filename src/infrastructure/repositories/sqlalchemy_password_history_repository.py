from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.entities.password_history import PasswordHistory
from ...domain.repositories.password_history_repository import PasswordHistoryRepository
from ..database.models.auth_models import PasswordHistoryModel

class SQLAlchemyPasswordHistoryRepository(PasswordHistoryRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, history: PasswordHistory) -> None:
        model = PasswordHistoryModel(id=str(history.id), user_id=str(history.user_id), password_hash=history.password_hash, changed_at=history.changed_at)
        self.session.add(model)
        await self.session.commit()

    async def get_last_n_hashes(self, user_id: UUID, n: int=5) -> list[str]:
        stmt = select(PasswordHistoryModel).where(PasswordHistoryModel.user_id == str(user_id)).order_by(desc(PasswordHistoryModel.changed_at)).limit(n)
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [row.password_hash for row in rows]

    async def delete_old_entries(self, user_id: UUID, keep: int=5) -> None:
        stmt = select(PasswordHistoryModel.id).where(PasswordHistoryModel.user_id == str(user_id)).order_by(desc(PasswordHistoryModel.changed_at)).limit(keep)
        result = await self.session.execute(stmt)
        ids_to_keep = {row[0] for row in result.fetchall()}
        delete_stmt = delete(PasswordHistoryModel).where(PasswordHistoryModel.user_id == str(user_id), ~PasswordHistoryModel.id.in_(ids_to_keep) if ids_to_keep else True)
        await self.session.execute(delete_stmt)
        await self.session.commit()
