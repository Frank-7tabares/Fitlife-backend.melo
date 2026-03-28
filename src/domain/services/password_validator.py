import re
from typing import Tuple
from ..exceptions.validation_exceptions import WeakPasswordException
_MIN_LENGTH = 8
_SPECIAL_CHARS = '!@#$%^&*'

class PasswordValidator:
    MIN_LENGTH = _MIN_LENGTH
    SPECIAL_CHARS = _SPECIAL_CHARS

    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        if len(password) < _MIN_LENGTH:
            return (False, f'Mínimo {_MIN_LENGTH} caracteres')
        if not re.search('[A-Z]', password):
            return (False, 'Debe contener al menos 1 mayúscula')
        if not re.search('[a-z]', password):
            return (False, 'Debe contener al menos 1 minúscula')
        if not re.search('\\d', password):
            return (False, 'Debe contener al menos 1 número')
        if not re.search(f'[{re.escape(_SPECIAL_CHARS)}]', password):
            return (False, f'Debe contener al menos 1 carácter especial ({_SPECIAL_CHARS})')
        return (True, '')

    @staticmethod
    def validate_or_raise(password: str) -> None:
        is_valid, reason = PasswordValidator.validate(password)
        if not is_valid:
            raise WeakPasswordException(reason)
