from decimal import Decimal
from ..value_objects.bmi import BMI

class BMICalculator:

    @staticmethod
    def calculate(weight_kg: float, height_cm: float) -> BMI:
        return BMI.from_measurements(weight_kg, height_cm)

    @staticmethod
    def category(bmi: BMI) -> str:
        return bmi.category()

    @staticmethod
    def adjustment_for_score(bmi: BMI) -> Decimal:
        val = bmi.value
        if Decimal('18.5') <= val < Decimal('25.0'):
            return Decimal('0')
        elif Decimal('25.0') <= val < Decimal('30.0'):
            return Decimal('1.5')
        elif val >= Decimal('30.0'):
            return Decimal('3.5')
        elif Decimal('17.0') <= val < Decimal('18.5'):
            return Decimal('1.0')
        return Decimal('3.0')
