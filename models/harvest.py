"""Harvest and yield records database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class HarvestRecord(Base):
    __tablename__ = "harvest_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True)
    harvest_date = Column(Date, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    quantity_unit = Column(String(30), default="Quintal", nullable=False)  # Quintal, Kg, Ton, Bags
    sale_quantity = Column(Float, nullable=True)
    selling_price = Column(Float, nullable=True)  # Unit price or total sale revenue
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    farmer = relationship("User", back_populates="harvest_records")
    crop = relationship("Crop", back_populates="harvest_records")

    @property
    def total_revenue(self) -> float:
        """Calculate recorded gross revenue from harvest sales."""
        if self.selling_price is None:
            return 0.0
        qty = self.sale_quantity if (self.sale_quantity is not None and self.sale_quantity > 0) else self.quantity
        return round(float(qty) * float(self.selling_price), 2)

    @property
    def unit(self) -> str:
        """Compatibility property for quantity_unit."""
        return self.quantity_unit

    @property
    def selling_price_per_unit(self):
        """Compatibility property for selling_price."""
        return self.selling_price

    @property
    def buyer_name(self):
        """Compatibility property for buyer extracted from notes."""
        if self.notes and "Buyer: " in self.notes:
            part = self.notes.split("Buyer: ")[1]
            for sep in [" | ", ", Grade:", ","]:
                if sep in part:
                    part = part.split(sep)[0]
            return part.strip()
        return None

    @property
    def quality_grade(self):
        """Compatibility property for quality grade extracted from notes."""
        if self.notes and "Grade: " in self.notes:
            return self.notes.split("Grade: ")[1].split(" | ")[0].strip()
        return "Standard"

    def __repr__(self):
        return f"<HarvestRecord {self.id} {self.quantity} {self.quantity_unit}>"
