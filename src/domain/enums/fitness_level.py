"""Enum: Nivel de condición física."""
from enum import Enum


class FitnessLevel(str, Enum):
    """Nivel de condición física del usuario."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    ELITE = "ELITE"
