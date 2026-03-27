from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ....infrastructure.database.connection import get_db
from ....infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ....infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
from ....infrastructure.repositories.sqlalchemy_instructor_repository import SQLAlchemyInstructorRepository
from ....infrastructure.repositories.sqlalchemy_password_reset_token_repository import SQLAlchemyPasswordResetTokenRepository
from ....infrastructure.repositories.sqlalchemy_password_history_repository import SQLAlchemyPasswordHistoryRepository
from ....application.use_cases.register_user import RegisterUser
from ....application.use_cases.login_user import LoginUser
from ....application.use_cases.refresh_token import RefreshToken
from ....application.use_cases.password_reset_request import PasswordResetRequest
from ....application.use_cases.password_reset import PasswordReset
from ....application.use_cases.password_change import PasswordChange
from ....application.dtos.auth_dtos import (
    RegisterUserRequest,
    LoginUserRequest,
    RefreshTokenRequest,
    PasswordResetRequestDto,
    PasswordResetVerifyCodeDto,
    PasswordResetDto,
    PasswordChangeDto,
    TokenResponse,
    RegisterResponse,
    PasswordChangeResponse,
)
from ....application.exceptions import EmailAlreadyRegisteredError
from ....config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/test-smtp")
async def test_smtp(email: str = ""):
    """Solo DEBUG: prueba SMTP. URL: /api/v1/auth/test-smtp?email=tu@email.com"""
    import os
    if not os.getenv("DEBUG", "").lower() in ("true", "1", "yes"):
        return {"ok": False, "error": "Solo en modo DEBUG"}
    if not email or "@" not in email:
        return {"ok": False, "error": "Indica ?email=tu@email.com"}
    try:
        from ....infrastructure.email.email_service_smtp import SmtpEmailService
        sent = await SmtpEmailService.send_password_reset_email(
            to_email=email, reset_token="test-token", user_name="Test"
        )
        return {"ok": sent, "message": "Email enviado. Revisa bandeja y spam." if sent else "No se envio"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def get_user_repository(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyUserRepository(db)

async def get_refresh_token_repository(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyRefreshTokenRepository(db)

async def get_password_reset_token_repository(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyPasswordResetTokenRepository(db)

async def get_password_history_repository(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyPasswordHistoryRepository(db)

async def get_instructor_repository(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyInstructorRepository(db)

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterUserRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    refresh_repo: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repository),
    instructor_repo: SQLAlchemyInstructorRepository = Depends(get_instructor_repository),
):
    use_case = RegisterUser(user_repo, refresh_repo, instructor_repo)
    try:
        return await use_case.execute(request)
    except EmailAlreadyRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        detail = str(e) if getattr(settings, "DEBUG", False) else "Error al registrarse. Intenta de nuevo."
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginUserRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    refresh_repo: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repository),
):
    use_case = LoginUser(user_repo, refresh_repo)
    try:
        return await use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshTokenRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    refresh_repo: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repository),
):
    use_case = RefreshToken(user_repo, refresh_repo)
    try:
        return await use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/password/reset-request", status_code=status.HTTP_200_OK)
async def reset_password_request(
    request: PasswordResetRequestDto,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    reset_token_repo: SQLAlchemyPasswordResetTokenRepository = Depends(get_password_reset_token_repository),
):
    """Solicita restablecimiento de contraseña (RF-012 a RF-014, RF-024).

    Respuesta genérica para prevenir enumeración de usuarios (RF-024).
    """
    print(f"[API] POST /auth/password/reset-request email={request.email}", flush=True)
    use_case = PasswordResetRequest(user_repo, reset_token_repo)
    try:
        return await use_case.execute(request)
    except Exception as e:
        # En modo DEBUG mostramos el detalle real (por ejemplo, SMTP no configurado).
        detail = str(e) if getattr(settings, "DEBUG", False) else "Error al procesar solicitud"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

@router.post("/password/reset", response_model=PasswordChangeResponse)
async def reset_password(
    request: PasswordResetDto,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    reset_token_repo: SQLAlchemyPasswordResetTokenRepository = Depends(get_password_reset_token_repository),
    password_history_repo: SQLAlchemyPasswordHistoryRepository = Depends(get_password_history_repository),
):
    """Confirma restablecimiento de contraseña con token (RF-015 a RF-018).

    Validaciones:
    - Token válido y no expirado (RF-015, RF-016)
    - Contraseña con complejidad requerida (RF-017)
    - No reutilización de últimas 5 contraseñas (RF-019)
    """
    use_case = PasswordReset(user_repo, reset_token_repo, password_history_repo)
    try:
        return await use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/password/verify-code", status_code=status.HTTP_200_OK)
async def verify_reset_code(
    request: PasswordResetVerifyCodeDto,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    reset_token_repo: SQLAlchemyPasswordResetTokenRepository = Depends(get_password_reset_token_repository),
):
    """Valida que el código OTP pertenezca al email indicado y esté vigente."""
    token_entity = await reset_token_repo.find_by_token(request.token)
    if not token_entity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido o expirado")
    user = await user_repo.find_by_id(token_entity.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido o expirado")
    if user.email.strip().lower() != str(request.email).strip().lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido para este correo")
    return {"message": "Código válido"}

@router.post("/password/change", response_model=PasswordChangeResponse)
async def change_password(
    user_id: UUID,
    request: PasswordChangeDto,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_history_repo: SQLAlchemyPasswordHistoryRepository = Depends(get_password_history_repository),
    refresh_repo: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repository),
):
    """Cambia contraseña de usuario autenticado (RF-020 a RF-021).

    Validaciones:
    - Contraseña actual es correcta (RF-020)
    - Nueva contraseña con complejidad requerida (RF-021)
    - No reutilización de últimas 5 contraseñas (RF-019)

    Nota: En futuras fases, validar que user_id provenga del JWT (no solo del path).
    """
    use_case = PasswordChange(user_repo, password_history_repo, refresh_repo)
    try:
        return await use_case.execute(str(user_id), request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
