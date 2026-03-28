from enum import Enum

class UserRole(str, Enum):
    USER = 'USER'
    INSTRUCTOR = 'INSTRUCTOR'
    ADMIN = 'ADMIN'
