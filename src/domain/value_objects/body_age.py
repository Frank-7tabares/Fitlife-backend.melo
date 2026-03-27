"""Value Object: BodyAge (edad corporal estimada)."""
from dataclasses import dataclass
from decimal import Decimal

_MIN_BODY_AGE = Decimal("18")
_MAX_BODY_AGE = Decimal("120")


@dataclass(frozen=True)
class BodyAge:
    """Value Object inmutable para edad corporal estimada."""

    value: Decimal

    def __post_init__(self):
        value = Decimal(str(self.value))
        object.__setattr__(self, "value", value)
        if not (_MIN_BODY_AGE <= value <= _MAX_BODY_AGE):
            raise ValueError(
                f"BodyAge debe estar entre {_MIN_BODY_AGE} y {_MAX_BODY_AGE}, recibido: {value}"
            )

    def age_difference(self, real_age: int) -> Decimal:
        """Diferencia entre edad corporal y edad real (positivo = mayor, negativo = menor)."""
        return self.value - Decimal(str(real_age))

    def __float__(self) -> float:
        return float(self.value)
