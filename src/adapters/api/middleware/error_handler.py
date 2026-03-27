"""Middleware: Manejador centralizado de errores HTTP."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ....domain.exceptions.base import DomainException
from ....domain.exceptions.user_exceptions import UserNotFoundException, EmailAlreadyExistsException


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores de excepción en la app FastAPI."""

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(request: Request, exc: UserNotFoundException):
        return JSONResponse(
            status_code=404,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(EmailAlreadyExistsException)
    async def email_exists_handler(request: Request, exc: EmailAlreadyExistsException):
        return JSONResponse(
            status_code=409,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message, "code": exc.code},
        )
