from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class PasswordHistory:
    id: UUID
    user_id: UUID
    password_hash: str
    changed_at: datetime
