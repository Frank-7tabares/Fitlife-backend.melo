from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from ...domain.entities.user import UserRole

class AdminUserListItem(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime

class AdminUserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
