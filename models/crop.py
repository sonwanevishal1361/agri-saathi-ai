"""Crop management database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Crop(Base):
    __tablename__ = "crops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    variety = Column(String(100), nullable=True)
    plot_name = Column(String(100), nullable=True)
    area = Column(Float, nullable=False)
    area_unit = Column(String(20), default="Acre", nullable=False)
    sowing_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=False)
    actual_harvest_date = Column(Date, nullable=True)
    soil_type = Column(String(100), nullable=True)
    irrigation_method = Column(String(100), nullable=True)
    growth_stage = Column(String(50), default="Sowing", nullable=False)
    status = Column(String(30), default="active", nullable=False, index=True)  # active, harvested, failed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    farmer = relationship("User", back_populates="crops")
    activities = relationship("FarmActivity", back_populates="crop", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="crop", cascade="all, delete-orphan")
    harvest_records = relationship("HarvestRecord", back_populates="crop", cascade="all, delete-orphan")
    health_observations = relationship("HealthObservation", back_populates="crop", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Crop {self.id} {self.name} ({self.status})>"
