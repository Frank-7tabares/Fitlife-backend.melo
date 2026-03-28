from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class FitnessScore:
    value: Decimal

    def __post_init__(self):
        value = Decimal(str(self.value))
        object.__setattr__(self, 'value', value)
        if not Decimal('0') <= value <= Decimal('100'):
            raise ValueError(f'FitnessScore debe estar entre 0 y 100, recibido: {value}')

    def category(self) -> str:
        if self.value >= Decimal('85'):
            return 'EXCELLENT'
        elif self.value >= Decimal('70'):
            return 'GOOD'
        elif self.value >= Decimal('50'):
            return 'FAIR'
        return 'POOR'

    def __float__(self) -> float:
        return float(self.value)
