"""Farm activities / diary database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class FarmActivity(Base):
    __tablename__ = "farm_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="SET NULL"), nullable=True, index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # Sowing, Irrigation, Fertilizer, Spraying, etc.
    activity_date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=False)
    quantity = Column(Float, nullable=True)
    unit = Column(String(30), nullable=True)
    product_name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    farmer = relationship("User", back_populates="activities")
    crop = relationship("Crop", back_populates="activities")

    @property
    def cost(self):
        """Compatibility property for activity cost."""
        return None

    def __repr__(self):
        return f"<FarmActivity {self.id} {self.activity_type} on {self.activity_date}>"
