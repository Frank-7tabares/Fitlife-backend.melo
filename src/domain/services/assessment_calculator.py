from typing import Any, Dict
from ..entities.assessment import AssessmentCategory, BodyAgeComparison

class AssessmentCalculator:

    @staticmethod
    def calculate_score(responses: Dict[str, Any]) -> float:
        from .bmi_calculator import BMICalculator

        def _to_float(v: Any) -> float | None:
            if v is None:
                return None
            if isinstance(v, (int, float)):
                return float(v)
            try:
                return float(str(v))
            except (ValueError, TypeError):
                return None
        weight_kg = _to_float(responses.get('weight_kg'))
        height_cm = _to_float(responses.get('height_cm'))
        activity = _to_float(responses.get('activity'))
        real_age = _to_float(responses.get('real_age'))
        if activity is None:
            activity = 5.0
        activity_score = max(activity, 0.0) * 10.0
        bmi_penalty = 0.0
        if weight_kg is not None and height_cm is not None:
            try:
                bmi = BMICalculator.calculate(weight_kg, height_cm)
                bmi_penalty = float(BMICalculator.adjustment_for_score(bmi))
            except Exception:
                bmi_penalty = 0.0
        age_penalty = 0.0
        if real_age is not None:
            age_penalty = abs(real_age - 35.0) / 10.0 * 5.0
        score = activity_score - bmi_penalty * 12.0 - age_penalty
        return min(max(score, 0.0), 100.0)

    @staticmethod
    def determine_category(score: float) -> AssessmentCategory:
        if score >= 90:
            return AssessmentCategory.EXCELLENT
        if score >= 70:
            return AssessmentCategory.GOOD
        if score >= 50:
            return AssessmentCategory.FAIR
        return AssessmentCategory.POOR

    @staticmethod
    def calculate_body_age(real_age: int, score: float) -> float:
        adjustment = (50.0 - float(score)) / 10.0
        return float(real_age) + adjustment

    @staticmethod
    def compare_body_age(real_age: int, body_age: float) -> BodyAgeComparison:
        if body_age > real_age + 0.5:
            return BodyAgeComparison.BODY_OLDER
        if body_age < real_age - 0.5:
            return BodyAgeComparison.BODY_YOUNGER
        return BodyAgeComparison.BODY_EQUAL
