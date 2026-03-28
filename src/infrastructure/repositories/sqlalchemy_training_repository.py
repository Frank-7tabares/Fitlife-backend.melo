from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.entities.training import Routine, RoutineExercise
from ..database.models.training_models import RoutineModel, ExerciseModel
from ..database.models.training_assignment_models import RoutineAssignmentModel, WorkoutCompletionModel

class SQLAlchemyTrainingRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_routine(self, routine: Routine) -> Routine:
        model = RoutineModel(id=str(routine.id), name=routine.name, description=routine.description, goal=routine.goal, level=routine.level, exercises_data=[{'exercise_id': str(e.exercise_id), 'sets': e.sets, 'reps': e.reps, 'rest_seconds': e.rest_seconds} for e in routine.exercises], creator_id=str(routine.creator_id))
        self.session.add(model)
        await self.session.commit()
        return routine

    async def find_routine_by_id(self, routine_id: UUID) -> Optional[Routine]:
        stmt = select(RoutineModel).where(RoutineModel.id == str(routine_id))
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        if not m:
            return None
        return self._to_entity(m)

    async def update_routine(self, routine: Routine) -> Routine:
        from sqlalchemy.orm.attributes import flag_modified
        stmt = select(RoutineModel).where(RoutineModel.id == str(routine.id))
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        if not m:
            return routine
        m.name = routine.name
        m.description = routine.description
        m.goal = routine.goal
        m.level = routine.level
        m.exercises_data = [{'exercise_id': str(e.exercise_id), 'sets': e.sets, 'reps': e.reps, 'rest_seconds': e.rest_seconds} for e in routine.exercises]
        flag_modified(m, 'exercises_data')
        await self.session.commit()
        return routine

    async def delete_routine(self, routine_id: UUID) -> bool:
        rid = str(routine_id)
        await self.session.execute(delete(RoutineAssignmentModel).where(RoutineAssignmentModel.routine_id == rid))
        await self.session.execute(delete(WorkoutCompletionModel).where(WorkoutCompletionModel.routine_id == rid))
        stmt = delete(RoutineModel).where(RoutineModel.id == rid)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def find_routines_by_creator(self, creator_id: UUID) -> List[Routine]:
        stmt = select(RoutineModel).where(RoutineModel.creator_id == str(creator_id)).order_by(RoutineModel.id.desc())
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def delete_routines_by_creator(self, creator_id: UUID) -> int:
        routines = await self.find_routines_by_creator(creator_id)
        for r in routines:
            await self.delete_routine(r.id)
        return len(routines)

    async def get_exercise_names(self, ids: List[UUID]) -> Dict[UUID, str]:
        if not ids:
            return {}
        stmt = select(ExerciseModel.id, ExerciseModel.name).where(ExerciseModel.id.in_([str(i) for i in ids]))
        result = await self.session.execute(stmt)
        return {UUID(row.id): row.name for row in result.all()}

    def _to_entity(self, m: RoutineModel) -> Routine:
        return Routine(id=UUID(m.id), name=m.name, description=m.description, goal=m.goal, level=m.level, exercises=[RoutineExercise(exercise_id=UUID(e['exercise_id']), sets=e['sets'], reps=e['reps'], rest_seconds=e['rest_seconds']) for e in m.exercises_data], creator_id=UUID(m.creator_id))
