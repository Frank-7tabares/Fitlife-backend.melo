from .base import DomainException

class UserNotFoundException(DomainException):

    def __init__(self, identifier: str=''):
        msg = f'Usuario no encontrado: {identifier}' if identifier else 'Usuario no encontrado'
        super().__init__(msg, code='USER_NOT_FOUND')

class EmailAlreadyExistsException(DomainException):

    def __init__(self, email: str=''):
        msg = f'El email ya está registrado: {email}' if email else 'El email ya está registrado'
        super().__init__(msg, code='EMAIL_ALREADY_EXISTS')

class UserInactiveException(DomainException):

    def __init__(self, user_id: str=''):
        msg = f'La cuenta de usuario está inactiva: {user_id}' if user_id else 'La cuenta está inactiva'
        super().__init__(msg, code='USER_INACTIVE')
