from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from ...domain.entities.training import FitnessLevel

class RoutineExerciseDTO(BaseModel):
    exercise_id: UUID
    exercise_name: Optional[str] = None
    sets: int = Field(..., gt=0)
    reps: int = Field(..., gt=0)
    rest_seconds: int = Field(..., ge=0)

class CreateRoutineRequest(BaseModel):
    name: str
    description: str
    goal: str
    level: FitnessLevel
    exercises: List[RoutineExerciseDTO]
    creator_id: UUID

class RoutineResponse(BaseModel):
    id: UUID
    name: str
    description: str
    goal: str
    level: FitnessLevel
    exercises: List[RoutineExerciseDTO]
    creator_id: UUID

class UpdateRoutineRequest(BaseModel):
    name: str
    description: str
    goal: str
    level: FitnessLevel
    exercises: List[RoutineExerciseDTO]

class AssignRoutineRequest(BaseModel):
    routine_id: UUID

class CompleteWorkoutRequest(BaseModel):
    effort_level: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None

class WorkoutCompletionResponse(BaseModel):
    id: UUID
    user_id: UUID
    routine_id: UUID
    completed_at: datetime
    effort_level: int
    notes: Optional[str] = None
