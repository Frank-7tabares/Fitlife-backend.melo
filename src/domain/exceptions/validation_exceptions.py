from .base import DomainException

class InvalidEmailException(DomainException):

    def __init__(self, email: str=''):
        msg = f'Formato de email inválido: {email}' if email else 'Formato de email inválido'
        super().__init__(msg, code='INVALID_EMAIL')

class WeakPasswordException(DomainException):

    def __init__(self, reason: str=''):
        msg = f'Contraseña débil: {reason}' if reason else 'La contraseña no cumple los requisitos'
        super().__init__(msg, code='WEAK_PASSWORD')

class InvalidValueException(DomainException):

    def __init__(self, field: str='', reason: str=''):
        msg = f"Valor inválido para '{field}': {reason}" if field else 'Valor de dominio inválido'
        super().__init__(msg, code='INVALID_VALUE')
