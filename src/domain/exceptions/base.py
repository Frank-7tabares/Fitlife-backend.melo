"""Excepción base para todas las excepciones de dominio."""


class DomainException(Exception):
    """Excepción base de la capa de dominio.

    Todas las excepciones de negocio deben heredar de esta clase
    para permitir manejo diferenciado en los adaptadores primarios.
    """

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return self.message
