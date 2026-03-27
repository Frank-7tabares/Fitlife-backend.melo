"""Caso de uso: obtener historial de auditoría del perfil (RF-036, RF-037)."""
from uuid import UUID
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.repositories.sqlalchemy_audit_repository import SQLAlchemyAuditRepository
from src.application.dtos.user_dtos import ProfileAuditHistoryResponse, ProfileAuditLogResponse

class GetProfileAudit:
    """Devuelve el historial de cambios en el perfil de un usuario.

    Requisitos:
    - RF-036: Registrar cambios de perfil
    - RF-037: Permitir acceso al historial (solo propietario o admin)
    """

    def __init__(self, user_repo: UserRepository, audit_repo: SQLAlchemyAuditRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def execute(self, user_id: UUID) -> ProfileAuditHistoryResponse:
        """Obtiene historial de auditoría del perfil.

        Args:
            user_id: ID del usuario

        Raises:
            ValueError: Si usuario no existe
        """
        # Validar que usuario existe
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Obtener logs de auditoría (la implementación depende del repositorio)
        logs = await self.audit_repo.get_logs_by_user_id(user_id)

        # Mapear a DTOs
        audit_responses = [
            ProfileAuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                changed_by=log.changed_by,
                changes=log.changes,
                timestamp=log.timestamp
            )
            for log in logs
        ]

        return ProfileAuditHistoryResponse(
            user_id=user_id,
            total=len(audit_responses),
            logs=audit_responses
        )
