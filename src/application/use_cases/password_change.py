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

    def __init__(self, user_repository: UserRepository, password_history_repository: PasswordHistoryRepository, refresh_token_repository: SQLAlchemyRefreshTokenRepository):
        self.user_repository = user_repository
        self.password_history_repository = password_history_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, user_id: str, request: PasswordChangeDto) -> PasswordChangeResponse:
        user_id_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        user = await self.user_repository.find_by_id(user_id_uuid)
        if not user:
            raise ValueError('Usuario no encontrado')
        if not PasswordHasher.verify(request.current_password, user.password_hash):
            raise ValueError('Contraseña actual incorrecta')
        is_valid, error_message = PasswordValidator.validate(request.new_password)
        if not is_valid:
            raise ValueError(f'Contraseña débil: {error_message}')
        old_hashes = await self.password_history_repository.get_last_n_hashes(user.id, 5)
        for old_hash in old_hashes:
            if PasswordHasher.verify(request.new_password, old_hash):
                raise ValueError('No puedes reutilizar una contraseña anterior. Elige una contraseña diferente a las últimas 5.')
        history = PasswordHistory(id=uuid4(), user_id=user.id, password_hash=user.password_hash, changed_at=datetime.utcnow())
        await self.password_history_repository.save(history)
        user.password_hash = PasswordHasher.hash(request.new_password)
        await self.user_repository.update(user)
        await self.password_history_repository.delete_old_entries(user.id, keep=5)
        await self.refresh_token_repository.revoke_all_for_user(user.id)
        return PasswordChangeResponse(message='Contraseña actualizada exitosamente', updated_at=datetime.utcnow())
