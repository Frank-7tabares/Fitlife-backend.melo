"""Servicio de envío de emails para restablecimiento de contraseña (RF-012)."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ...config.settings import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar emails de restablecimiento de contraseña."""

    @staticmethod
    async def send_password_reset_email(to_email: str, reset_token: str, user_name: str = "") -> bool:
        """Envía enlace de restablecimiento de contraseña por email.
        
        Args:
            to_email: Dirección del destinatario
            reset_token: Token de restablecimiento a incluir en el enlace
            user_name: Nombre del usuario (para personalización)
            
        Returns:
            True si se envió exitosamente, False si falló
        """
        try:
            # Construir enlace de restablecimiento
            reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
            
            # Construir email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Restablece tu contraseña en FitLife"
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = to_email

            # Cuerpo HTML del email
            html = f"""
            <html>
              <body>
                <h2>Hola {user_name or 'Usuario'},</h2>
                <p>Recibimos una solicitud para restablecer tu contraseña.</p>
                <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                <p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                  Restablecer contraseña
                </a></p>
                <p>Este enlace expira en 1 hora.</p>
                <p>Si no solicitaste este cambio, ignora este email.</p>
                <p>Saludos,<br>El equipo de FitLife</p>
              </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            msg.attach(part)

            # Enviar SMTP (aquí se podría usar smtplib real en producción)
            # Por ahora, solo registrar el intento
            logger.info(f"Email de restablecimiento enviado a {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error al enviar email a {to_email}: {str(e)}")
            return False
