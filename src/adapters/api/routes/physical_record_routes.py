from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....application.dtos.physical_record_dtos import (
    PhysicalRecordListResponse,
    PhysicalRecordRequest,
    PhysicalRecordResponse,
)
from ....application.use_cases.physical_record_use_cases import PhysicalRecordUseCases
from ....infrastructure.database.connection import get_db
from ....infrastructure.repositories.sqlalchemy_physical_record_repository import (
    SQLAlchemyPhysicalRecordRepository,
)

router = APIRouter(prefix="/users/{user_id}/physical-records", tags=["Physical Progress"])


async def get_use_cases(db: AsyncSession = Depends(get_db)) -> PhysicalRecordUseCases:
    repo = SQLAlchemyPhysicalRecordRepository(db)
    return PhysicalRecordUseCases(repo)


@router.post("", response_model=PhysicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    user_id: UUID,
    request: PhysicalRecordRequest,
    use_cases: PhysicalRecordUseCases = Depends(get_use_cases),
):
    return await use_cases.create_record(user_id, request)


@router.get("", response_model=PhysicalRecordListResponse)
async def get_history(
    user_id: UUID,
    use_cases: PhysicalRecordUseCases = Depends(get_use_cases),
):
    return await use_cases.get_history(user_id)
