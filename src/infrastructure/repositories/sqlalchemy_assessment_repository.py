from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.entities.assessment import Assessment
from ..database.models.assessment_model import AssessmentModel

class SQLAlchemyAssessmentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, assessment: Assessment) -> Assessment:
        model = AssessmentModel(id=str(assessment.id), user_id=str(assessment.user_id), fitness_score=assessment.fitness_score, category=assessment.category, body_age=assessment.body_age, comparison=assessment.comparison, responses=assessment.responses, created_at=assessment.created_at)
        self.session.add(model)
        await self.session.commit()
        return assessment

    async def find_by_user_id(self, user_id: UUID) -> List[Assessment]:
        stmt = select(AssessmentModel).where(AssessmentModel.user_id == str(user_id)).order_by(AssessmentModel.created_at.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._map_to_entity(m) for m in models]

    def _map_to_entity(self, m: AssessmentModel) -> Assessment:
        return Assessment(id=UUID(m.id), user_id=UUID(m.user_id), fitness_score=m.fitness_score, category=m.category, body_age=m.body_age, comparison=m.comparison, responses=m.responses, created_at=m.created_at)
