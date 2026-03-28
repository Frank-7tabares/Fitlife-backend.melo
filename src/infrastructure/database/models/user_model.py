from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Enum as SQLEnum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid
from src.domain.entities.user import UserRole, Gender, FitnessGoal

class UserModel(Base):
    __tablename__ = 'users'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    full_name = Column(String(255), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)
    height = Column(Float, nullable=True)
    fitness_goal = Column(SQLEnum(FitnessGoal), nullable=True)
    activity_level = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
