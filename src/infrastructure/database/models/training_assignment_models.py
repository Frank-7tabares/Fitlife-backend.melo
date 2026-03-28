from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid

class RoutineAssignmentModel(Base):
    __tablename__ = 'routine_assignments'
    user_id = Column(CHAR(36), ForeignKey('users.id'), primary_key=True)
    routine_id = Column(CHAR(36), ForeignKey('routines.id'), primary_key=True)
    assigned_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)

class WorkoutCompletionModel(Base):
    __tablename__ = 'workout_completions'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, index=True)
    routine_id = Column(CHAR(36), ForeignKey('routines.id'), nullable=False)
    completed_at = Column(DateTime, server_default=func.now())
    effort_level = Column(Integer, nullable=False)
    notes = Column(String(500))
