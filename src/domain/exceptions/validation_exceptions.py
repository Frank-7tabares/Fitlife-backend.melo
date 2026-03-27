"""Excepciones de dominio para validaciones de valor."""
from .base import DomainException


class InvalidEmailException(DomainException):
    """Se lanza cuando el formato de email es inválido."""

    def __init__(self, email: str = ""):
        msg = f"Formato de email inválido: {email}" if email else "Formato de email inválido"
        super().__init__(msg, code="INVALID_EMAIL")


class WeakPasswordException(DomainException):
    """Se lanza cuando una contraseña no cumple los requisitos de complejidad."""

    def __init__(self, reason: str = ""):
        msg = f"Contraseña débil: {reason}" if reason else "La contraseña no cumple los requisitos"
        super().__init__(msg, code="WEAK_PASSWORD")


class InvalidValueException(DomainException):
    """Se lanza cuando un valor de dominio es inválido."""

    def __init__(self, field: str = "", reason: str = ""):
        msg = f"Valor inválido para '{field}': {reason}" if field else "Valor de dominio inválido"
        super().__init__(msg, code="INVALID_VALUE")
