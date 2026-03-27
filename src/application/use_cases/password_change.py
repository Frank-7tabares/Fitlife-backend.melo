"""Caso de uso: cambiar contraseña (autenticado) - RF-020 a RF-021."""
from datetime import datetime
from uuid import uuid4, UUID
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.password_history_repository import PasswordHistoryRepository
from ...domain.entities.password_history import PasswordHistory
from ...infrastructure.security.password_hasher import PasswordHasher
from ...infrastructure.security.password_validator import PasswordValidator
from ...infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
from ..dtos.auth_dtos import PasswordChangeDto, PasswordChangeResponse


class PasswordChange:
    """Cambio de contraseña para usuario autenticado.

    Requisitos funcionales:
    - RF-020: Verificar contraseña actual antes de permitir cambio
    - RF-021: Validar complejidad de nueva contraseña
    - RF-019: No reutilizar últimas 5 contraseñas
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_history_repository: PasswordHistoryRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.password_history_repository = password_history_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, user_id: str, request: PasswordChangeDto) -> PasswordChangeResponse:
        """Ejecuta cambio de contraseña para usuario autenticado.

        Args:
            user_id: ID del usuario autenticado (del JWT)
            request: DTO con current_password y new_password

        Raises:
            ValueError: Si contraseña actual inválida, nueva contraseña débil, o reutiliza antiguas
        """
        # Obtener usuario
        user_id_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        user = await self.user_repository.find_by_id(user_id_uuid)
        if not user:
            raise ValueError("Usuario no encontrado")

        # RF-020: Verificar contraseña actual
        if not PasswordHasher.verify(request.current_password, user.password_hash):
            raise ValueError("Contraseña actual incorrecta")

        # RF-021: Validar complejidad de nueva contraseña
        is_valid, error_message = PasswordValidator.validate(request.new_password)
        if not is_valid:
            raise ValueError(f"Contraseña débil: {error_message}")

        # RF-019: Verificar que no reutilice últimas 5 contraseñas
        old_hashes = await self.password_history_repository.get_last_n_hashes(user.id, 5)

        for old_hash in old_hashes:
            if PasswordHasher.verify(request.new_password, old_hash):
                raise ValueError("No puedes reutilizar una contraseña anterior. Elige una contraseña diferente a las últimas 5.")

        # Guardar contraseña anterior en historial antes de cambiar
        history = PasswordHistory(
            id=uuid4(),
            user_id=user.id,
            password_hash=user.password_hash,
            changed_at=datetime.utcnow(),
        )
        await self.password_history_repository.save(history)

        # Cambiar contraseña
        user.password_hash = PasswordHasher.hash(request.new_password)
        await self.user_repository.update(user)

        # Limpiar historial muy antiguo (mantener solo últimas 5)
        await self.password_history_repository.delete_old_entries(user.id, keep=5)

        # Invalidar todos los refresh tokens del usuario para cerrar sesión en otras cuentas.
        await self.refresh_token_repository.revoke_all_for_user(user.id)

        return PasswordChangeResponse(
            message="Contraseña actualizada exitosamente",
            updated_at=datetime.utcnow(),
        )
