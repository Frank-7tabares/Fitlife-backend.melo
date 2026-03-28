from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..connection import Base
import uuid

class ProfileAuditLogModel(Base):
    __tablename__ = 'profile_audit_logs'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    changed_by = Column(CHAR(36), ForeignKey('users.id'), nullable=False)
    changes = Column(JSON, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
