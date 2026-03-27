from typing import Any, Dict

from ..entities.assessment import AssessmentCategory, BodyAgeComparison


class AssessmentCalculator:
    @staticmethod
    def calculate_score(responses: Dict[str, Any]) -> float:
        """
        Cálculo de puntuación basado en:
        - Nivel de actividad (responses['activity'] viene del front como 2..10)
        - IMC calculado con weight_kg/height_cm
        - Ajuste suave por edad real para que no sea igual para todos
        """

        # Import local para evitar acoplar demasiado el módulo al resto.
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

        weight_kg = _to_float(responses.get("weight_kg"))
        height_cm = _to_float(responses.get("height_cm"))
        activity = _to_float(responses.get("activity"))
        real_age = _to_float(responses.get("real_age"))

        # Actividad: activityToScore (front) => 2..10 => 20..100
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

        # Penalización por edad (suave): 35 años => 0, a mayor diferencia => penaliza.
        age_penalty = 0.0
        if real_age is not None:
            age_penalty = abs(real_age - 35.0) / 10.0 * 5.0  # aprox 0..20

        score = activity_score - (bmi_penalty * 12.0) - age_penalty
        return min(max(score, 0.0), 100.0)

    @staticmethod
    def determine_category(score: float) -> AssessmentCategory:
        # Categorías existentes (no cambiamos el enum para no romper persistencia/DB).
        if score >= 90:
            return AssessmentCategory.EXCELLENT
        if score >= 70:
            return AssessmentCategory.GOOD
        if score >= 50:
            return AssessmentCategory.FAIR
        return AssessmentCategory.POOR

    @staticmethod
    def calculate_body_age(real_age: int, score: float) -> float:
        # Score alto => menor ajuste, score bajo => mayor ajuste.
        adjustment = (50.0 - float(score)) / 10.0
        return float(real_age) + adjustment

    @staticmethod
    def compare_body_age(real_age: int, body_age: float) -> BodyAgeComparison:
        if body_age > real_age + 0.5:
            return BodyAgeComparison.BODY_OLDER
        if body_age < real_age - 0.5:
            return BodyAgeComparison.BODY_YOUNGER
        return BodyAgeComparison.BODY_EQUAL
