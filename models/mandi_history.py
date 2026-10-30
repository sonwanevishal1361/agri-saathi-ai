"""Mandi market price history and cache database models."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class MandiPriceHistory(Base):
    """Historical snapshot of APMC mandi price arrivals for trend tracking."""

    __tablename__ = "mandi_price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    market = Column(String(150), nullable=False, index=True)
    commodity = Column(String(100), nullable=False, index=True)
    variety = Column(String(100), nullable=True)
    grade = Column(String(50), nullable=True)
    arrival_date = Column(String(20), nullable=False, index=True)
    min_price = Column(Float, nullable=False, default=0.0)
    max_price = Column(Float, nullable=False, default=0.0)
    modal_price = Column(Float, nullable=False, default=0.0)
    recorded_at = Column(DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "state", "district", "market", "commodity", "variety", "arrival_date",
            name="uq_mandi_history_entry"
        ),
    )

    def __repr__(self):
        return f"<MandiPriceHistory {self.market} - {self.commodity} ({self.arrival_date}): ₹{self.modal_price}>"


class MandiPriceCache(Base):
    """Database cache table for external mandi API responses."""

    __tablename__ = "mandi_price_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    response_json = Column(Text, nullable=False)
    cached_at = Column(DateTime, default=utc_now, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<MandiPriceCache key={self.cache_key} expires={self.expires_at}>"

