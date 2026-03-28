from abc import ABC, abstractmethod
from uuid import UUID
from ...domain.entities.password_reset_token import PasswordResetToken

class PasswordResetTokenRepository(ABC):

    @abstractmethod
    async def save(self, token: PasswordResetToken) -> None:
        pass

    @abstractmethod
    async def find_by_token(self, token: str) -> PasswordResetToken | None:
        pass

    @abstractmethod
    async def mark_as_used(self, token_id: UUID) -> None:
        pass

    @abstractmethod
    async def delete_expired_tokens(self, user_id: UUID) -> None:
        pass
