from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional

class ResetTokenStatus(str, Enum):
    PENDING = 'PENDING'
    USED = 'USED'
    EXPIRED = 'EXPIRED'

@dataclass
class PasswordResetToken:
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    status: ResetTokenStatus
    created_at: datetime
    used_at: Optional[datetime] = None
