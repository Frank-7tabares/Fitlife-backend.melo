"""Interfaz de repositorio para PasswordResetToken."""
from abc import ABC, abstractmethod
from uuid import UUID
from ...domain.entities.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository(ABC):
    """Contrato de repositorio para tokens de restablecimiento de contraseña."""

    @abstractmethod
    async def save(self, token: PasswordResetToken) -> None:
        """Guarda un nuevo token de restablecimiento."""
        pass

    @abstractmethod
    async def find_by_token(self, token: str) -> PasswordResetToken | None:
        """Busca un token por su valor. Retorna None si no existe o está expirado."""
        pass

    @abstractmethod
    async def mark_as_used(self, token_id: UUID) -> None:
        """Marca un token como usado."""
        pass

    @abstractmethod
    async def delete_expired_tokens(self, user_id: UUID) -> None:
        """Elimina tokens expirados de un usuario."""
        pass
