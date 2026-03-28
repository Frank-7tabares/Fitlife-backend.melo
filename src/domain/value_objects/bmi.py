from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class BMI:
    value: Decimal

    def __post_init__(self):
        value = Decimal(str(self.value))
        object.__setattr__(self, 'value', value)
        if value <= Decimal('0'):
            raise ValueError(f'BMI debe ser mayor a 0, recibido: {value}')

    @classmethod
    def from_measurements(cls, weight_kg: float, height_cm: float) -> 'BMI':
        if height_cm <= 0 or weight_kg <= 0:
            raise ValueError('Peso y altura deben ser positivos')
        height_m = Decimal(str(height_cm)) / Decimal('100')
        bmi_value = Decimal(str(weight_kg)) / height_m ** 2
        return cls(value=bmi_value.quantize(Decimal('0.01')))

    def category(self) -> str:
        if self.value < Decimal('18.5'):
            return 'UNDERWEIGHT'
        elif self.value < Decimal('25.0'):
            return 'NORMAL'
        elif self.value < Decimal('30.0'):
            return 'OVERWEIGHT'
        return 'OBESE'

    def __float__(self) -> float:
        return float(self.value)
