"""Enum: Roles de usuario en el sistema."""
from enum import Enum


class UserRole(str, Enum):
    """Roles de usuario para autorización RBAC."""

    USER = "USER"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"
