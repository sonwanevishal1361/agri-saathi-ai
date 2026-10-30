"""User/Farmer account database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    preferred_language = Column(String(10), default="en", nullable=False)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    farm_size = Column(Float, nullable=True)
    farm_area_unit = Column(String(20), default="Acre", nullable=False)
    soil_type = Column(String(100), nullable=True)
    irrigation_method = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships with cascade delete on farmer account deletion
    crops = relationship("Crop", back_populates="farmer", cascade="all, delete-orphan")
    activities = relationship("FarmActivity", back_populates="farmer", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="farmer", cascade="all, delete-orphan")
    harvest_records = relationship("HarvestRecord", back_populates="farmer", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="farmer", cascade="all, delete-orphan")
    health_observations = relationship("HealthObservation", back_populates="farmer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.id} {self.full_name}>"
