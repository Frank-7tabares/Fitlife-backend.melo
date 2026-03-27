"""Value Object: HashedPassword (contraseña ya hasheada)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class HashedPassword:
    """Value Object inmutable para contraseña hasheada."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 20:
            raise ValueError("Hash de contraseña inválido")

    def __str__(self) -> str:
        return self.value
