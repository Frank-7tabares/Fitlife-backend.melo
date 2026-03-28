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

    def __init__(self, user_repository: UserRepository, reset_token_repository: PasswordResetTokenRepository, password_history_repository: PasswordHistoryRepository):
        self.user_repository = user_repository
        self.reset_token_repository = reset_token_repository
        self.password_history_repository = password_history_repository

    async def execute(self, request: PasswordResetDto) -> PasswordChangeResponse:
        if not request.token or not request.token.strip():
            raise ValueError('Código/token requerido')
        reset_token = await self.reset_token_repository.find_by_token(request.token)
        if not reset_token:
            raise ValueError('Token inválido o no encontrado')
        if reset_token.status == ResetTokenStatus.USED:
            raise ValueError('Token ya ha sido utilizado')
        if reset_token.status == ResetTokenStatus.EXPIRED:
            raise ValueError('Token expirado')
        if datetime.utcnow() > reset_token.expires_at:
            raise ValueError('Token expirado')
        user = await self.user_repository.find_by_id(reset_token.user_id)
        if not user:
            raise ValueError('Usuario no encontrado')
        if request.email and str(request.email).strip().lower() != user.email.strip().lower():
            raise ValueError('Código inválido para este correo')
        is_valid, error_message = PasswordValidator.validate(request.new_password)
        if not is_valid:
            raise ValueError(f'Contraseña débil: {error_message}')
        old_hashes = await self.password_history_repository.get_last_n_hashes(user.id, 5)
        new_hash = PasswordHasher.hash(request.new_password)
        for old_hash in old_hashes:
            if PasswordHasher.verify(request.new_password, old_hash):
                raise ValueError('No puedes reutilizar una contraseña anterior. Elige una contraseña diferente a las últimas 5.')
        old_hash_to_save = user.password_hash
        user.password_hash = new_hash
        await self.user_repository.update(user)
        history = PasswordHistory(id=uuid4(), user_id=user.id, password_hash=old_hash_to_save, changed_at=datetime.utcnow())
        await self.password_history_repository.save(history)
        await self.reset_token_repository.mark_as_used(reset_token.id)
        await self.reset_token_repository.delete_expired_tokens(user.id)
        return PasswordChangeResponse(message='Contraseña restablecida exitosamente', updated_at=datetime.utcnow())
