"""Envío de correos: Resend (HTTPS) si hay API key — necesario en Render (SMTP bloqueado). Si no, SMTP."""
from ...config.settings import settings
from .email_service_resend import ResendEmailService
from .email_service_smtp import SmtpEmailService


def send_password_reset_sync(to_email: str, reset_token: str, user_name: str='') -> bool:
    key = (getattr(settings, 'RESEND_API_KEY', None) or '').strip()
    if key:
        print('[Email] Enviando con Resend (HTTPS; Render no permite SMTP saliente).', flush=True)
        return ResendEmailService.send_password_reset_sync(to_email, reset_token, user_name)
    print('[Email] Enviando con SMTP (local / VPS con puertos 587/465 abiertos).', flush=True)
    return SmtpEmailService._send_password_reset_email_sync(to_email, reset_token, user_name)
