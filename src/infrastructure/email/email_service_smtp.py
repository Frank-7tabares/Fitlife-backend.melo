"""Servicio de envío de emails usando SMTP real (restablecimiento y bienvenida)."""

import asyncio
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from ...config.settings import settings

logger = logging.getLogger(__name__)


def _normalize_app_password(raw: str) -> str:
    """Gmail muestra la App Password con espacios; SMTP suele requerirla sin espacios."""
    return "".join((raw or "").split())


class SmtpEmailService:
    """Email service que envía mensajes vía SMTP."""

    @staticmethod
    def _frontend_base_url() -> str:
        """
        Usa el primer origin permitido por CORS para apuntar al frontend real
        (útil cuando FRONTEND_URL por defecto no coincide con Vite 5173/5174).
        """
        try:
            if hasattr(settings, "cors_origins_list") and settings.cors_origins_list:
                return settings.cors_origins_list[0]
        except Exception:
            pass
        return settings.FRONTEND_URL

    @staticmethod
    def _send_password_reset_email_sync(to_email: str, reset_token: str, user_name: str = "") -> bool:
        """Versión síncrona para ejecutar en thread (evita bloqueos del event loop)."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Codigo para cambiar tu contrasena - FitLife"
            # Gmail rechaza o falla si From / envelope no coincide con la cuenta autenticada.
            smtp_user = (getattr(settings, "EMAIL_USER", None) or "").strip()
            from_addr = smtp_user or (getattr(settings, "EMAIL_FROM", None) or "").strip()
            msg["From"] = formataddr(("FitLife", from_addr)) if from_addr else settings.EMAIL_FROM
            msg["To"] = to_email

            html = f"""
            <html>
              <body>
                <h2>Hola {user_name or 'Usuario'},</h2>
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
            </html>
            """

            msg.attach(MIMEText(html, "html"))

            email_user = (getattr(settings, "EMAIL_USER", None) or "").strip()
            email_password = _normalize_app_password(
                (getattr(settings, "EMAIL_PASSWORD", None) or "").strip()
            )
            if (
                not email_user
                or not email_password
                or "your-" in email_user.lower()
                or "your-" in email_password.lower()
            ):
                raise RuntimeError(
                    "SMTP no configurado en el backend. Define EMAIL_USER y EMAIL_PASSWORD (App Password) en fitlife-backend-melo/.env"
                )

            host = getattr(settings, "EMAIL_HOST", "smtp.gmail.com")
            # Intentar 465 (SSL) y 587 (STARTTLS): Gmail funciona con ambos
            ports_to_try = [465, 587]
            port_setting = int(getattr(settings, "EMAIL_PORT", 587))
            if port_setting in ports_to_try:
                ports_to_try = [port_setting] + [p for p in ports_to_try if p != port_setting]

            last_err = None
            for port in ports_to_try:
                try:
                    if port == 465:
                        context = ssl.create_default_context()
                        with smtplib.SMTP_SSL(host, port, context=context, timeout=25) as server:
                            server.login(email_user, email_password)
                            server.sendmail(from_addr, [to_email], msg.as_string())
                    else:
                        server = smtplib.SMTP(host, port, timeout=25)
                        try:
                            server.ehlo()
                            server.starttls(context=ssl.create_default_context())
                            server.ehlo()
                            server.login(email_user, email_password)
                            server.sendmail(from_addr, [to_email], msg.as_string())
                        finally:
                            server.quit()
                    logger.info(f"Email de restablecimiento enviado a {to_email} (puerto {port})")
                    return True
                except Exception as e:
                    last_err = e
                    print(f"[SMTP] Puerto {port} falló: {e}. Probando siguiente...", flush=True)
                    continue

            if last_err:
                hint = ""
                msg = str(last_err).lower()
                if "535" in msg or "badcredentials" in msg:
                    hint = " (Gmail: usa App Password con 2FA habilitado)"
                logger.error(f"Error al enviar email a {to_email}: {last_err}{hint}")
                raise RuntimeError(f"No se pudo enviar el email.{hint}".strip())
            return False
        except Exception as e:
            hint = ""
            msg = str(e).lower()
            if "535" in msg or "badcredentials" in msg:
                hint = " (Sugerencia: si usas Gmail, configura EMAIL_PASSWORD como App Password y asegúrate de que la cuenta tenga 2FA habilitado.)"
            logger.error(f"Error al enviar email de restablecimiento a {to_email}: {str(e)}{hint}")
            raise RuntimeError(f"No se pudo enviar el email de restablecimiento.{hint}".strip())

    @staticmethod
    async def send_password_reset_email(to_email: str, reset_token: str, user_name: str = "") -> bool:
        """Envía en thread separado para evitar bloqueos del event loop de uvicorn."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: SmtpEmailService._send_password_reset_email_sync(to_email, reset_token, user_name),
        )

    @staticmethod
    async def send_welcome_email(to_email: str, user_name: str) -> bool:
        try:
            login_url = f"{SmtpEmailService._frontend_base_url()}/auth/login"

            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Bienvenido a FitLife"
            smtp_user = (getattr(settings, "EMAIL_USER", None) or "").strip()
            from_addr = smtp_user or (getattr(settings, "EMAIL_FROM", None) or "").strip()
            msg["From"] = formataddr(("FitLife", from_addr)) if from_addr else settings.EMAIL_FROM
            msg["To"] = to_email

            html = f"""
            <html>
              <body>
                <h2>Hola {user_name or 'Usuario'},</h2>
                <p>Bienvenido a FitLife.</p>
                <p>Comienza creando tu evaluación física para obtener tu plan personalizado.</p>
                <p>
                  <a href="{login_url}" style="background-color: #CCFF00; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Ir a iniciar sesión
                  </a>
                </p>
                <p>Saludos,<br>El equipo de FitLife</p>
              </body>
            </html>
            """

            msg.attach(MIMEText(html, "html"))

            email_user = (getattr(settings, "EMAIL_USER", None) or "").strip()
            email_password = _normalize_app_password(
                (getattr(settings, "EMAIL_PASSWORD", None) or "").strip()
            )
            if (
                not email_user
                or not email_password
                or "your-" in email_user.lower()
                or "your-" in email_password.lower()
            ):
                logger.warning("SMTP no configurado: EMAIL_USER/EMAIL_PASSWORD. Omite envío de bienvenida.")
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

            logger.info(f"Email de bienvenida enviado a {to_email}")
            return True
        except Exception as e:
            hint = ""
            msg_str = str(e).lower()
            if "535" in msg_str or "badcredentials" in msg_str:
                hint = " (Gmail: usa App Password con 2FA.)"
            logger.error(f"Error al enviar email de bienvenida a {to_email}: {e}{hint}")
            return False

