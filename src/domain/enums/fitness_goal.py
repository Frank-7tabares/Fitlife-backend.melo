"""Enum: Objetivo de fitness del usuario."""
from enum import Enum


class FitnessGoal(str, Enum):
    """Objetivo principal de fitness del usuario."""

    WEIGHT_LOSS = "WEIGHT_LOSS"
    MUSCLE_GAIN = "MUSCLE_GAIN"
    GENERAL_FITNESS = "GENERAL_FITNESS"
    ATHLETIC_PERFORMANCE = "ATHLETIC_PERFORMANCE"
    FLEXIBILITY = "FLEXIBILITY"
    ENDURANCE = "ENDURANCE"
