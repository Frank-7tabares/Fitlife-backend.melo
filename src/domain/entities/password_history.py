"""Entidad de dominio: Historial de contraseñas (RF-019 - no reutilizar últimas 5)."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class PasswordHistory:
    """Registro histórico de contraseña para impedir reutilización.
    
    Atributos:
        id: UUID único del registro
        user_id: Usuario propietario
        password_hash: Hash de contraseña anterior (almacenar solo hashes, nunca texto plano)
        changed_at: Timestamp del cambio
    
    Notas:
        - Mantener solo las últimas 5 contraseñas por usuario (RF-019)
        - Al cambiar contraseña, verificar que no coincida con ninguna de las 5 anteriores
    """
    id: UUID
    user_id: UUID
    password_hash: str
    changed_at: datetime
