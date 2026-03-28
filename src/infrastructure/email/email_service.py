import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ...config.settings import settings
import logging
logger = logging.getLogger(__name__)

class EmailService:

    @staticmethod
    async def send_password_reset_email(to_email: str, reset_token: str, user_name: str='') -> bool:
        try:
            reset_url = f'{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}'
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Restablece tu contraseña en FitLife'
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = to_email
            html = f'''\n            <html>\n              <body>\n                <h2>Hola {user_name or 'Usuario'},</h2>\n                <p>Recibimos una solicitud para restablecer tu contraseña.</p>\n                <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>\n                <p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">\n                  Restablecer contraseña\n                </a></p>\n                <p>Este enlace expira en 1 hora.</p>\n                <p>Si no solicitaste este cambio, ignora este email.</p>\n                <p>Saludos,<br>El equipo de FitLife</p>\n              </body>\n            </html>\n            '''
            part = MIMEText(html, 'html')
            msg.attach(part)
            logger.info(f'Email de restablecimiento enviado a {to_email}')
            return True
        except Exception as e:
            logger.error(f'Error al enviar email a {to_email}: {str(e)}')
            return False
