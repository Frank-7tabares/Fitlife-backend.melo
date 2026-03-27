"""Dependencias compartidas para los adaptadores API (FastAPI Depends)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database.connection import get_db
from ...infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ...infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
from ...application.services.jwt_service import JWTService
from ...domain.entities.user import User, UserRole

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> SQLAlchemyUserRepository:
    """Inyecta el repositorio de usuarios."""
    return SQLAlchemyUserRepository(db)


async def get_refresh_token_repository(
    db: AsyncSession = Depends(get_db),
) -> SQLAlchemyRefreshTokenRepository:
    """Inyecta el repositorio de tokens de refresco."""
    return SQLAlchemyRefreshTokenRepository(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> User:
    """Valida el JWT del header Authorization y retorna el usuario autenticado."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido",
        )
    try:
        payload = JWTService.decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token inválido: sin sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o expirado",
        )

    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de usuario inactiva",
        )
    return user


async def get_current_instructor(
    current_user: User = Depends(get_current_user),
) -> User:
    """Requiere que el usuario autenticado tenga rol INSTRUCTOR o ADMIN."""
    if current_user.role not in (UserRole.INSTRUCTOR, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a instructores",
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Requiere que el usuario autenticado tenga rol ADMIN."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores",
        )
    return current_user
