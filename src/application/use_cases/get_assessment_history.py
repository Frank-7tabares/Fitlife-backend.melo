from typing import List
from uuid import UUID
from ...infrastructure.repositories.sqlalchemy_assessment_repository import SQLAlchemyAssessmentRepository
from ..dtos.assessment_dtos import AssessmentResponse, BODY_AGE_DISCLAIMER

class GetAssessmentHistory:

    def __init__(self, repository: SQLAlchemyAssessmentRepository):
        self.repository = repository

    async def execute(self, user_id: UUID) -> List[AssessmentResponse]:
        assessments = await self.repository.find_by_user_id(user_id)
        return [AssessmentResponse(id=a.id, user_id=a.user_id, fitness_score=a.fitness_score, category=a.category, body_age=a.body_age, comparison=a.comparison, responses=a.responses, created_at=a.created_at, body_age_disclaimer=BODY_AGE_DISCLAIMER) for a in assessments]
