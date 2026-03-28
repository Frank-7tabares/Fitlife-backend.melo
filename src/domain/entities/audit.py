from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Dict, Any

@dataclass
class ProfileAuditLog:
    id: UUID
    user_id: UUID
    changed_by: UUID
    changes: Dict[str, Any]
    timestamp: datetime
