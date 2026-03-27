"""Entidad de dominio: Token de restablecimiento de contraseña (RF-011 a RF-025)."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional


class ResetTokenStatus(str, Enum):
    """Estado del token de restablecimiento."""
    PENDING = "PENDING"  # Válido, sin usar
    USED = "USED"  # Ya utilizado
    EXPIRED = "EXPIRED"  # Expirado


@dataclass
class PasswordResetToken:
    """Token para restablecimiento de contraseña.
    
    Atributos:
        id: UUID único del token
        user_id: Usuario propietario
        token: Valor del token (cadena aleatoria; no es el JWT)
        expires_at: Expiración (1 hora desde creación, RF-016)
        status: PENDING | USED | EXPIRED (RF-014)
        created_at: Timestamp de creación
        used_at: Timestamp de uso (si aplicable)
    """
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    status: ResetTokenStatus
    created_at: datetime
    used_at: Optional[datetime] = None
