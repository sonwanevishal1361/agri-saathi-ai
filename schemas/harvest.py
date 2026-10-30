"""Pydantic schemas for Harvest Records."""

from datetime import date
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class HarvestCreate(BaseModel):
    crop_id: str
    harvest_date: date
    quantity: float = Field(..., gt=0, description="Harvested quantity must be greater than zero")
    quantity_unit: str = Field(default="Quintal", max_length=30)
    sale_quantity: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

    # Compatibility fields
    unit: Optional[str] = None
    selling_price_per_unit: Optional[float] = None
    buyer_name: Optional[str] = None
    quality_grade: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Unit mapping
            if not data.get("quantity_unit") and data.get("unit"):
                data["quantity_unit"] = str(data.get("unit")).strip()
            # Selling price mapping
            if data.get("selling_price") is None and data.get("selling_price_per_unit") is not None:
                data["selling_price"] = data.get("selling_price_per_unit")
            # If selling price is given, default sale quantity to quantity if not specified
            if data.get("selling_price") is not None and data.get("sale_quantity") is None:
                data["sale_quantity"] = data.get("quantity")
            # Extra buyer and grade notes
            extra_notes = []
            if data.get("buyer_name"):
                extra_notes.append(f"Buyer: {data.get('buyer_name')}")
            if data.get("quality_grade"):
                extra_notes.append(f"Grade: {data.get('quality_grade')}")
            if extra_notes:
                current_notes = data.get("notes") or ""
                data["notes"] = (current_notes + " | " + " | ".join(extra_notes)).strip(" | ")
        return data


class HarvestUpdate(BaseModel):
    harvest_date: Optional[date] = None
    quantity: Optional[float] = Field(None, gt=0)
    quantity_unit: Optional[str] = Field(None, max_length=30)
    sale_quantity: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class HarvestResponse(BaseModel):
    id: str
    farmer_id: str
    crop_id: str
    harvest_date: date
    quantity: float
    quantity_unit: str
    sale_quantity: Optional[float]
    selling_price: Optional[float]
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)
