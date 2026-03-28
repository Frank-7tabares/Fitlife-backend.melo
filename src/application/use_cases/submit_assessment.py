from uuid import uuid4
from datetime import datetime
from ...domain.entities.assessment import Assessment
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.assessment_calculator import AssessmentCalculator
from ...domain.exceptions.user_exceptions import UserNotFoundException
from ...infrastructure.repositories.sqlalchemy_assessment_repository import SQLAlchemyAssessmentRepository
from ..dtos.assessment_dtos import SubmitAssessmentRequest, AssessmentResponse, BODY_AGE_DISCLAIMER

class SubmitAssessment:

    def __init__(self, repository: SQLAlchemyAssessmentRepository, user_repository: UserRepository):
        self.repository = repository
        self.user_repository = user_repository
        self.calculator = AssessmentCalculator()

    async def execute(self, request: SubmitAssessmentRequest) -> AssessmentResponse:
        user = await self.user_repository.find_by_id(request.user_id)
        if not user:
            raise UserNotFoundException(str(request.user_id))
        score = self.calculator.calculate_score(request.responses)
        category = self.calculator.determine_category(score)
        body_age = self.calculator.calculate_body_age(request.real_age, score)
        comparison = self.calculator.compare_body_age(request.real_age, body_age)
        assessment = Assessment(id=uuid4(), user_id=request.user_id, fitness_score=score, category=category, body_age=body_age, comparison=comparison, responses=request.responses, created_at=datetime.utcnow())
        await self.repository.save(assessment)
        return AssessmentResponse(id=assessment.id, user_id=assessment.user_id, fitness_score=assessment.fitness_score, category=assessment.category, body_age=assessment.body_age, comparison=assessment.comparison, responses=assessment.responses, created_at=assessment.created_at, body_age_disclaimer=BODY_AGE_DISCLAIMER)
