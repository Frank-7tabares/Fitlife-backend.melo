from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid

class InstructorModel(Base):
    __tablename__ = 'instructors'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    certifications = Column(JSON, nullable=False)
    specializations = Column(String(500), nullable=True)
    rating_avg = Column(Float, default=0.0, nullable=False)
    certificate_url = Column(String(500), nullable=True)
    certificate_status = Column(String(20), default='pending', nullable=False)

class InstructorAssignmentModel(Base):
    __tablename__ = 'instructor_assignments'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    instructor_id = Column(CHAR(36), ForeignKey('instructors.id', ondelete='CASCADE'), nullable=False, index=True)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class InstructorRatingModel(Base):
    __tablename__ = 'instructor_ratings'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    instructor_id = Column(CHAR(36), ForeignKey('instructors.id', ondelete='CASCADE'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    comment = Column(Text, nullable=True)
