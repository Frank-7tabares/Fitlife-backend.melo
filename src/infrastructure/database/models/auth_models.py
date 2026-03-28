from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid
from src.domain.entities.password_reset_token import ResetTokenStatus

class RefreshTokenModel(Base):
    __tablename__ = 'refresh_tokens'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    revoked_at = Column(DateTime, nullable=True)

class PasswordResetTokenModel(Base):
    __tablename__ = 'password_reset_tokens'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    status = Column(Enum(ResetTokenStatus), default=ResetTokenStatus.PENDING, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    used_at = Column(DateTime, nullable=True)

class PasswordHistoryModel(Base):
    __tablename__ = 'password_history'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    changed_at = Column(DateTime, server_default=func.now())
