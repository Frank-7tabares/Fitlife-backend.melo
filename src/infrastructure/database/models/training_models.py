from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.mysql import CHAR
from ..connection import Base
import uuid
from ....domain.entities.training import FitnessLevel

class ExerciseModel(Base):
    __tablename__ = 'exercises'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    muscle_group = Column(String(100))
    difficulty = Column(String(50))

class RoutineModel(Base):
    __tablename__ = 'routines'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    goal = Column(String(255))
    level = Column(SQLEnum(FitnessLevel), nullable=False)
    exercises_data = Column(JSON, nullable=False)
    creator_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)
