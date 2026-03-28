from abc import ABC, abstractmethod
from uuid import UUID
from ...domain.entities.password_history import PasswordHistory

class PasswordHistoryRepository(ABC):

    @abstractmethod
    async def save(self, history: PasswordHistory) -> None:
        pass

    @abstractmethod
    async def get_last_n_hashes(self, user_id: UUID, n: int=5) -> list[str]:
        pass

    @abstractmethod
    async def delete_old_entries(self, user_id: UUID, keep: int=5) -> None:
        pass
