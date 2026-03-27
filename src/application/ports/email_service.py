"""Puerto de salida: Servicio de email (interfaz ABC)."""
from abc import ABC, abstractmethod


class EmailService(ABC):
    """Puerto de salida para envío de correos electrónicos."""

    @abstractmethod
    async def send_password_reset_email(
        self, to_email: str, reset_token: str, user_name: str
    ) -> bool:
        """Envía email de restablecimiento de contraseña.

        Returns:
            True si se envió correctamente, False en caso contrario.
        """
        ...

    @abstractmethod
    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Envía email de bienvenida al registrarse."""
        ...

    @abstractmethod
    async def send_password_changed_email(self, to_email: str, user_name: str) -> bool:
        """Envía confirmación de cambio de contraseña exitoso."""
        ...
