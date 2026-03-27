"""Servicio de validación de complejidad de contraseña (RF-017)."""
import re
from typing import Tuple


class PasswordValidator:
    """Valida complejidad de contraseña (igual que en registro)."""

    MIN_LENGTH = 8

    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        if len(password) < PasswordValidator.MIN_LENGTH:
            return False, f"Mínimo {PasswordValidator.MIN_LENGTH} caracteres"
        if not re.search(r"[A-Z]", password):
            return False, "Debe contener al menos 1 mayúscula"
        if not re.search(r"[a-z]", password):
            return False, "Debe contener al menos 1 minúscula"
        if not re.search(r"\d", password):
            return False, "Debe contener al menos 1 número"
        return True, ""
