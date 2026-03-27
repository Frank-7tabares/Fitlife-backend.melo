"""Rutas de administración: listar usuarios, eliminar usuario, verificar certificados, subir certificados (solo rol admin)."""
import uuid as uuid_mod
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ....infrastructure.database.connection import get_db
from ....infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ....infrastructure.repositories.sqlalchemy_instructor_repository import (
    SQLAlchemyInstructorRepository,
    SQLAlchemyInstructorAssignmentRepository,
    SQLAlchemyInstructorRatingRepository,
)
from ....infrastructure.repositories.sqlalchemy_training_repository import SQLAlchemyTrainingRepository
from ....infrastructure.repositories.sqlalchemy_training_assignment_repository import SQLAlchemyTrainingAssignmentRepository
from ....infrastructure.repositories.sqlalchemy_nutrition_repository import SQLAlchemyNutritionRepository
from ....infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
from ....application.use_cases.instructor_use_cases import InstructorUseCases
from ....application.dtos.instructor_dtos import VerifyCertificateRequest
from ..dependencies import get_current_admin, get_user_repository
from ....application.dtos.admin_dtos import AdminUserListItem, AdminUserUpdateRequest
from ....domain.entities.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["Admin"])


async def get_instructor_use_cases(db: AsyncSession = Depends(get_db)):
    return InstructorUseCases(
        SQLAlchemyInstructorRepository(db),
        SQLAlchemyInstructorAssignmentRepository(db),
        SQLAlchemyInstructorRatingRepository(db),
    )


@router.get("/users", response_model=list[AdminUserListItem])
async def list_users(
    _admin: User = Depends(get_current_admin),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    """Lista todos los usuarios del sistema (solo admin)."""
    users = await user_repo.find_all()
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


@router.patch("/users/{user_id}", response_model=AdminUserListItem)
async def update_user(
    user_id: UUID,
    request: AdminUserUpdateRequest,
    admin: User = Depends(get_current_admin),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    """Edita un usuario (solo admin): email, nombre, rol y estado."""
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    # Evita bloquear la cuenta admin actual por accidente
    if user_id == admin.id:
        if request.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propia cuenta",
            )
        if request.role is not None and request.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes cambiar tu propio rol",
            )

    if request.email is not None and request.email.lower().strip() != user.email.lower().strip():
        exists = await user_repo.exists_by_email(request.email)
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está en uso")
        user.email = request.email.lower().strip()

    if request.full_name is not None:
        name = request.full_name.strip()
        user.full_name = name if name else None

    if request.role is not None:
        user.role = request.role

    if request.is_active is not None:
        user.is_active = request.is_active

    updated = await user_repo.update(user)
    return AdminUserListItem(
        id=updated.id,
        email=updated.email,
        full_name=updated.full_name,
        role=updated.role,
        is_active=updated.is_active,
        created_at=updated.created_at,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Elimina un usuario (solo admin). Borra en cascada rutinas, asignaciones, planes y registro de instructor."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta",
        )
    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    training_repo = SQLAlchemyTrainingRepository(db)
    assignment_repo = SQLAlchemyTrainingAssignmentRepository(db)
    nutrition_repo = SQLAlchemyNutritionRepository(db)
    instructor_repo = SQLAlchemyInstructorRepository(db)
    audit_repo = SQLAlchemyAuditRepository(db)

    await training_repo.delete_routines_by_creator(user_id)
    await assignment_repo.delete_assignments_and_completions_by_user(user_id)
    await nutrition_repo.delete_plans_by_user_id(user_id)
    await audit_repo.delete_logs_involving_user(user_id)
    await instructor_repo.delete_by_id(user_id)
    await user_repo.delete_by_id(user_id)


@router.patch("/instructors/{instructor_id}/verify-certificate")
async def verify_instructor_certificate(
    instructor_id: UUID,
    request: VerifyCertificateRequest,
    _admin: User = Depends(get_current_admin),
    use_cases: InstructorUseCases = Depends(get_instructor_use_cases),
):
    """Verifica o rechaza el certificado profesional de un instructor (solo admin)."""
    try:
        await use_cases.verify_certificate(instructor_id, request.status)
        return {"message": f"Certificado {request.status}"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload-certificate")
async def upload_certificate(
    request: Request,
    file: UploadFile = File(...),
    _admin: User = Depends(get_current_admin),
):
    """Sube un certificado profesional (PDF o imagen). Devuelve la URL para crear instructor (solo admin)."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre de archivo vacío")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archivo demasiado grande (máx 5 MB)")
    upload_dir = Path("uploads/certificates")
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid_mod.uuid4().hex}{ext}"
    file_path = upload_dir / safe_name
    with open(file_path, "wb") as f:
        f.write(content)
    path = f"/api/v1/static/certificates/{safe_name}"
    base = str(request.base_url).rstrip("/")
    url = f"{base}{path}"
    return {"url": url}
