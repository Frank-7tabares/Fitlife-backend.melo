"""Excepciones de dominio relacionadas con usuarios."""
from .base import DomainException


class UserNotFoundException(DomainException):
    """Se lanza cuando no se encuentra un usuario."""

    def __init__(self, identifier: str = ""):
        msg = f"Usuario no encontrado: {identifier}" if identifier else "Usuario no encontrado"
        super().__init__(msg, code="USER_NOT_FOUND")


class EmailAlreadyExistsException(DomainException):
    """Se lanza cuando se intenta registrar un email ya existente."""

    def __init__(self, email: str = ""):
        msg = f"El email ya está registrado: {email}" if email else "El email ya está registrado"
        super().__init__(msg, code="EMAIL_ALREADY_EXISTS")


class UserInactiveException(DomainException):
    """Se lanza cuando se intenta operar sobre un usuario inactivo."""

    def __init__(self, user_id: str = ""):
        msg = f"La cuenta de usuario está inactiva: {user_id}" if user_id else "La cuenta está inactiva"
        super().__init__(msg, code="USER_INACTIVE")
