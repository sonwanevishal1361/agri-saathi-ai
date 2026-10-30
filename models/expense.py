"""Farm expense tracking database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="SET NULL"), nullable=True, index=True)
    category = Column(String(50), nullable=False, index=True)  # Seeds, Fertilizers, Labor, etc.
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    expense_date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=False)
    vendor = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    farmer = relationship("User", back_populates="expenses")
    crop = relationship("Crop", back_populates="expenses")

    @property
    def payee(self):
        """Compatibility property for vendor."""
        return self.vendor

    @property
    def notes(self):
        """Compatibility property for description."""
        return self.description

    @property
    def payment_method(self):
        """Default payment method representation."""
        return "Cash"

    def __repr__(self):
        return f"<Expense {self.id} ₹{self.amount} ({self.category})>"
