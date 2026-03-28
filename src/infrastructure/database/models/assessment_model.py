from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid
from ....domain.entities.assessment import AssessmentCategory, BodyAgeComparison

class AssessmentModel(Base):
    __tablename__ = 'assessments'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    fitness_score = Column(Float, nullable=False)
    category = Column(SQLEnum(AssessmentCategory), nullable=False)
    body_age = Column(Float, nullable=False)
    comparison = Column(SQLEnum(BodyAgeComparison), nullable=False)
    responses = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
