"""Caso de uso: solicitar restablecimiento de contraseña (RF-012 a RF-014, RF-024)."""
import logging
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta
import secrets
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.password_reset_token_repository import PasswordResetTokenRepository
from ...domain.entities.password_reset_token import PasswordResetToken, ResetTokenStatus
from ..dtos.auth_dtos import PasswordResetRequestDto
from ...infrastructure.email.email_service_smtp import SmtpEmailService
from ...config.settings import settings

logger = logging.getLogger("fitlife.password_reset")


def _make_log_reset():
    """Escribe en backend_requests.log para diagnosticar envío de email."""
    def _write(status: str, detail: str):
        try:
            from datetime import datetime
            log_path = Path(__file__).resolve().parents[3] / "backend_requests.log"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | [PasswordReset] {status}: {detail}\n")
        except Exception:
            pass
    return _write


def _reset_link_for_logs(reset_token_value: str) -> str:
    base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    try:
        if hasattr(settings, "cors_origins_list") and settings.cors_origins_list:
            base = settings.cors_origins_list[0]
    except Exception:
        pass
    return f"{base.rstrip('/')}/auth/reset-password?token={reset_token_value}"


class PasswordResetRequest:
    """Genera token de restablecimiento y envía por email.
    
    Notas:
    - Token válido 1 hora (RF-016)
    - Respuesta genérica aunque email no exista (RF-024: prevenir enumeración)
    - Rate limiting debe implementarse a nivel de ruta (3/hora por email, RF-023)
    """

    def __init__(
        self,
        user_repository: UserRepository,
        reset_token_repository: PasswordResetTokenRepository,
    ):
        self.user_repository = user_repository
        self.reset_token_repository = reset_token_repository

    async def execute(self, request: PasswordResetRequestDto) -> dict:
        """Ejecuta solicitud de restablecimiento.
        
        Retorna respuesta genérica independientemente de si usuario existe.
        """
        # Normalizamos email para evitar problemas de mayúsculas/minúsculas.
        email = str(request.email).strip().lower()

        # Buscar usuario (silenciosamente, sin revelar si existe)
        user = await self.user_repository.find_by_email(email)
        found = "sí" if user else "NO"
        msg = f"[PasswordReset] email={email} usuario_en_bd={found}"
        print(msg, flush=True)
        logger.info(msg)
        if not user:
            warn = "[PasswordReset] No se envía correo: email NO registrado en la BD."
            print(warn, flush=True)
            logger.warning(warn)
            _make_log_reset()("USUARIO_NO_ENCONTRADO", email)

        # Generar código OTP de 6 dígitos (válido 1 hora)
        reset_token_value = f"{secrets.randbelow(1000000):06d}"
        expires_at = datetime.utcnow() + timedelta(hours=1)  # RF-016: 1 hora
        
        # Si usuario existe, guardar token y enviar email
        reset_link = None
        email_sent = False
        if user:
            reset_token = PasswordResetToken(
                id=uuid4(),
                user_id=user.id,
                token=reset_token_value,
                expires_at=expires_at,
                status=ResetTokenStatus.PENDING,
                created_at=datetime.utcnow(),
            )
            await self.reset_token_repository.save(reset_token)
            reset_link = _reset_link_for_logs(reset_token_value)

            # Enviar email con SmtpEmailService (directo, más fiable que subprocess)
            user_name = (user.full_name or "Usuario").replace('"', "'").replace("\n", " ")[:50]
            _log_reset = _make_log_reset()
            try:
                sent = await SmtpEmailService.send_password_reset_email(
                    to_email=user.email,
                    reset_token=reset_token_value,
                    user_name=user_name,
                )
                if sent:
                    print(f"[PasswordReset] Email enviado a {user.email}", flush=True)
                    _log_reset("EMAIL_ENVIADO", user.email)
                    email_sent = True
                else:
                    print("[PasswordReset] SmtpEmailService no pudo enviar", flush=True)
                    _log_reset("EMAIL_NO_ENVIADO", "SmtpEmailService retornó False")
            except Exception as e:
                print(f"[PasswordReset] Error enviando email: {e}", flush=True)
                _log_reset("EMAIL_ERROR", str(e))

        # Respuesta genérica (sin exponer código)
        response = {
            "message": "Si el email está registrado, recibirás un código de verificación para cambiar la contraseña.",
        }
        debug_data = {"user_found": bool(user), "_backend": "fitlife-local"}
        if getattr(settings, "DEBUG", False) and user:
            debug_data["email_sent"] = email_sent
        response["debug"] = debug_data
        return response
