"""Pydantic schemas for Farm Activities / Diary."""

from datetime import date
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class ActivityCreate(BaseModel):
    crop_id: Optional[str] = None
    activity_type: str = Field(..., min_length=2, max_length=50)
    activity_date: date
    description: str = Field(default="", min_length=0)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=30)
    product_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    cost: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            desc = data.get("description") or data.get("notes")
            if not desc or not str(desc).strip():
                act_t = data.get("activity_type", "Farm")
                desc = f"{act_t} काम पूर्ण केले"
            data["description"] = str(desc).strip()
        return data


class ActivityUpdate(BaseModel):
    crop_id: Optional[str] = None
    activity_type: Optional[str] = Field(None, min_length=2, max_length=50)
    activity_date: Optional[date] = None
    description: Optional[str] = Field(None, min_length=1)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=30)
    product_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    cost: Optional[float] = Field(None, ge=0)


class ActivityResponse(BaseModel):
    id: str
    farmer_id: str
    crop_id: Optional[str]
    activity_type: str
    activity_date: date
    description: str
    quantity: Optional[float]
    unit: Optional[str]
    product_name: Optional[str]
    notes: Optional[str]
    cost: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
