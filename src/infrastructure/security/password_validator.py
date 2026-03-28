import re
from typing import Tuple

class PasswordValidator:
    MIN_LENGTH = 8

    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        if len(password) < PasswordValidator.MIN_LENGTH:
            return (False, f'Mínimo {PasswordValidator.MIN_LENGTH} caracteres')
        if not re.search('[A-Z]', password):
            return (False, 'Debe contener al menos 1 mayúscula')
        if not re.search('[a-z]', password):
            return (False, 'Debe contener al menos 1 minúscula')
        if not re.search('\\d', password):
            return (False, 'Debe contener al menos 1 número')
        return (True, '')
