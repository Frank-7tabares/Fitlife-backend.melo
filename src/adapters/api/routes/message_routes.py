"""Rutas de API para mensajería (chat atleta-instructor)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.repositories.sqlalchemy_instructor_repository import (
    SQLAlchemyInstructorRepository,
    SQLAlchemyInstructorAssignmentRepository,
)
from src.application.use_cases.message_use_cases import (
    SendMessage,
    GetMessagesByUser,
    MarkMessageAsRead,
    GetConversation,
    MarkThreadRead,
    GetCoachInbox,
)
from src.application.dtos.message_dtos import (
    SendMessageRequest,
    MessageResponse,
    MessageListResponse,
    ConversationResponse,
    CoachInboxResponse,
)
from src.domain.entities.user import User, UserRole
from ..dependencies import get_current_user

router = APIRouter(prefix="/messages", tags=["Messaging"])


async def get_message_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyMessageRepository(db)


async def get_user_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyUserRepository(db)


async def get_instructor_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyInstructorRepository(db)


async def get_assignment_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyInstructorAssignmentRepository(db)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    message_repo: SQLAlchemyMessageRepository = Depends(get_message_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    instructor_repo: SQLAlchemyInstructorRepository = Depends(get_instructor_repo),
):
    """Envía un mensaje. El remitente es siempre el usuario autenticado."""
    use_case = SendMessage(message_repo, user_repo, instructor_repo)
    try:
        return await use_case.execute(current_user.id, request)
    except ValueError as e:
        msg = str(e).lower()
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "not assigned" in msg or "no puedes" in msg or "solo " in msg or "no tienes" in msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/inbox", response_model=CoachInboxResponse)
async def get_coach_inbox(
    current_user: User = Depends(get_current_user),
    message_repo: SQLAlchemyMessageRepository = Depends(get_message_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
    """Bandeja de conversaciones para instructor/admin (último mensaje y no leídos)."""
    use_case = GetCoachInbox(message_repo, user_repo)
    try:
        return await use_case.execute(current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/user/{user_id}", response_model=MessageListResponse)
async def get_user_messages(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    message_repo: SQLAlchemyMessageRepository = Depends(get_message_repo),
):
    """Bandeja de entrada (solo el propio usuario o admin)."""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    use_case = GetMessagesByUser(message_repo)
    return await use_case.execute(user_id, skip, limit)


@router.get("/conversation/{peer_id}", response_model=ConversationResponse)
async def get_conversation(
    peer_id: UUID,
    current_user: User = Depends(get_current_user),
    message_repo: SQLAlchemyMessageRepository = Depends(get_message_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    instructor_repo: SQLAlchemyInstructorRepository = Depends(get_instructor_repo),
    assignment_repo: SQLAlchemyInstructorAssignmentRepository = Depends(get_assignment_repo),
):
    """Historial de chat con otro usuario (atleta-instructor asignados o admin)."""
    use_case = GetConversation(message_repo, user_repo, instructor_repo, assignment_repo)
    try:
        return await use_case.execute(current_user, peer_id)
    except ValueError as e:
        msg = str(e).lower()
        if "no encontrado" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/conversation/{peer_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_conversation_read(
    peer_id: UUID,
    current_user: User = Depends(get_current_user),
    message_repo: SQLAlchemyMessageRepository = Depends(get_message_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    instructor_repo: SQLAlchemyInstructorRepository = Depends(get_instructor_repo),
    assignment_repo: SQLAlchemyInstructorAssignmentRepository = Depends(get_assignment_repo),
):
    """Marca como leídos los mensajes del peer hacia el usuario actual."""
    use_case = MarkThreadRead(message_repo, user_repo, instructor_repo, assignment_repo)
    try:
        await use_case.execute(current_user, peer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{message_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_message_as_read(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    message_repo: SQLAlchemyMessageRepository = Depends(get_message_repo),
):
    """Marca un mensaje como leído (solo el destinatario)."""
    msg = await message_repo.find_by_id(message_id)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado")
    if msg.recipient_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    use_case = MarkMessageAsRead(message_repo)
    await use_case.execute(message_id)
