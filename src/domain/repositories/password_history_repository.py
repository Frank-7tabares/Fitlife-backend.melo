"""Interfaz de repositorio para PasswordHistory."""
from abc import ABC, abstractmethod
from uuid import UUID
from ...domain.entities.password_history import PasswordHistory


class PasswordHistoryRepository(ABC):
    """Contrato de repositorio para historial de contraseñas."""

    @abstractmethod
    async def save(self, history: PasswordHistory) -> None:
        """Guarda un nuevo registro en el historial."""
        pass

    @abstractmethod
    async def get_last_n_hashes(self, user_id: UUID, n: int = 5) -> list[str]:
        """Obtiene los últimos n hashes de contraseña de un usuario."""
        pass

    @abstractmethod
    async def delete_old_entries(self, user_id: UUID, keep: int = 5) -> None:
        """Elimina entradas antiguas, manteniendo los últimosn registros."""
        pass
