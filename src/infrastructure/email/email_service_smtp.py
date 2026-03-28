import asyncio
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from ...config.settings import settings
logger = logging.getLogger(__name__)

def _send_password_reset_via_outbound(to_email: str, reset_token: str, user_name: str='') -> bool:
    from .email_outbound import send_password_reset_sync
    return send_password_reset_sync(to_email, reset_token, user_name)

def _normalize_app_password(raw: str) -> str:
    s = (raw or '').strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()
    return ''.join(s.split())

class SmtpEmailService:

    @staticmethod
    def _frontend_base_url() -> str:
        try:
            if hasattr(settings, 'cors_origins_list') and settings.cors_origins_list:
                return settings.cors_origins_list[0]
        except Exception:
            pass
        return settings.FRONTEND_URL

    @staticmethod
    def _send_password_reset_email_sync(to_email: str, reset_token: str, user_name: str='') -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Codigo para cambiar tu contrasena - FitLife'
            smtp_user = (getattr(settings, 'EMAIL_USER', None) or '').strip()
            from_addr = smtp_user or (getattr(settings, 'EMAIL_FROM', None) or '').strip()
            msg['From'] = formataddr(('FitLife', from_addr)) if from_addr else settings.EMAIL_FROM
            msg['To'] = to_email
            html = f"""\n            <html>\n              <body>\n                <h2>Hola {user_name or 'Usuario'},</h2>\n                <p>Recibimos una solicitud para cambiar tu contraseña.</p>\n                <p>Ingresa este codigo en la pantalla de recuperacion:</p>\n                <p>\n                  <span style="display:inline-block;background:#111;color:#CCFF00;padding:12px 18px;border-radius:8px;font-size:24px;font-weight:700;letter-spacing:3px;">\n                    {reset_token}\n                  </span>\n                </p>\n                <p>Este codigo expira en 1 hora.</p>\n                <p>Si no solicitaste este cambio, ignora este email.</p>\n                <p>Saludos,<br>El equipo de FitLife</p>\n              </body>\n            </html>\n            """
            msg.attach(MIMEText(html, 'html'))
            email_user = (getattr(settings, 'EMAIL_USER', None) or '').strip()
            email_password = _normalize_app_password((getattr(settings, 'EMAIL_PASSWORD', None) or '').strip())
            if not email_user or not email_password or 'your-' in email_user.lower() or ('your-' in email_password.lower()):
                raise RuntimeError('SMTP no configurado en el backend. Define EMAIL_USER y EMAIL_PASSWORD (App Password) en fitlife-backend-melo/.env')
            host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
            ports_to_try = [465, 587]
            port_setting = int(getattr(settings, 'EMAIL_PORT', 587))
            if port_setting in ports_to_try:
                ports_to_try = [port_setting] + [p for p in ports_to_try if p != port_setting]
            last_err = None
            for port in ports_to_try:
                try:
                    envelope_from = email_user
                    if port == 465:
                        context = ssl.create_default_context()
                        with smtplib.SMTP_SSL(host, port, context=context, timeout=20) as server:
                            server.login(email_user, email_password)
                            server.sendmail(envelope_from, [to_email], msg.as_string())
                    else:
                        server = smtplib.SMTP(host, port, timeout=20)
                        try:
                            server.ehlo()
                            server.starttls(context=ssl.create_default_context())
                            server.ehlo()
                            server.login(email_user, email_password)
                            server.sendmail(envelope_from, [to_email], msg.as_string())
                        finally:
                            server.quit()
                    logger.info(f'Email de restablecimiento enviado a {to_email} (puerto {port})')
                    return True
                except Exception as e:
                    last_err = e
                    print(f'[SMTP] Puerto {port} falló: {e}. Probando siguiente...', flush=True)
                    continue
            if last_err:
                hint = ''
                msg = str(last_err).lower()
                if '535' in msg or 'badcredentials' in msg:
                    hint = ' (Gmail: usa App Password con 2FA habilitado)'
                logger.error(f'Error al enviar email a {to_email}: {last_err}{hint}')
                raise RuntimeError(f'No se pudo enviar el email.{hint}'.strip())
            return False
        except Exception as e:
            hint = ''
            msg = str(e).lower()
            if '535' in msg or 'badcredentials' in msg:
                hint = ' (Sugerencia: si usas Gmail, configura EMAIL_PASSWORD como App Password y asegúrate de que la cuenta tenga 2FA habilitado.)'
            logger.error(f'Error al enviar email de restablecimiento a {to_email}: {str(e)}{hint}')
            raise RuntimeError(f'No se pudo enviar el email de restablecimiento.{hint}'.strip())

    @staticmethod
    async def send_password_reset_email(to_email: str, reset_token: str, user_name: str='') -> bool:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: _send_password_reset_via_outbound(to_email, reset_token, user_name))

    @staticmethod
    async def send_welcome_email(to_email: str, user_name: str) -> bool:
        try:
            login_url = f'{SmtpEmailService._frontend_base_url()}/auth/login'
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Bienvenido a FitLife'
            smtp_user = (getattr(settings, 'EMAIL_USER', None) or '').strip()
            from_addr = smtp_user or (getattr(settings, 'EMAIL_FROM', None) or '').strip()
            msg['From'] = formataddr(('FitLife', from_addr)) if from_addr else settings.EMAIL_FROM
            msg['To'] = to_email
            html = f'''\n            <html>\n              <body>\n                <h2>Hola {user_name or 'Usuario'},</h2>\n                <p>Bienvenido a FitLife.</p>\n                <p>Comienza creando tu evaluación física para obtener tu plan personalizado.</p>\n                <p>\n                  <a href="{login_url}" style="background-color: #CCFF00; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px;">\n                    Ir a iniciar sesión\n                  </a>\n                </p>\n                <p>Saludos,<br>El equipo de FitLife</p>\n              </body>\n            </html>\n            '''
            msg.attach(MIMEText(html, 'html'))
            email_user = (getattr(settings, 'EMAIL_USER', None) or '').strip()
            email_password = _normalize_app_password((getattr(settings, 'EMAIL_PASSWORD', None) or '').strip())
            if not email_user or not email_password or 'your-' in email_user.lower() or ('your-' in email_password.lower()):
                logger.warning('SMTP no configurado: EMAIL_USER/EMAIL_PASSWORD. Omite envío de bienvenida.')
                return False
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=20)
            try:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(email_user, email_password)
                server.sendmail(from_addr, [to_email], msg.as_string())
            finally:
                server.quit()
            logger.info(f'Email de bienvenida enviado a {to_email}')
            return True
        except Exception as e:
            hint = ''
            msg_str = str(e).lower()
            if '535' in msg_str or 'badcredentials' in msg_str:
                hint = ' (Gmail: usa App Password con 2FA.)'
            logger.error(f'Error al enviar email de bienvenida a {to_email}: {e}{hint}')
            return False
