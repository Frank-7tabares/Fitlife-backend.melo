"""
Pruebas unitarias — AssessmentCalculator
Casos borde sobre el cálculo de puntuación, categoría y edad corporal.
"""
import pytest
from src.domain.services.assessment_calculator import AssessmentCalculator
from src.domain.entities.assessment import AssessmentCategory, BodyAgeComparison


@pytest.fixture
def calc() -> AssessmentCalculator:
    return AssessmentCalculator()


# ---------------------------------------------------------------------------
# calculate_score
# ---------------------------------------------------------------------------

class TestCalculateScore:

    def test_empty_responses_returns_zero(self, calc):
        assert calc.calculate_score({}) == 0.0

    def test_all_zeros_returns_zero(self, calc):
        score = calc.calculate_score({"pushups": 0, "run_minutes": 0, "flexibility": 0})
        assert score == 0.0

    def test_all_max_values_returns_100(self, calc):
        # 5 preguntas × valor 10 = máximo posible
        responses = {f"q{i}": 10 for i in range(5)}
        assert calc.calculate_score(responses) == 100.0

    def test_boolean_true_counts_as_10(self, calc):
        # True debe contar como 10 puntos según la implementación
        score = calc.calculate_score({"active": True})
        assert score == 100.0

    def test_values_above_max_capped_at_100(self, calc):
        # Valores extremadamente altos no deben superar 100
        score = calc.calculate_score({"pushups": 9999})
        assert score == 100.0

    def test_partial_score_calculated_correctly(self, calc):
        # 1 pregunta con valor 5 de 10 → 50%
        score = calc.calculate_score({"q1": 5})
        assert score == pytest.approx(50.0)

    def test_mixed_types_ignored_strings(self, calc):
        # Strings no son numéricos, se omiten
        score = calc.calculate_score({"name": "alto", "pushups": 10})
        # "name" no es numérico ni bool → no suma; solo "pushups":10 → 10/20*100 = 50
        assert score == pytest.approx(50.0)

    def test_single_question_max(self, calc):
        assert calc.calculate_score({"q1": 10}) == 100.0

    def test_single_question_zero(self, calc):
        assert calc.calculate_score({"q1": 0}) == 0.0

    def test_negative_values_reduce_score(self, calc):
        # Valores negativos reducen la puntuación pero están acotados en 0
        score = calc.calculate_score({"q1": -10})
        assert score == 0.0


# ---------------------------------------------------------------------------
# determine_category — límites exactos
# ---------------------------------------------------------------------------

class TestDetermineCategory:

    def test_score_100_is_excellent(self, calc):
        assert calc.determine_category(100.0) == AssessmentCategory.EXCELLENT

    def test_score_90_boundary_is_excellent(self, calc):
        assert calc.determine_category(90.0) == AssessmentCategory.EXCELLENT

    def test_score_just_below_90_is_good(self, calc):
        assert calc.determine_category(89.9) == AssessmentCategory.GOOD

    def test_score_70_boundary_is_good(self, calc):
        assert calc.determine_category(70.0) == AssessmentCategory.GOOD

    def test_score_just_below_70_is_fair(self, calc):
        assert calc.determine_category(69.9) == AssessmentCategory.FAIR

    def test_score_50_boundary_is_fair(self, calc):
        assert calc.determine_category(50.0) == AssessmentCategory.FAIR

    def test_score_just_below_50_is_poor(self, calc):
        assert calc.determine_category(49.9) == AssessmentCategory.POOR

    def test_score_0_is_poor(self, calc):
        assert calc.determine_category(0.0) == AssessmentCategory.POOR


# ---------------------------------------------------------------------------
# calculate_body_age
# ---------------------------------------------------------------------------

class TestCalculateBodyAge:

    def test_score_50_equals_real_age(self, calc):
        # adjustment = (50 - 50) / 10 = 0 → body_age = real_age
        assert calc.calculate_body_age(30, 50.0) == pytest.approx(30.0)

    def test_score_100_makes_body_younger(self, calc):
        # adjustment = (50 - 100) / 10 = -5 → body_age = 25
        assert calc.calculate_body_age(30, 100.0) == pytest.approx(25.0)

    def test_score_0_makes_body_older(self, calc):
        # adjustment = (50 - 0) / 10 = 5 → body_age = 35
        assert calc.calculate_body_age(30, 0.0) == pytest.approx(35.0)

    def test_score_90_body_age_younger(self, calc):
        # adjustment = (50 - 90) / 10 = -4 → body_age = 26
        assert calc.calculate_body_age(30, 90.0) == pytest.approx(26.0)

    def test_young_real_age(self, calc):
        # Edad muy baja: 18 años con score 0 → body_age = 23
        assert calc.calculate_body_age(18, 0.0) == pytest.approx(23.0)

    def test_elderly_real_age(self, calc):
        # Edad alta: 70 años con score 100 → body_age = 65
        assert calc.calculate_body_age(70, 100.0) == pytest.approx(65.0)


# ---------------------------------------------------------------------------
# compare_body_age — límites exactos del rango ±0.5
# ---------------------------------------------------------------------------

class TestCompareBodyAge:

    def test_body_younger_when_body_age_significantly_lower(self, calc):
        # body_age = 25, real_age = 30 → diferencia -5 → BODY_YOUNGER
        assert calc.compare_body_age(30, 25.0) == BodyAgeComparison.BODY_YOUNGER

    def test_body_older_when_body_age_significantly_higher(self, calc):
        # body_age = 35, real_age = 30 → diferencia +5 → BODY_OLDER
        assert calc.compare_body_age(30, 35.0) == BodyAgeComparison.BODY_OLDER

    def test_body_equal_when_same_age(self, calc):
        assert calc.compare_body_age(30, 30.0) == BodyAgeComparison.BODY_EQUAL

    def test_body_equal_at_upper_boundary(self, calc):
        # body_age = real_age + 0.5 → exactamente en el límite → BODY_EQUAL
        assert calc.compare_body_age(30, 30.5) == BodyAgeComparison.BODY_EQUAL

    def test_body_older_just_above_upper_boundary(self, calc):
        # body_age = real_age + 0.51 → supera el límite → BODY_OLDER
        assert calc.compare_body_age(30, 30.51) == BodyAgeComparison.BODY_OLDER

    def test_body_equal_at_lower_boundary(self, calc):
        # body_age = real_age - 0.5 → exactamente en el límite → BODY_EQUAL
        assert calc.compare_body_age(30, 29.5) == BodyAgeComparison.BODY_EQUAL

    def test_body_younger_just_below_lower_boundary(self, calc):
        # body_age = real_age - 0.51 → supera el límite → BODY_YOUNGER
        assert calc.compare_body_age(30, 29.49) == BodyAgeComparison.BODY_YOUNGER
