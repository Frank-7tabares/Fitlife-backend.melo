"""Rutas de API para recordatorios (Historia 8 - Reminders, RF-095 a RF-100)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories.sqlalchemy_reminder_repository import SQLAlchemyReminderRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.application.use_cases.reminder_use_cases import (
    CreateReminder,
    GetRemindersByUser,
    GetReminderById,
    UpdateReminder,
    DeleteReminder,
)
from src.application.dtos.reminder_dtos import (
    CreateReminderRequest,
    UpdateReminderRequest,
    ReminderResponse,
    ReminderListResponse,
)

router = APIRouter(prefix="/reminders", tags=["Reminders"])


async def get_reminder_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyReminderRepository(db)


async def get_user_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyUserRepository(db)


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    user_id: UUID,
    request: CreateReminderRequest,
    reminder_repo: SQLAlchemyReminderRepository = Depends(get_reminder_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
    """Crea un nuevo recordatorio (RF-095 a RF-100).

    Requisitos:
    - Tipo de recordatorio obligatorio (RF-097)
    - Frecuencia configurable (RF-099)
    - Soporte de zona horaria (RF-100)
    - Formato HH:MM para hora programada (RF-100)
    """
    use_case = CreateReminder(reminder_repo, user_repo)
    try:
        return await use_case.execute(user_id, request)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/user/{user_id}", response_model=ReminderListResponse)
async def get_user_reminders(
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
    reminder_repo: SQLAlchemyReminderRepository = Depends(get_reminder_repo),
):
    """Obtiene recordatorios del usuario (RF-098).

    Requisitos:
    - Incluye conteo de recordatorios activos
    - Soporte para paginación
    - Ordenados por fecha de creación
    """
    use_case = GetRemindersByUser(reminder_repo)
    return await use_case.execute(user_id, skip, limit)


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    reminder_repo: SQLAlchemyReminderRepository = Depends(get_reminder_repo),
):
    """Obtiene un recordatorio específico."""
    use_case = GetReminderById(reminder_repo)
    try:
        return await use_case.execute(reminder_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    request: UpdateReminderRequest,
    reminder_repo: SQLAlchemyReminderRepository = Depends(get_reminder_repo),
):
    """Actualiza un recordatorio existente.

    Soporta actualizaciones parciales - solo los campos proporcionados se actualizan.
    """
    use_case = UpdateReminder(reminder_repo)
    try:
        return await use_case.execute(reminder_id, request)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: UUID,
    reminder_repo: SQLAlchemyReminderRepository = Depends(get_reminder_repo),
):
    """Elimina un recordatorio."""
    use_case = DeleteReminder(reminder_repo)
    try:
        await use_case.execute(reminder_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
