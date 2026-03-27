from uuid import uuid4
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID
from ...domain.entities.training import Routine, RoutineExercise, RoutineAssignment, WorkoutCompletion
from ...infrastructure.repositories.sqlalchemy_training_repository import SQLAlchemyTrainingRepository
from ...infrastructure.repositories.sqlalchemy_training_assignment_repository import SQLAlchemyTrainingAssignmentRepository
from ..dtos.training_dtos import CreateRoutineRequest, UpdateRoutineRequest, RoutineResponse, RoutineExerciseDTO, AssignRoutineRequest, CompleteWorkoutRequest, WorkoutCompletionResponse

class TrainingUseCases:
    def __init__(self, routine_repo: SQLAlchemyTrainingRepository, assignment_repo: SQLAlchemyTrainingAssignmentRepository):
        self.routine_repo = routine_repo
        self.assignment_repo = assignment_repo

    async def create_routine(self, request: CreateRoutineRequest) -> RoutineResponse:
        routine = Routine(
            id=uuid4(),
            name=request.name,
            description=request.description,
            goal=request.goal,
            level=request.level,
            exercises=[
                RoutineExercise(exercise_id=e.exercise_id, sets=e.sets, reps=e.reps, rest_seconds=e.rest_seconds)
                for e in request.exercises
            ],
            creator_id=request.creator_id
        )
        await self.routine_repo.save_routine(routine)
        return self._map_to_response(routine, {})

    async def update_routine(self, routine_id: UUID, user_id: UUID, request: UpdateRoutineRequest, is_admin: bool = False) -> RoutineResponse:
        routine = await self.routine_repo.find_routine_by_id(routine_id)
        if not routine:
            raise ValueError("Routine not found")
        if not is_admin and str(routine.creator_id) != str(user_id):
            raise ValueError("Solo puedes editar tus propias rutinas")
        updated = Routine(
            id=routine.id,
            name=request.name,
            description=request.description,
            goal=request.goal,
            level=request.level,
            exercises=[
                RoutineExercise(exercise_id=e.exercise_id, sets=e.sets, reps=e.reps, rest_seconds=e.rest_seconds)
                for e in request.exercises
            ],
            creator_id=routine.creator_id,
        )
        await self.routine_repo.update_routine(updated)
        ids = [e.exercise_id for e in updated.exercises]
        names = await self.routine_repo.get_exercise_names(ids)
        return self._map_to_response(updated, names)

    async def delete_routine(self, routine_id: UUID, user_id: UUID, is_admin: bool = False) -> bool:
        routine = await self.routine_repo.find_routine_by_id(routine_id)
        if not routine:
            raise ValueError("Routine not found")
        if not is_admin and str(routine.creator_id) != str(user_id):
            raise ValueError("Solo puedes eliminar tus propias rutinas")
        return await self.routine_repo.delete_routine(routine_id)

    async def assign_routine(self, user_id: UUID, request: AssignRoutineRequest) -> bool:
        assignment = RoutineAssignment(
            user_id=user_id,
            routine_id=request.routine_id,
            assigned_at=datetime.utcnow(),
            is_active=True
        )
        await self.assignment_repo.save_assignment(assignment)
        return True

    async def get_active_routine(self, user_id: UUID) -> Optional[RoutineResponse]:
        assignment = await self.assignment_repo.find_active_assignment(user_id)
        if not assignment:
            return None
        routine = await self.routine_repo.find_routine_by_id(assignment.routine_id)
        if not routine:
            return None
        ids = [e.exercise_id for e in routine.exercises]
        names = await self.routine_repo.get_exercise_names(ids)
        return self._map_to_response(routine, names)

    async def list_routines_by_creator(self, creator_id: UUID) -> List[RoutineResponse]:
        routines = await self.routine_repo.find_routines_by_creator(creator_id)
        all_ids = []
        for r in routines:
            all_ids.extend(e.exercise_id for e in r.exercises)
        names = await self.routine_repo.get_exercise_names(list(set(all_ids))) if all_ids else {}
        return [self._map_to_response(r, names) for r in routines]

    async def complete_workout(self, user_id: UUID, request: CompleteWorkoutRequest) -> bool:
        assignment = await self.assignment_repo.find_active_assignment(user_id)
        if not assignment:
            raise ValueError("No active routine assigned")

        completion = WorkoutCompletion(
            id=uuid4(),
            user_id=user_id,
            routine_id=assignment.routine_id,
            completed_at=datetime.utcnow(),
            effort_level=request.effort_level,
            notes=request.notes
        )
        await self.assignment_repo.save_completion(completion)
        return True

    async def get_completions(self, user_id: UUID, limit: int = 50) -> List[WorkoutCompletionResponse]:
        completions = await self.assignment_repo.find_completions_by_user(user_id, limit=limit)
        return [
            WorkoutCompletionResponse(
                id=c.id,
                user_id=c.user_id,
                routine_id=c.routine_id,
                completed_at=c.completed_at,
                effort_level=c.effort_level,
                notes=c.notes,
            )
            for c in completions
        ]

    def _map_to_response(self, r: Routine, exercise_names: Optional[Dict[UUID, str]] = None) -> RoutineResponse:
        names = exercise_names or {}
        return RoutineResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            goal=r.goal,
            level=r.level,
            exercises=[
                RoutineExerciseDTO(
                    exercise_id=e.exercise_id,
                    exercise_name=names.get(e.exercise_id),
                    sets=e.sets,
                    reps=e.reps,
                    rest_seconds=e.rest_seconds
                )
                for e in r.exercises
            ],
            creator_id=r.creator_id
        )
