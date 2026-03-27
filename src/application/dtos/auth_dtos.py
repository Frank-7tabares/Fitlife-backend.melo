from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from ...domain.entities.user import UserRole
from typing import Optional

# Límites seguros para evitar abusos (texto muy largo, etc.)
MAX_FULL_NAME = 255
MAX_SPECIALTY = 500
MAX_ADMIN_CODE = 100
MIN_PASSWORD = 8
MAX_PASSWORD = 128

def _strip_str(v: Optional[str]) -> Optional[str]:
    if v is None: return None
    s = v.strip()
    return s if s else None

class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=MIN_PASSWORD, max_length=MAX_PASSWORD)
    full_name: Optional[str] = Field(None, max_length=MAX_FULL_NAME)
    role: Optional[str] = Field("client", max_length=20)
    specialty: Optional[str] = Field(None, max_length=MAX_SPECIALTY)
    age: Optional[int] = Field(None, ge=14, le=120)
    admin_code: Optional[str] = Field(None, max_length=MAX_ADMIN_CODE)

    model_config = {"str_strip_whitespace": True}

class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: UUID
    email: str
    role: UserRole
    full_name: Optional[str]
    created_at: datetime


class RegisterResponse(BaseModel):
    """Respuesta de registro: datos de usuario y tokens (spec: proporciona tokens de acceso y actualización)."""
    id: UUID
    email: str
    role: UserRole
    full_name: Optional[str]
    age: Optional[int] = None
    created_at: datetime
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequestDto(BaseModel):
    """Solicitud de restablecimiento: envío de token por email (RF-012 a RF-014)."""
    email: EmailStr


class PasswordResetVerifyCodeDto(BaseModel):
    """Validación de código OTP para restablecer contraseña."""
    email: EmailStr
    token: str


class PasswordResetDto(BaseModel):
    """Restablecimiento de contraseña con token (RF-015 a RF-018)."""
    token: str
    email: Optional[EmailStr] = None
    new_password: str


class PasswordChangeDto(BaseModel):
    """Cambio de contraseña con verificación de actual (RF-020 a RF-021)."""
    current_password: str
    new_password: str


class PasswordChangeResponse(BaseModel):
    """Respuesta tras cambio exitoso."""
    message: str
    updated_at: datetime
