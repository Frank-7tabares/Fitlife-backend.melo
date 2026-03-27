from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from ..entities.user import User

class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass

    @abstractmethod
    async def find_all(self) -> list[User]:
        pass

    @abstractmethod
    async def find_by_role(self, role: str) -> list[User]:
        pass

    @abstractmethod
    async def delete_by_id(self, user_id: UUID) -> bool:
        pass
