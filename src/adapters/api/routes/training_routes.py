from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from ....infrastructure.database.connection import get_db
from ....infrastructure.repositories.sqlalchemy_training_repository import SQLAlchemyTrainingRepository
from ....infrastructure.repositories.sqlalchemy_training_assignment_repository import SQLAlchemyTrainingAssignmentRepository
from ....application.use_cases.training_use_cases import TrainingUseCases
from ....application.dtos.training_dtos import CreateRoutineRequest, UpdateRoutineRequest, RoutineResponse, AssignRoutineRequest, CompleteWorkoutRequest, WorkoutCompletionResponse
from ....infrastructure.database.models.training_models import ExerciseModel
from sqlalchemy import select
from ..dependencies import get_current_user, get_current_instructor
from ....domain.entities.user import User

router = APIRouter(prefix="", tags=["Training & Routines"])

async def get_use_cases(db: AsyncSession = Depends(get_db)):
    routine_repo = SQLAlchemyTrainingRepository(db)
    assignment_repo = SQLAlchemyTrainingAssignmentRepository(db)
    return TrainingUseCases(routine_repo, assignment_repo)

@router.get("/training/routines", response_model=List[RoutineResponse])
async def list_routines_by_creator(
    creator_id: UUID = Query(..., description="ID del instructor que creó las rutinas"),
    current_user: User = Depends(get_current_instructor),
    use_cases: TrainingUseCases = Depends(get_use_cases),
):
    """Lista rutinas creadas por un instructor. Solo ese instructor o admin puede ver."""
    if current_user.role.value != "ADMIN" and str(current_user.id) != str(creator_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes listar tus propias rutinas")
    return await use_cases.list_routines_by_creator(creator_id)

@router.get("/exercises")
async def list_exercises(db: AsyncSession = Depends(get_db)):
    """Lista todos los ejercicios disponibles para crear rutinas."""
    stmt = select(ExerciseModel).order_by(ExerciseModel.name)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [{"id": str(r.id), "name": r.name, "description": r.description or "", "muscle_group": r.muscle_group or "", "difficulty": r.difficulty or ""} for r in rows]

@router.post("/training/routines", response_model=RoutineResponse, status_code=status.HTTP_201_CREATED)
async def create_routine(
    request: CreateRoutineRequest,
    current_user: User = Depends(get_current_instructor),
    use_cases: TrainingUseCases = Depends(get_use_cases),
):
    """Crea una rutina. Solo instructor o admin. creator_id debe ser el usuario actual (o cualquier si admin)."""
    if current_user.role.value != "ADMIN" and str(request.creator_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes crear rutinas como tú mismo")
    return await use_cases.create_routine(request)

@router.put("/training/routines/{routine_id}", response_model=RoutineResponse)
async def update_routine(
    routine_id: UUID,
    request: UpdateRoutineRequest,
    current_user: User = Depends(get_current_instructor),
    use_cases: TrainingUseCases = Depends(get_use_cases),
):
    """Edita una rutina. Solo el creador o admin."""
    try:
        return await use_cases.update_routine(routine_id, current_user.id, request, is_admin=(current_user.role.value == "ADMIN"))
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/training/routines/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routine(
    routine_id: UUID,
    current_user: User = Depends(get_current_instructor),
    use_cases: TrainingUseCases = Depends(get_use_cases),
):
    """Elimina una rutina. Solo el creador o admin."""
    try:
        ok = await use_cases.delete_routine(routine_id, current_user.id, is_admin=(current_user.role.value == "ADMIN"))
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routine not found")
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.post("/users/{user_id}/routines/assign")
async def assign_routine(
    user_id: UUID,
    request: AssignRoutineRequest,
    _current_user: User = Depends(get_current_instructor),
    use_cases: TrainingUseCases = Depends(get_use_cases),
):
    await use_cases.assign_routine(user_id, request)
    return {"message": "Routine assigned successfully"}

@router.get("/users/{user_id}/routines/active", response_model=Optional[RoutineResponse])
async def get_active_routine(user_id: UUID, use_cases: TrainingUseCases = Depends(get_use_cases)):
    routine = await use_cases.get_active_routine(user_id)
    if not routine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active routine found")
    return routine

@router.post("/workouts/complete")
async def complete_workout(user_id: UUID, request: CompleteWorkoutRequest, use_cases: TrainingUseCases = Depends(get_use_cases)):
    try:
        await use_cases.complete_workout(user_id, request)
        return {"message": "Workout completed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/users/{user_id}/workouts/completions", response_model=List[WorkoutCompletionResponse])
async def get_user_completions(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    use_cases: TrainingUseCases = Depends(get_use_cases),
):
    """Lista entrenamientos completados del usuario. Solo puede ver los propios (o admin/instructor cualquier usuario)."""
    if current_user.role.value not in ("ADMIN", "INSTRUCTOR") and str(current_user.id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes ver tu propio progreso")
    return await use_cases.get_completions(user_id, limit=limit)
