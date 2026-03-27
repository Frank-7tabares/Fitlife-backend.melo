"""Repositorio de tokens de restablecimiento de contraseña usando SQLAlchemy."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.password_reset_token import PasswordResetToken, ResetTokenStatus
from ...domain.repositories.password_reset_token_repository import PasswordResetTokenRepository
from ..database.models.auth_models import PasswordResetTokenModel


class SQLAlchemyPasswordResetTokenRepository(PasswordResetTokenRepository):
    """Persiste tokens de restablecimiento de contraseña."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, token: PasswordResetToken) -> None:
        """Guarda un nuevo token de restablecimiento."""
        model = PasswordResetTokenModel(
            id=str(token.id),
            user_id=str(token.user_id),
            token=token.token,
            expires_at=token.expires_at,
            status=token.status,
            created_at=token.created_at,
            used_at=token.used_at,
        )
        self.session.add(model)
        await self.session.commit()

    async def find_by_token(self, token: str) -> Optional[PasswordResetToken]:
        """Busca un token válido y no expirado."""
        stmt = select(PasswordResetTokenModel).where(
            PasswordResetTokenModel.token == token,
            PasswordResetTokenModel.status == ResetTokenStatus.PENDING,
        )
        result = await self.session.execute(stmt)
        row = result.scalars().first()

        if not row:
            return None
        
        # Verificar expiración
        if row.expires_at < datetime.utcnow():
            return None
        
        return PasswordResetToken(
            id=UUID(row.id),
            user_id=UUID(row.user_id),
            token=row.token,
            expires_at=row.expires_at,
            status=ResetTokenStatus(row.status),
            created_at=row.created_at,
            used_at=row.used_at,
        )

    async def mark_as_used(self, token_id: UUID) -> None:
        """Marca un token como usado."""
        stmt = (
            update(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.id == str(token_id))
            .values(status=ResetTokenStatus.USED, used_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_expired_tokens(self, user_id: UUID) -> None:
        """Elimina tokens expirados de un usuario."""
        stmt = delete(PasswordResetTokenModel).where(
            PasswordResetTokenModel.user_id == str(user_id),
            PasswordResetTokenModel.expires_at < datetime.utcnow(),
        )
        await self.session.execute(stmt)
        await self.session.commit()
