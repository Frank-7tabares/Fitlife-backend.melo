"""Rutas de instructores (Historia 3): GET /instructors, GET /instructors/{id}, POST /users/{id}/assign-instructor, POST /instructors/{id}/rate."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from ....infrastructure.database.connection import get_db
from ....infrastructure.repositories.sqlalchemy_instructor_repository import (
    SQLAlchemyInstructorRepository,
    SQLAlchemyInstructorAssignmentRepository,
    SQLAlchemyInstructorRatingRepository,
)
from ....application.use_cases.instructor_use_cases import InstructorUseCases
from ....application.dtos.instructor_dtos import (
    InstructorResponse,
    CreateInstructorRequest,
    AssignInstructorRequest,
    RateInstructorRequest,
)
from ..dependencies import get_current_admin
from ....domain.entities.user import User

router = APIRouter(prefix="/instructors", tags=["Instructors"])


async def get_instructor_use_cases(db: AsyncSession = Depends(get_db)):
    return InstructorUseCases(
        SQLAlchemyInstructorRepository(db),
        SQLAlchemyInstructorAssignmentRepository(db),
        SQLAlchemyInstructorRatingRepository(db),
    )


@router.post("", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED)
async def create_instructor(
    request: CreateInstructorRequest,
    _admin: User = Depends(get_current_admin),
    use_cases: InstructorUseCases = Depends(get_instructor_use_cases),
):
    """Crea un instructor (solo admin). Requiere certificate_url para verificación de profesional."""
    return await use_cases.create_instructor(
        name=request.name,
        certifications=request.certifications,
        specializations=request.specializations,
        certificate_url=request.certificate_url,
    )


@router.get("", response_model=List[InstructorResponse])
async def list_instructors(
    use_cases: InstructorUseCases = Depends(get_instructor_use_cases),
):
    """Lista todos los instructores con nombre, certificaciones, calificación y conteo de usuarios activos."""
    return await use_cases.list_instructors()


@router.get("/{instructor_id}", response_model=InstructorResponse)
async def get_instructor(
    instructor_id: UUID,
    use_cases: InstructorUseCases = Depends(get_instructor_use_cases),
):
    """Detalle de un instructor."""
    instructor = await use_cases.get_instructor_by_id(instructor_id)
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found")
    return instructor


@router.post("/{instructor_id}/rate")
async def rate_instructor(
    instructor_id: UUID,
    request: RateInstructorRequest,
    use_cases: InstructorUseCases = Depends(get_instructor_use_cases),
    user_id: Optional[UUID] = Query(None, description="En producción debe venir del JWT"),
):
    """Califica al instructor (solo si el usuario está asignado a ese instructor). RF-048, RF-050."""
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required (user_id from JWT in production)",
        )
    try:
        await use_cases.rate_instructor(user_id, instructor_id, request)
        return {"message": "Rating submitted successfully"}
    except ValueError as e:
        if "not assigned" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
