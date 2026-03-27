from uuid import uuid4
from datetime import datetime, timedelta
from ...domain.entities.user import User, UserRole
from ...domain.entities.instructor import Instructor
from ...domain.repositories.user_repository import UserRepository
from ..dtos.auth_dtos import RegisterUserRequest, RegisterResponse
from ...infrastructure.security.password_hasher import PasswordHasher
from ...infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
from ...infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRepository
from ..services.jwt_service import JWTService
from ..exceptions import EmailAlreadyRegisteredError
from ...config.settings import settings


def _resolve_role(role_str: str | None) -> UserRole:
    r = (role_str or "client").lower().strip()
    if r == "instructor" or r == "coach": return UserRole.INSTRUCTOR
    if r == "admin": return UserRole.ADMIN
    return UserRole.USER


class RegisterUser:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
        instructor_repository: SQLAlchemyInstructorRepository | None = None,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.instructor_repository = instructor_repository

    async def execute(self, request: RegisterUserRequest) -> RegisterResponse:
        # Normalizamos email para evitar problemas de mayúsculas/minúsculas.
        email = str(request.email).strip().lower()

        if await self.user_repository.exists_by_email(email):
            raise EmailAlreadyRegisteredError("Email already registered")

        role = _resolve_role(request.role)

        if role == UserRole.ADMIN:
            if not request.admin_code or request.admin_code.strip() != settings.ADMIN_REGISTER_CODE.strip():
                raise ValueError("Código de administrador inválido. Contacta al administrador del sistema.")

        user_id = uuid4()
        user_age = request.age if role == UserRole.USER else None
        user = User(
            id=user_id,
            email=email,
            password_hash=PasswordHasher.hash(request.password),
            role=role,
            is_active=True,
            created_at=datetime.utcnow(),
            full_name=request.full_name,
            age=user_age,
        )

        await self.user_repository.save(user)

        if role == UserRole.INSTRUCTOR and self.instructor_repository:
            specs = ", ".join(s.strip().upper() for s in (request.specialty or "").split(",") if s.strip())
            instructor = Instructor(
                id=user_id,
                name=request.full_name or request.email,
                certifications=[],
                specializations=specs,
                rating_avg=0.0,
                active_users_count=0,
            )
            await self.instructor_repository.save(instructor)

        access_token = JWTService.create_access_token(data={"sub": str(user.id), "role": user.role})
        refresh_token = JWTService.create_refresh_token(data={"sub": str(user.id)})
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_token_repository.save(user.id, refresh_token, expires_at)

        return RegisterResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.full_name,
            age=user.age,
            created_at=user.created_at,
            access_token=access_token,
            refresh_token=refresh_token,
        )
