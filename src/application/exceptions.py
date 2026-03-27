"""Excepciones de la capa de aplicación para que los adaptadores mapeen a códigos HTTP."""


class EmailAlreadyRegisteredError(ValueError):
    """El correo electrónico ya está registrado (debe devolver 409 Conflict)."""
    pass
