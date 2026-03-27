from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
from src.application.use_cases.update_profile import UpdateProfile
from src.application.use_cases.get_profile_audit import GetProfileAudit
from src.application.dtos.user_dtos import (
    UpdateProfileRequest,
    UserProfileResponse,
    ProfileAuditHistoryResponse,
    ActiveInstructorResponse,
)
from src.application.use_cases.get_assessment_history import GetAssessmentHistory
from src.application.dtos.assessment_dtos import AssessmentResponse
from src.infrastructure.repositories.sqlalchemy_assessment_repository import SQLAlchemyAssessmentRepository
from src.application.dtos.instructor_dtos import AssignInstructorRequest
from src.application.dtos.admin_dtos import AdminUserListItem
from src.domain.entities.user import UserRole, User
from src.application.use_cases.message_use_cases import (
    resolve_coach_user_id_for_profile,
    coach_owns_assignment,
)
from .assessment_routes import get_assessment_repository
from .instructor_routes import get_instructor_use_cases
from src.application.use_cases.instructor_use_cases import InstructorUseCases
from ..dependencies import get_current_instructor, get_user_repository, get_current_user
from src.infrastructure.repositories.sqlalchemy_instructor_repository import (
    SQLAlchemyInstructorRepository,
    SQLAlchemyInstructorAssignmentRepository,
)
from src.infrastructure.repositories.sqlalchemy_message_repository import SQLAlchemyMessageRepository
from src.infrastructure.database.models.instructor_models import InstructorAssignmentModel

router = APIRouter(prefix="/users", tags=["Users & Profiles"])

async def get_repos(db: AsyncSession = Depends(get_db)):
    user_repo = SQLAlchemyUserRepository(db)
    audit_repo = SQLAlchemyAuditRepository(db)
    return user_repo, audit_repo


@router.get("/me/active-instructor", response_model=ActiveInstructorResponse)
async def get_my_active_instructor(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Instructor activo del atleta (mismo id de usuario que fila `instructors` si se registró como coach)."""
    if current_user.role != UserRole.USER:
        return ActiveInstructorResponse()
    user_repo = SQLAlchemyUserRepository(db)
    assignment_repo = SQLAlchemyInstructorAssignmentRepository(db)
    asn = await assignment_repo.find_active_by_user(current_user.id)

    # Caso normal: hay asignación activa.
    if asn:
        inst_repo = SQLAlchemyInstructorRepository(db)
        model = await inst_repo.find_by_id(asn.instructor_id)
        name = model.name if model else None
        messaging_uid = await resolve_coach_user_id_for_profile(
            asn.instructor_id, user_repo, inst_repo
        )
        return ActiveInstructorResponse(
            instructor_id=asn.instructor_id,
            instructor_name=name,
            messaging_user_id=messaging_uid,
        )

    # Fallback: si no hay asignación activa, pero sí mensajes, inferimos el coach
    # desde el emisor más reciente que tenga rol INSTRUCTOR.
    msg_repo = SQLAlchemyMessageRepository(db)
    recent_msgs = await msg_repo.get_by_recipient(current_user.id, limit=20)
    inst_repo = SQLAlchemyInstructorRepository(db)
    for msg in recent_msgs:
        if msg.sender_id == current_user.id:
            continue
        sender = await user_repo.find_by_id(msg.sender_id)
        if sender and sender.role == UserRole.INSTRUCTOR:
            model = await inst_repo.find_by_id(sender.id)
            name = model.name if model else (sender.full_name or sender.email)
            return ActiveInstructorResponse(
                instructor_id=sender.id,
                instructor_name=name,
                messaging_user_id=sender.id,
            )

    return ActiveInstructorResponse()


@router.get("/clients", response_model=List[AdminUserListItem])
async def list_clients(
    _current_user = Depends(get_current_instructor),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    """Lista atletas (usuarios con rol USER). Solo instructor o admin."""
    users = await user_repo.find_by_role(UserRole.USER.value)
    return [
        AdminUserListItem(id=u.id, email=u.email, full_name=u.full_name, role=u.role, is_active=u.is_active, created_at=u.created_at)
        for u in users
    ]


@router.get("/clients/assigned", response_model=List[AdminUserListItem])
async def list_assigned_clients(
    current_user: User = Depends(get_current_user),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    db: AsyncSession = Depends(get_db),
):
    """Lista atletas asignados al instructor actual (para chat). Admin ve todos los USER."""
    if current_user.role == UserRole.ADMIN:
        users = await user_repo.find_by_role(UserRole.USER.value)
        return [
            AdminUserListItem(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at,
            )
            for u in users
        ]
    if current_user.role != UserRole.INSTRUCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo instructores")
    inst_repo = SQLAlchemyInstructorRepository(db)
    stmt = select(
        InstructorAssignmentModel.user_id,
        InstructorAssignmentModel.instructor_id,
    ).where(InstructorAssignmentModel.is_active.is_(True))
    res = await db.execute(stmt)
    rows = res.fetchall()
    coach_key = str(current_user.id).strip().lower()

    def _parse_uuid(val: object) -> UUID:
        return UUID(str(val).strip())

    profile_ids = {_parse_uuid(r[1]) for r in rows}
    owns_cache: dict[UUID, bool] = {}
    for pid in profile_ids:
        if str(pid).lower() == coach_key:
            owns_cache[pid] = True
        else:
            owns_cache[pid] = await coach_owns_assignment(
                pid, current_user.id, user_repo, inst_repo
            )
    seen: set[UUID] = set()
    user_ids: List[UUID] = []
    for uid_str, iid_str in rows:
        pid = _parse_uuid(iid_str)
        if not owns_cache[pid]:
            continue
        uid = _parse_uuid(uid_str)
        if uid not in seen:
            seen.add(uid)
            user_ids.append(uid)
    out: List[AdminUserListItem] = []
    for uid in user_ids:
        u = await user_repo.find_by_id(uid)
        if u:
            out.append(
                AdminUserListItem(
                    id=u.id,
                    email=u.email,
                    full_name=u.full_name,
                    role=u.role,
                    is_active=u.is_active,
                    created_at=u.created_at,
                )
            )
    return out

@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_profile(user_id: UUID, repos: tuple = Depends(get_repos)):
    user_repo, _ = repos
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        version=user.version,
        created_at=user.created_at,
        age=user.age,
        gender=user.gender,
        height=user.height,
        fitness_goal=user.fitness_goal,
        activity_level=user.activity_level
    )

@router.patch("/{user_id}/profile", response_model=UserProfileResponse)
async def update_profile(
    user_id: UUID, 
    request: UpdateProfileRequest, 
    repos: tuple = Depends(get_repos)
):
    user_repo, audit_repo = repos
    use_case = UpdateProfile(user_repo, audit_repo)
    try:
        # In a real app, 'changed_by' would come from the JWT token
        return await use_case.execute(user_id, user_id, request)
    except ValueError as e:
        if "Concurrency conflict" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{user_id}/profile/audit", response_model=ProfileAuditHistoryResponse)
async def get_profile_audit(user_id: UUID, repos: tuple = Depends(get_repos)):
    """Obtiene el historial de cambios del perfil (RF-036, RF-037)."""
    user_repo, audit_repo = repos
    use_case = GetProfileAudit(user_repo, audit_repo)
    try:
        return await use_case.execute(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{user_id}/assessments", response_model=List[AssessmentResponse])
async def get_user_assessments(
    user_id: UUID,
    repo: SQLAlchemyAssessmentRepository = Depends(get_assessment_repository),
):
    """Historial de evaluaciones del usuario (alias spec: GET /users/{id}/assessments)."""
    use_case = GetAssessmentHistory(repo)
    return await use_case.execute(user_id)


@router.post("/{user_id}/assign-instructor")
async def assign_instructor(
    user_id: UUID,
    request: AssignInstructorRequest,
    use_cases: InstructorUseCases = Depends(get_instructor_use_cases),
):
    """Asigna un instructor al usuario. Desactiva la asignación anterior si existe (Historia 3)."""
    try:
        await use_cases.assign_instructor(user_id, request)
        return {"message": "Instructor assigned successfully"}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
