import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise ValueError(f'Formato de email inválido: {self.value}')

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value

    def domain(self) -> str:
        return self.value.split('@')[1]
