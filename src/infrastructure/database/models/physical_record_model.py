import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func

from ..connection import Base


class PhysicalRecordModel(Base):
    __tablename__ = "physical_records"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    body_fat_percentage = Column(Float, nullable=True)
    waist = Column(Float, nullable=True)
    hip = Column(Float, nullable=True)
    activity_level = Column(String(20), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
