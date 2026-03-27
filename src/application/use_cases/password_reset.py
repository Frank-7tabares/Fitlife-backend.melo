"""Caso de uso: confirmar restablecimiento de contraseña con token (RF-015 a RF-018)."""
from datetime import datetime
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.password_reset_token_repository import PasswordResetTokenRepository
from ...domain.repositories.password_history_repository import PasswordHistoryRepository
from ...domain.entities.password_history import PasswordHistory
from ...domain.entities.password_reset_token import ResetTokenStatus
from ...infrastructure.security.password_hasher import PasswordHasher
from ...infrastructure.security.password_validator import PasswordValidator
from ..dtos.auth_dtos import PasswordResetDto, PasswordChangeResponse
from uuid import uuid4


class PasswordReset:
    """Confirma restablecimiento de contraseña con token seguro.

    Requisitos funcionales:
    - RF-015: Validar token (no expirado, no usado, existe)
    - RF-016: Token válido 1 hora
    - RF-017: Validar complejidad de nueva contraseña
    - RF-018: Cambiar contraseña en BD
    - RF-019: Guardar contraseña anterior en historial (no reutilizar últimas 5)
    """

    def __init__(
        self,
        user_repository: UserRepository,
        reset_token_repository: PasswordResetTokenRepository,
        password_history_repository: PasswordHistoryRepository,
    ):
        self.user_repository = user_repository
        self.reset_token_repository = reset_token_repository
        self.password_history_repository = password_history_repository

    async def execute(self, request: PasswordResetDto) -> PasswordChangeResponse:
        """Ejecuta confirmación de restablecimiento.

        Raises:
            ValueError: Si token inválido, expirado, ya usado, o contraseña inválida
        """
        if not request.token or not request.token.strip():
            raise ValueError("Código/token requerido")

        # RF-015: Buscar y validar token/código
        reset_token = await self.reset_token_repository.find_by_token(request.token)

        if not reset_token:
            raise ValueError("Token inválido o no encontrado")

        if reset_token.status == ResetTokenStatus.USED:
            raise ValueError("Token ya ha sido utilizado")

        if reset_token.status == ResetTokenStatus.EXPIRED:
            raise ValueError("Token expirado")

        # RF-016: Validar expiración
        if datetime.utcnow() > reset_token.expires_at:
            raise ValueError("Token expirado")

        # Obtener usuario
        user = await self.user_repository.find_by_id(reset_token.user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        # Si viene email, forzar que el código corresponda a ese usuario (flujo por OTP).
        if request.email and str(request.email).strip().lower() != user.email.strip().lower():
            raise ValueError("Código inválido para este correo")

        # RF-017: Validar complejidad de nueva contraseña
        is_valid, error_message = PasswordValidator.validate(request.new_password)
        if not is_valid:
            raise ValueError(f"Contraseña débil: {error_message}")

        # RF-019: Verificar que no reutilice últimas 5 contraseñas
        old_hashes = await self.password_history_repository.get_last_n_hashes(user.id, 5)
        new_hash = PasswordHasher.hash(request.new_password)

        for old_hash in old_hashes:
            if PasswordHasher.verify(request.new_password, old_hash):
                raise ValueError("No puedes reutilizar una contraseña anterior. Elige una contraseña diferente a las últimas 5.")

        # RF-018: Cambiar contraseña (guardar hash anterior antes de actualizar)
        old_hash_to_save = user.password_hash
        user.password_hash = new_hash
        await self.user_repository.update(user)

        # Guardar en historial la contraseña que acabamos de reemplazar
        history = PasswordHistory(
            id=uuid4(),
            user_id=user.id,
            password_hash=old_hash_to_save,
            changed_at=datetime.utcnow(),
        )
        await self.password_history_repository.save(history)

        # Limpiar tokens expirados y marcar este como usado
        await self.reset_token_repository.mark_as_used(reset_token.id)
        await self.reset_token_repository.delete_expired_tokens(user.id)

        return PasswordChangeResponse(
            message="Contraseña restablecida exitosamente",
            updated_at=datetime.utcnow(),
        )
