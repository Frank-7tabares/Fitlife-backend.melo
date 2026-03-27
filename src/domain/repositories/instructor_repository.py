"""Puerto de salida: Repositorio de instructores (interfaz ABC)."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.instructor import Instructor, InstructorAssignment, InstructorRating


class InstructorRepository(ABC):
    """Puerto de salida para persistencia de instructores."""

    @abstractmethod
    async def save(self, instructor: Instructor) -> Instructor:
        """Persiste un instructor nuevo o actualizado."""
        ...

    @abstractmethod
    async def find_by_id(self, instructor_id: UUID) -> Optional[Instructor]:
        """Busca un instructor por ID."""
        ...

    @abstractmethod
    async def find_all(self) -> List[Instructor]:
        """Obtiene todos los instructores disponibles."""
        ...

    @abstractmethod
    async def update_rating_avg(self, instructor_id: UUID, new_avg: float) -> None:
        """Actualiza el promedio de calificación de un instructor."""
        ...


class InstructorAssignmentRepository(ABC):
    """Puerto de salida para asignaciones de instructores."""

    @abstractmethod
    async def save(self, assignment: InstructorAssignment) -> InstructorAssignment:
        """Persiste una asignación."""
        ...

    @abstractmethod
    async def find_active_by_user(self, user_id: UUID) -> Optional[InstructorAssignment]:
        """Busca la asignación activa de un usuario."""
        ...

    @abstractmethod
    async def deactivate_active_for_user(self, user_id: UUID) -> None:
        """Desactiva la asignación activa de un usuario."""
        ...

    @abstractmethod
    async def count_active_by_instructor(self, instructor_id: UUID) -> int:
        """Cuenta usuarios activos de un instructor."""
        ...


class InstructorRatingRepository(ABC):
    """Puerto de salida para calificaciones de instructores."""

    @abstractmethod
    async def save(self, rating: InstructorRating) -> InstructorRating:
        """Persiste una calificación."""
        ...

    @abstractmethod
    async def get_average_rating(self, instructor_id: UUID) -> Optional[float]:
        """Obtiene el promedio de calificaciones de un instructor."""
        ...
