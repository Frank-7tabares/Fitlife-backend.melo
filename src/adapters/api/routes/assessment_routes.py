from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from ....infrastructure.database.connection import get_db
from ....infrastructure.repositories.sqlalchemy_assessment_repository import SQLAlchemyAssessmentRepository
from ....infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ....application.use_cases.submit_assessment import SubmitAssessment
from ....application.use_cases.get_assessment_history import GetAssessmentHistory
from ....application.dtos.assessment_dtos import SubmitAssessmentRequest, AssessmentResponse
from ....domain.exceptions.user_exceptions import UserNotFoundException

router = APIRouter(prefix="/assessments", tags=["Fitness Assessments"])

async def get_assessment_repository(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyAssessmentRepository(db)

async def get_user_repository(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyUserRepository(db)

@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def submit_assessment(
    request: SubmitAssessmentRequest,
    repo: SQLAlchemyAssessmentRepository = Depends(get_assessment_repository),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    use_case = SubmitAssessment(repo, user_repo)
    try:
        return await use_case.execute(request)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/user/{user_id}", response_model=List[AssessmentResponse])
async def get_history(
    user_id: UUID, 
    repo: SQLAlchemyAssessmentRepository = Depends(get_assessment_repository)
):
    use_case = GetAssessmentHistory(repo)
    return await use_case.execute(user_id)
