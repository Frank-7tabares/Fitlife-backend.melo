import logging
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4
from datetime import datetime, timedelta
import secrets
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.password_reset_token_repository import PasswordResetTokenRepository
from ...domain.entities.password_reset_token import PasswordResetToken, ResetTokenStatus
from ..dtos.auth_dtos import PasswordResetRequestDto
from ...infrastructure.email.email_service_smtp import SmtpEmailService
from ...config.settings import settings
logger = logging.getLogger('fitlife.password_reset')

def _make_log_reset():

    def _write(status: str, detail: str):
        try:
            from datetime import datetime
            log_path = Path(__file__).resolve().parents[3] / 'backend_requests.log'
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f'{datetime.now().isoformat()} | [PasswordReset] {status}: {detail}\n')
        except Exception:
            pass
    return _write

async def _send_password_reset_email_safe(to_email: str, reset_token_value: str, user_name: str) -> bool:
    _log_reset = _make_log_reset()
    try:
        sent = await SmtpEmailService.send_password_reset_email(
            to_email=to_email, reset_token=reset_token_value, user_name=user_name
        )
        if sent:
            print(f'[PasswordReset] Email enviado a {to_email}', flush=True)
            _log_reset('EMAIL_ENVIADO', to_email)
            return True
        print('[PasswordReset] SmtpEmailService no pudo enviar', flush=True)
        _log_reset('EMAIL_NO_ENVIADO', 'SmtpEmailService retornó False')
        return False
    except Exception as e:
        print(f'[PasswordReset] Error enviando email: {e}', flush=True)
        _log_reset('EMAIL_ERROR', str(e))
        logger.exception('Password reset email failed')
        return False


class PasswordResetRequest:

    def __init__(self, user_repository: UserRepository, reset_token_repository: PasswordResetTokenRepository):
        self.user_repository = user_repository
        self.reset_token_repository = reset_token_repository

    async def execute(self, request: PasswordResetRequestDto, background_tasks: Optional[Any]=None) -> dict:
        email = str(request.email).strip().lower()
        user = await self.user_repository.find_by_email(email)
        found = 'sí' if user else 'NO'
        msg = f'[PasswordReset] email={email} usuario_en_bd={found}'
        print(msg, flush=True)
        logger.info(msg)
        if not user:
            warn = '[PasswordReset] No se envía correo: email NO registrado en la BD.'
            print(warn, flush=True)
            logger.warning(warn)
            _make_log_reset()('USUARIO_NO_ENCONTRADO', email)
        reset_token_value = f'{secrets.randbelow(1000000):06d}'
        expires_at = datetime.utcnow() + timedelta(hours=1)
        email_sent = False
        if user:
            reset_token = PasswordResetToken(id=uuid4(), user_id=user.id, token=reset_token_value, expires_at=expires_at, status=ResetTokenStatus.PENDING, created_at=datetime.utcnow())
            await self.reset_token_repository.save(reset_token)
            user_name = (user.full_name or 'Usuario').replace('"', "'").replace('\n', ' ')[:50]
            use_sync = bool(getattr(settings, 'PASSWORD_RESET_EMAIL_SYNC', False))
            if background_tasks is not None and not use_sync:
                print('[PasswordReset] Token guardado; correo SMTP en segundo plano (evita timeout en Render).', flush=True)
                background_tasks.add_task(_send_password_reset_email_safe, user.email, reset_token_value, user_name)
                email_sent = None
            else:
                print('[PasswordReset] Enviando correo (SMTP) en la misma petición (PASSWORD_RESET_EMAIL_SYNC o sin BackgroundTasks)…', flush=True)
                email_sent = await _send_password_reset_email_safe(user.email, reset_token_value, user_name)
        response = {'message': 'Si el email está registrado, recibirás un código de verificación para cambiar la contraseña.'}
        debug_data = {'user_found': bool(user)}
        if getattr(settings, 'DEBUG', False) and user:
            if email_sent is not None:
                debug_data['email_sent'] = email_sent
            elif background_tasks is not None and not use_sync:
                debug_data['email_queued'] = True
        response['debug'] = debug_data
        return response
