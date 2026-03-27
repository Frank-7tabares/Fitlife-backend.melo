import bcrypt

# bcrypt 4.x rechaza contraseñas > 72 bytes; truncar en UTF-8 de forma segura
BCRYPT_MAX_BYTES = 72


def _to_bcrypt_input(password: str) -> bytes:
    """Convierte la contraseña a bytes y trunca a 72 bytes para bcrypt."""
    encoded = password.encode("utf-8")
    if len(encoded) > BCRYPT_MAX_BYTES:
        encoded = encoded[:BCRYPT_MAX_BYTES]
    return encoded


class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        data = _to_bcrypt_input(password)
        hashed = bcrypt.hashpw(data, bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        if not hashed_password:
            raise ValueError("hashed_password cannot be empty")
        data = _to_bcrypt_input(plain_password)
        try:
            return bcrypt.checkpw(data, hashed_password.encode("utf-8"))
        except (ValueError, TypeError):
            return False
