from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.entities.training import RoutineAssignment, WorkoutCompletion
from ..database.models.training_assignment_models import RoutineAssignmentModel, WorkoutCompletionModel

class SQLAlchemyTrainingAssignmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_assignment(self, assignment: RoutineAssignment) -> RoutineAssignment:
        # Check if there's an active assignment and deactivate it
        stmt = update(RoutineAssignmentModel).where(
            RoutineAssignmentModel.user_id == str(assignment.user_id),
            RoutineAssignmentModel.is_active == True
        ).values(is_active=False)
        await self.session.execute(stmt)

        model = RoutineAssignmentModel(
            user_id=str(assignment.user_id),
            routine_id=str(assignment.routine_id),
            assigned_at=assignment.assigned_at,
            is_active=True
        )
        self.session.add(model)
        await self.session.commit()
        return assignment

    async def delete_assignments_and_completions_by_user(self, user_id: UUID) -> None:
        """Elimina asignaciones y completados de rutinas de un usuario (para eliminar usuario)."""
        uid = str(user_id)
        await self.session.execute(delete(WorkoutCompletionModel).where(WorkoutCompletionModel.user_id == uid))
        await self.session.execute(delete(RoutineAssignmentModel).where(RoutineAssignmentModel.user_id == uid))
        await self.session.commit()

    async def find_active_assignment(self, user_id: UUID) -> Optional[RoutineAssignment]:
        stmt = select(RoutineAssignmentModel).where(
            RoutineAssignmentModel.user_id == str(user_id),
            RoutineAssignmentModel.is_active == True
        )
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        if not m:
            return None
        return RoutineAssignment(
            user_id=UUID(m.user_id),
            routine_id=UUID(m.routine_id),
            assigned_at=m.assigned_at,
            is_active=m.is_active
        )

    async def find_completions_by_user(self, user_id: UUID, limit: int = 50) -> List[WorkoutCompletion]:
        stmt = (
            select(WorkoutCompletionModel)
            .where(WorkoutCompletionModel.user_id == str(user_id))
            .order_by(WorkoutCompletionModel.completed_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [
            WorkoutCompletion(
                id=UUID(r.id),
                user_id=UUID(r.user_id),
                routine_id=UUID(r.routine_id),
                completed_at=r.completed_at,
                effort_level=r.effort_level,
                notes=r.notes,
            )
            for r in rows
        ]

    async def save_completion(self, completion: WorkoutCompletion) -> WorkoutCompletion:
        model = WorkoutCompletionModel(
            id=str(completion.id),
            user_id=str(completion.user_id),
            routine_id=str(completion.routine_id),
            completed_at=completion.completed_at,
            effort_level=completion.effort_level,
            notes=completion.notes
        )
        self.session.add(model)
        await self.session.commit()
        return completion
