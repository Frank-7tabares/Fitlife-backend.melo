from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.instructor import Instructor, InstructorAssignment, InstructorRating

class InstructorRepository(ABC):

    @abstractmethod
    async def save(self, instructor: Instructor) -> Instructor:
        ...

    @abstractmethod
    async def find_by_id(self, instructor_id: UUID) -> Optional[Instructor]:
        ...

    @abstractmethod
    async def find_all(self) -> List[Instructor]:
        ...

    @abstractmethod
    async def update_rating_avg(self, instructor_id: UUID, new_avg: float) -> None:
        ...

class InstructorAssignmentRepository(ABC):

    @abstractmethod
    async def save(self, assignment: InstructorAssignment) -> InstructorAssignment:
        ...

    @abstractmethod
    async def find_active_by_user(self, user_id: UUID) -> Optional[InstructorAssignment]:
        ...

    @abstractmethod
    async def deactivate_active_for_user(self, user_id: UUID) -> None:
        ...

    @abstractmethod
    async def count_active_by_instructor(self, instructor_id: UUID) -> int:
        ...

class InstructorRatingRepository(ABC):

    @abstractmethod
    async def save(self, rating: InstructorRating) -> InstructorRating:
        ...

    @abstractmethod
    async def get_average_rating(self, instructor_id: UUID) -> Optional[float]:
        ...
