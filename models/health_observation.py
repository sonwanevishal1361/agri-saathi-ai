"""Crop health observation and symptom diagnosis tracking model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class HealthObservation(Base):
    __tablename__ = "health_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="SET NULL"), nullable=True, index=True)
    symptom_description = Column(Text, nullable=False)
    image_storage_path = Column(String(255), nullable=True)
    possible_causes = Column(Text, nullable=True)
    advice_summary = Column(Text, nullable=True)
    source_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    farmer = relationship("User", back_populates="health_observations")
    crop = relationship("Crop", back_populates="health_observations")

    def __repr__(self):
        return f"<HealthObservation {self.id}>"
