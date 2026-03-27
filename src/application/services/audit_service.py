"""Servicio de aplicación: Auditoría de cambios en perfiles."""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any, List

from ...domain.entities.audit import ProfileAuditLog
from ...infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository


class AuditService:
    """Registra y consulta el historial de cambios en perfiles de usuario."""

    def __init__(self, audit_repository: SQLAlchemyAuditRepository):
        self.audit_repository = audit_repository

    async def log_profile_change(
        self,
        user_id: UUID,
        changed_by: UUID,
        changes: Dict[str, Any],
    ) -> ProfileAuditLog:
        """Registra un cambio en el perfil de usuario."""
        log = ProfileAuditLog(
            id=uuid4(),
            user_id=user_id,
            changed_by=changed_by,
            changes=changes,
            timestamp=datetime.utcnow(),
        )
        return await self.audit_repository.save_log(log)

    async def get_audit_history(self, user_id: UUID) -> List[ProfileAuditLog]:
        """Obtiene el historial de auditoría de un usuario."""
        return await self.audit_repository.get_logs_by_user_id(user_id)

    @staticmethod
    def compute_changes(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula los campos que cambiaron entre dos snapshots de perfil."""
        return {
            key: {"old": old.get(key), "new": new.get(key)}
            for key in new
            if new.get(key) != old.get(key)
        }
