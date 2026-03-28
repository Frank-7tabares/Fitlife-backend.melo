from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.training import Routine, RoutineAssignment, WorkoutCompletion

class TrainingRepository(ABC):

    @abstractmethod
    async def save_routine(self, routine: Routine) -> Routine:
        ...

    @abstractmethod
    async def find_routine_by_id(self, routine_id: UUID) -> Optional[Routine]:
        ...

class TrainingAssignmentRepository(ABC):

    @abstractmethod
    async def save_assignment(self, assignment: RoutineAssignment) -> RoutineAssignment:
        ...

    @abstractmethod
    async def find_active_assignment(self, user_id: UUID) -> Optional[RoutineAssignment]:
        ...

    @abstractmethod
    async def find_completions_by_user(self, user_id: UUID, limit: int=50) -> List[WorkoutCompletion]:
        ...

    @abstractmethod
    async def save_completion(self, completion: WorkoutCompletion) -> WorkoutCompletion:
        ...
