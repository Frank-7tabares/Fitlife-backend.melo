from datetime import datetime, timedelta
from ...domain.repositories.user_repository import UserRepository
from ..dtos.auth_dtos import LoginUserRequest, TokenResponse
from ...infrastructure.security.password_hasher import PasswordHasher
from ...infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
from ..services.jwt_service import JWTService
from ...config.settings import settings

class LoginUser:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, request: LoginUserRequest) -> TokenResponse:
        email = str(request.email).strip().lower()
        user = await self.user_repository.find_by_email(email)
        if not user or not PasswordHasher.verify(request.password, user.password_hash):
            raise ValueError("Invalid credentials")

        if not user.is_active:
            raise ValueError("User account is inactive")

        access_token = JWTService.create_access_token(data={"sub": str(user.id), "role": user.role})
        refresh_token = JWTService.create_refresh_token(data={"sub": str(user.id)})
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_token_repository.save(user.id, refresh_token, expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
