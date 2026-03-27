"""Servicio de dominio: Cálculo de IMC (Índice de Masa Corporal)."""
from decimal import Decimal

from ..value_objects.bmi import BMI


class BMICalculator:
    """Servicio de dominio para cálculo e interpretación del IMC."""

    @staticmethod
    def calculate(weight_kg: float, height_cm: float) -> BMI:
        """Calcula el BMI desde peso (kg) y altura (cm)."""
        return BMI.from_measurements(weight_kg, height_cm)

    @staticmethod
    def category(bmi: BMI) -> str:
        """Categoriza el BMI según OMS."""
        return bmi.category()

    @staticmethod
    def adjustment_for_score(bmi: BMI) -> Decimal:
        """Devuelve ajuste de edad corporal basado en el IMC.

        BMI normal (18.5-24.9) → 0
        Sobrepeso/bajo peso leve → +1 a +3
        Obesidad/bajo peso severo → +3 a +5
        """
        val = bmi.value
        if Decimal("18.5") <= val < Decimal("25.0"):
            return Decimal("0")
        elif Decimal("25.0") <= val < Decimal("30.0"):
            return Decimal("1.5")
        elif val >= Decimal("30.0"):
            return Decimal("3.5")
        elif Decimal("17.0") <= val < Decimal("18.5"):
            return Decimal("1.0")
        return Decimal("3.0")
