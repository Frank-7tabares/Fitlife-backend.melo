"""Puerto de salida: Repositorio de entrenamientos (interfaz ABC)."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.training import Routine, RoutineAssignment, WorkoutCompletion


class TrainingRepository(ABC):
    """Puerto de salida para persistencia de rutinas de entrenamiento."""

    @abstractmethod
    async def save_routine(self, routine: Routine) -> Routine:
        """Persiste una rutina nueva."""
        ...

    @abstractmethod
    async def find_routine_by_id(self, routine_id: UUID) -> Optional[Routine]:
        """Busca una rutina por ID."""
        ...


class TrainingAssignmentRepository(ABC):
    """Puerto de salida para asignaciones de rutinas."""

    @abstractmethod
    async def save_assignment(self, assignment: RoutineAssignment) -> RoutineAssignment:
        """Persiste una asignación de rutina."""
        ...

    @abstractmethod
    async def find_active_assignment(self, user_id: UUID) -> Optional[RoutineAssignment]:
        """Obtiene la asignación activa de rutina de un usuario."""
        ...

    @abstractmethod
    async def find_completions_by_user(self, user_id: UUID, limit: int = 50) -> List[WorkoutCompletion]:
        """Lista las completaciones de entrenamiento de un usuario (más recientes primero)."""
        ...

    @abstractmethod
    async def save_completion(self, completion: WorkoutCompletion) -> WorkoutCompletion:
        """Registra la completación de un entrenamiento."""
        ...
