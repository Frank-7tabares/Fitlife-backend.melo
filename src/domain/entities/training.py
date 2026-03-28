from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import List, Optional

class FitnessLevel(str, Enum):
    BEGINNER = 'BEGINNER'
    INTERMEDIATE = 'INTERMEDIATE'
    ADVANCED = 'ADVANCED'

@dataclass
class Exercise:
    id: UUID
    name: str
    description: str
    muscle_group: str
    difficulty: str

@dataclass
class RoutineExercise:
    exercise_id: UUID
    sets: int
    reps: int
    rest_seconds: int

@dataclass
class Routine:
    id: UUID
    name: str
    description: str
    goal: str
    level: FitnessLevel
    exercises: List[RoutineExercise]
    creator_id: UUID

@dataclass
class RoutineAssignment:
    user_id: UUID
    routine_id: UUID
    assigned_at: datetime
    is_active: bool

@dataclass
class WorkoutCompletion:
    id: UUID
    user_id: UUID
    routine_id: UUID
    completed_at: datetime
    effort_level: int
    notes: Optional[str]
