from datetime import datetime, timedelta
from ...domain.repositories.user_repository import UserRepository
from ..dtos.auth_dtos import TokenResponse, RefreshTokenRequest
from ...infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
from ..services.jwt_service import JWTService
from ...config.settings import settings

class RefreshToken:

    def __init__(self, user_repository: UserRepository, refresh_token_repository: SQLAlchemyRefreshTokenRepository):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, request: RefreshTokenRequest) -> TokenResponse:
        user_id = await self.refresh_token_repository.find_valid_user_id(request.refresh_token)
        if not user_id:
            raise ValueError('Invalid or expired refresh token')
        user = await self.user_repository.find_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError('User not found or inactive')
        await self.refresh_token_repository.revoke(request.refresh_token)
        access_token = JWTService.create_access_token(data={'sub': str(user.id), 'role': user.role})
        new_refresh_token = JWTService.create_refresh_token(data={'sub': str(user.id)})
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_token_repository.save(user.id, new_refresh_token, expires_at)
        return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)
