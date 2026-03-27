"""Repositorio de tokens de actualización (refresh) usando SQLAlchemy."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.auth_models import RefreshTokenModel


class SQLAlchemyRefreshTokenRepository:
    """Persiste y valida refresh tokens para renovación de access token y revocación."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user_id: UUID, token: str, expires_at: datetime) -> None:
        model = RefreshTokenModel(
            user_id=str(user_id),
            token=token,
            expires_at=expires_at,
        )
        self.session.add(model)
        await self.session.commit()

    async def find_valid_user_id(self, token: str) -> Optional[UUID]:
        """Devuelve user_id si el token existe, no está revocado y no ha expirado."""
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token == token,
            RefreshTokenModel.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if not row or row.expires_at < datetime.utcnow():
            return None
        return UUID(row.user_id)

    async def revoke(self, token: str) -> None:
        """Marca el token como revocado (logout o rotación)."""
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token == token)
            .values(revoked_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        """Revoca todos los refresh tokens válidos de un usuario."""
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == str(user_id),
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
        await self.session.commit()
