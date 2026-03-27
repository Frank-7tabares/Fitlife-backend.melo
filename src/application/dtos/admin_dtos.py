"""DTOs para endpoints de administración (solo admin)."""
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from ...domain.entities.user import UserRole


class AdminUserListItem(BaseModel):
    """Elemento de lista de usuarios para el panel admin."""
    id: UUID
    email: str
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime


class AdminUserUpdateRequest(BaseModel):
    """Campos editables por admin en gestión de usuarios."""
    email: EmailStr | None = None
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
