"""Tests unitarios para la capa de dominio: Value Objects, Enums, Exceptions y Domain Services."""
import pytest
from decimal import Decimal
from uuid import uuid4


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------

class TestEmailValueObject:
    def test_valid_email_creates_successfully(self):
        from src.domain.value_objects.email import Email
        email = Email("user@fitlife.com")
        assert str(email) == "user@fitlife.com"

    def test_email_extracts_domain(self):
        from src.domain.value_objects.email import Email
        email = Email("coach@gym.co")
        assert email.domain() == "gym.co"

    def test_invalid_email_raises_value_error(self):
        from src.domain.value_objects.email import Email
        with pytest.raises(ValueError, match="inválido"):
            Email("not-an-email")

    def test_invalid_email_no_tld(self):
        from src.domain.value_objects.email import Email
        with pytest.raises(ValueError):
            Email("user@domain")

    def test_email_is_immutable(self):
        from src.domain.value_objects.email import Email
        email = Email("a@b.com")
        with pytest.raises(Exception):
            email.value = "other@b.com"

    def test_email_equality(self):
        from src.domain.value_objects.email import Email
        assert Email("a@b.com") == Email("a@b.com")

    def test_email_inequality(self):
        from src.domain.value_objects.email import Email
        assert Email("a@b.com") != Email("c@b.com")


class TestHashedPasswordValueObject:
    def test_valid_hash_creates_successfully(self):
        from src.domain.value_objects.password import HashedPassword
        hp = HashedPassword("$2b$12$averylonghashvaluehere")
        assert str(hp) == "$2b$12$averylonghashvaluehere"

    def test_empty_hash_raises_value_error(self):
        from src.domain.value_objects.password import HashedPassword
        with pytest.raises(ValueError, match="inválido"):
            HashedPassword("")

    def test_too_short_hash_raises_value_error(self):
        from src.domain.value_objects.password import HashedPassword
        with pytest.raises(ValueError):
            HashedPassword("short")

    def test_hashed_password_is_immutable(self):
        from src.domain.value_objects.password import HashedPassword
        hp = HashedPassword("$2b$12$validhashfortest")
        with pytest.raises(Exception):
            hp.value = "other"


class TestFitnessScoreValueObject:
    @pytest.mark.parametrize("value,expected_float", [("75.50", 75.50), ("0", 0.0), ("100", 100.0)])
    def test_valid_score(self, value, expected_float):
        from src.domain.value_objects.fitness_score import FitnessScore
        assert float(FitnessScore(Decimal(value))) == expected_float

    @pytest.mark.parametrize("invalid", ["100.01", "-1"])
    def test_invalid_score_raises(self, invalid):
        from src.domain.value_objects.fitness_score import FitnessScore
        with pytest.raises(ValueError):
            FitnessScore(Decimal(invalid))

    @pytest.mark.parametrize("value,category", [("90", "EXCELLENT"), ("75", "GOOD"), ("60", "FAIR"), ("30", "POOR")])
    def test_category(self, value, category):
        from src.domain.value_objects.fitness_score import FitnessScore
        assert FitnessScore(Decimal(value)).category() == category


class TestBodyAgeValueObject:
    @pytest.mark.parametrize("value,expected", [("28.5", 28.5), ("18", 18.0), ("120", 120.0)])
    def test_valid_body_age(self, value, expected):
        from src.domain.value_objects.body_age import BodyAge
        assert float(BodyAge(Decimal(value))) == expected

    @pytest.mark.parametrize("invalid", ["17", "121"])
    def test_invalid_body_age_raises(self, invalid):
        from src.domain.value_objects.body_age import BodyAge
        with pytest.raises(ValueError):
            BodyAge(Decimal(invalid))

    @pytest.mark.parametrize("age_val,real_age,expected_diff", [("35", 30, "5"), ("25", 30, "-5")])
    def test_age_difference(self, age_val, real_age, expected_diff):
        from src.domain.value_objects.body_age import BodyAge
        assert BodyAge(Decimal(age_val)).age_difference(real_age) == Decimal(expected_diff)


class TestBMIValueObject:
    def test_valid_bmi_creates(self):
        from src.domain.value_objects.bmi import BMI
        bmi = BMI(Decimal("22.5"))
        assert float(bmi) == 22.5

    def test_zero_bmi_raises(self):
        from src.domain.value_objects.bmi import BMI
        with pytest.raises(ValueError):
            BMI(Decimal("0"))

    def test_negative_bmi_raises(self):
        from src.domain.value_objects.bmi import BMI
        with pytest.raises(ValueError):
            BMI(Decimal("-5"))

    def test_from_measurements(self):
        from src.domain.value_objects.bmi import BMI
        bmi = BMI.from_measurements(weight_kg=70, height_cm=175)
        assert 22 <= float(bmi) <= 23

    def test_from_measurements_zero_height_raises(self):
        from src.domain.value_objects.bmi import BMI
        with pytest.raises(ValueError):
            BMI.from_measurements(weight_kg=70, height_cm=0)

    @pytest.mark.parametrize("value,category", [("17.0", "UNDERWEIGHT"), ("22.0", "NORMAL"), ("27.0", "OVERWEIGHT"), ("32.0", "OBESE")])
    def test_bmi_category(self, value, category):
        from src.domain.value_objects.bmi import BMI
        assert BMI(Decimal(value)).category() == category


# ---------------------------------------------------------------------------
# Domain Enums
# ---------------------------------------------------------------------------

class TestDomainEnums:
    def test_user_role_values(self):
        from src.domain.enums.user_role import UserRole
        assert UserRole.USER.value == "USER"
        assert UserRole.INSTRUCTOR.value == "INSTRUCTOR"
        assert UserRole.ADMIN.value == "ADMIN"

    def test_fitness_level_values(self):
        from src.domain.enums.fitness_level import FitnessLevel
        assert FitnessLevel.BEGINNER.value == "BEGINNER"
        assert FitnessLevel.INTERMEDIATE.value == "INTERMEDIATE"
        assert FitnessLevel.ADVANCED.value == "ADVANCED"
        assert FitnessLevel.ELITE.value == "ELITE"

    def test_fitness_goal_values(self):
        from src.domain.enums.fitness_goal import FitnessGoal
        assert FitnessGoal.WEIGHT_LOSS.value == "WEIGHT_LOSS"
        assert FitnessGoal.MUSCLE_GAIN.value == "MUSCLE_GAIN"
        assert FitnessGoal.GENERAL_FITNESS.value == "GENERAL_FITNESS"
        assert FitnessGoal.ATHLETIC_PERFORMANCE.value == "ATHLETIC_PERFORMANCE"

    def test_user_role_from_string(self):
        from src.domain.enums.user_role import UserRole
        assert UserRole("ADMIN") == UserRole.ADMIN

    def test_fitness_goal_is_str_enum(self):
        from src.domain.enums.fitness_goal import FitnessGoal
        assert isinstance(FitnessGoal.WEIGHT_LOSS, str)


# ---------------------------------------------------------------------------
# Domain Exceptions
# ---------------------------------------------------------------------------

class TestDomainExceptions:
    def test_domain_exception_has_message_and_code(self):
        from src.domain.exceptions.base import DomainException
        exc = DomainException("error msg", "ERR_CODE")
        assert exc.message == "error msg"
        assert exc.code == "ERR_CODE"
        assert str(exc) == "error msg"

    def test_domain_exception_default_code(self):
        from src.domain.exceptions.base import DomainException
        exc = DomainException("msg")
        assert exc.code == "DOMAIN_ERROR"

    def test_user_not_found_exception(self):
        from src.domain.exceptions.user_exceptions import UserNotFoundException
        exc = UserNotFoundException("abc123")
        assert exc.code == "USER_NOT_FOUND"
        assert "abc123" in str(exc)

    def test_user_not_found_without_id(self):
        from src.domain.exceptions.user_exceptions import UserNotFoundException
        exc = UserNotFoundException()
        assert "no encontrado" in str(exc).lower()

    def test_email_already_exists_exception(self):
        from src.domain.exceptions.user_exceptions import EmailAlreadyExistsException
        exc = EmailAlreadyExistsException("dup@test.com")
        assert exc.code == "EMAIL_ALREADY_EXISTS"
        assert "dup@test.com" in str(exc)

    def test_user_inactive_exception(self):
        from src.domain.exceptions.user_exceptions import UserInactiveException
        exc = UserInactiveException("user-123")
        assert exc.code == "USER_INACTIVE"

    def test_invalid_email_exception(self):
        from src.domain.exceptions.validation_exceptions import InvalidEmailException
        exc = InvalidEmailException("bad@")
        assert exc.code == "INVALID_EMAIL"
        assert "bad@" in str(exc)

    def test_weak_password_exception(self):
        from src.domain.exceptions.validation_exceptions import WeakPasswordException
        exc = WeakPasswordException("muy corta")
        assert exc.code == "WEAK_PASSWORD"

    def test_invalid_value_exception(self):
        from src.domain.exceptions.validation_exceptions import InvalidValueException
        exc = InvalidValueException("age", "debe ser positivo")
        assert exc.code == "INVALID_VALUE"
        assert "age" in str(exc)

    def test_exceptions_inherit_from_domain_exception(self):
        from src.domain.exceptions.base import DomainException
        from src.domain.exceptions.user_exceptions import UserNotFoundException, EmailAlreadyExistsException
        from src.domain.exceptions.validation_exceptions import InvalidEmailException

        assert issubclass(UserNotFoundException, DomainException)
        assert issubclass(EmailAlreadyExistsException, DomainException)
        assert issubclass(InvalidEmailException, DomainException)

    def test_exceptions_are_catchable_as_exception(self):
        from src.domain.exceptions.base import DomainException
        from src.domain.exceptions.user_exceptions import UserNotFoundException
        with pytest.raises(Exception):
            raise UserNotFoundException("test")
        with pytest.raises(DomainException):
            raise UserNotFoundException("test")


# ---------------------------------------------------------------------------
# Domain Services
# ---------------------------------------------------------------------------

class TestPasswordValidatorDomainService:
    def test_valid_password_returns_true(self):
        from src.domain.services.password_validator import PasswordValidator
        is_valid, msg = PasswordValidator.validate("SecurePass123!")
        assert is_valid is True
        assert msg == ""

    def test_too_short_returns_false(self):
        from src.domain.services.password_validator import PasswordValidator
        is_valid, msg = PasswordValidator.validate("Sh0rt!")
        assert is_valid is False
        assert "8" in msg

    def test_no_uppercase_returns_false(self):
        from src.domain.services.password_validator import PasswordValidator
        is_valid, msg = PasswordValidator.validate("lowercase123!")
        assert is_valid is False
        assert "mayúscula" in msg

    def test_no_lowercase_returns_false(self):
        from src.domain.services.password_validator import PasswordValidator
        is_valid, msg = PasswordValidator.validate("UPPERCASE123!")
        assert is_valid is False
        assert "minúscula" in msg

    def test_no_digit_returns_false(self):
        from src.domain.services.password_validator import PasswordValidator
        is_valid, msg = PasswordValidator.validate("NoDigitsHere!")
        assert is_valid is False
        assert "número" in msg

    def test_no_special_char_returns_false(self):
        from src.domain.services.password_validator import PasswordValidator
        is_valid, msg = PasswordValidator.validate("NoSpecial123")
        assert is_valid is False
        assert "especial" in msg

    def test_validate_or_raise_with_valid_password(self):
        from src.domain.services.password_validator import PasswordValidator
        PasswordValidator.validate_or_raise("ValidPass123!")

    def test_validate_or_raise_raises_weak_password_exception(self):
        from src.domain.services.password_validator import PasswordValidator
        from src.domain.exceptions.validation_exceptions import WeakPasswordException
        with pytest.raises(WeakPasswordException):
            PasswordValidator.validate_or_raise("weak")


class TestBMICalculatorDomainService:
    def test_calculate_returns_bmi(self):
        from src.domain.services.bmi_calculator import BMICalculator
        bmi = BMICalculator.calculate(weight_kg=70, height_cm=175)
        assert 22 <= float(bmi) <= 23

    def test_category_normal(self):
        from src.domain.services.bmi_calculator import BMICalculator
        from src.domain.value_objects.bmi import BMI
        bmi = BMI(Decimal("22.0"))
        assert BMICalculator.category(bmi) == "NORMAL"

    def test_adjustment_normal_bmi_is_zero(self):
        from src.domain.services.bmi_calculator import BMICalculator
        from src.domain.value_objects.bmi import BMI
        bmi = BMI(Decimal("22.0"))
        assert BMICalculator.adjustment_for_score(bmi) == Decimal("0")

    def test_adjustment_overweight(self):
        from src.domain.services.bmi_calculator import BMICalculator
        from src.domain.value_objects.bmi import BMI
        bmi = BMI(Decimal("27.0"))
        assert BMICalculator.adjustment_for_score(bmi) == Decimal("1.5")

    def test_adjustment_obese(self):
        from src.domain.services.bmi_calculator import BMICalculator
        from src.domain.value_objects.bmi import BMI
        bmi = BMI(Decimal("32.0"))
        assert BMICalculator.adjustment_for_score(bmi) == Decimal("3.5")

    def test_adjustment_underweight(self):
        from src.domain.services.bmi_calculator import BMICalculator
        from src.domain.value_objects.bmi import BMI
        bmi = BMI(Decimal("17.5"))
        assert BMICalculator.adjustment_for_score(bmi) == Decimal("1.0")

    def test_adjustment_severely_underweight(self):
        from src.domain.services.bmi_calculator import BMICalculator
        from src.domain.value_objects.bmi import BMI
        bmi = BMI(Decimal("15.0"))
        assert BMICalculator.adjustment_for_score(bmi) == Decimal("3.0")
