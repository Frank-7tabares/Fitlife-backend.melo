import logging
import httpx
from ...config.settings import settings

logger = logging.getLogger(__name__)


def _password_reset_html(user_name: str, reset_token: str) -> str:
    name = (user_name or 'Usuario').replace('<', '').replace('>', '')[:80]
    return f"""<html>
  <body>
    <h2>Hola {name},</h2>
    <p>Recibimos una solicitud para cambiar tu contraseña.</p>
    <p>Ingresa este codigo en la pantalla de recuperacion:</p>
    <p>
      <span style="display:inline-block;background:#111;color:#CCFF00;padding:12px 18px;border-radius:8px;font-size:24px;font-weight:700;letter-spacing:3px;">
        {reset_token}
      </span>
    </p>
    <p>Este codigo expira en 1 hora.</p>
    <p>Si no solicitaste este cambio, ignora este email.</p>
    <p>Saludos,<br>El equipo de FitLife</p>
  </body>
</html>"""


class ResendEmailService:

    @staticmethod
    def send_password_reset_sync(to_email: str, reset_token: str, user_name: str='') -> bool:
        api_key = (getattr(settings, 'RESEND_API_KEY', None) or '').strip()
        if not api_key:
            raise RuntimeError('RESEND_API_KEY no está definida')
        from_raw = (getattr(settings, 'RESEND_FROM', None) or '').strip() or (getattr(settings, 'EMAIL_FROM', None) or '').strip()
        if not from_raw or 'your-' in from_raw.lower():
            raise RuntimeError(
                'Define RESEND_FROM o EMAIL_FROM con un remitente verificado en Resend (ej: onboarding@resend.dev o tu dominio).'
            )
        from_header = from_raw if '<' in from_raw else f'FitLife <{from_raw}>'
        payload = {
            'from': from_header,
            'to': [to_email],
            'subject': 'Codigo para cambiar tu contrasena - FitLife',
            'html': _password_reset_html(user_name, reset_token),
        }
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                'https://api.resend.com/emails',
                json=payload,
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            )
        if r.status_code >= 400:
            detail = (r.text or '')[:500]
            logger.error('Resend HTTP %s: %s', r.status_code, detail)
            raise RuntimeError(f'Resend rechazó el envío ({r.status_code}): {detail}')
        logger.info('Email de restablecimiento enviado vía Resend a %s', to_email)
        return True
