"""Pydantic schemas for Crop management."""

from datetime import date, timedelta
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict


class CropCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    variety: Optional[str] = Field(None, max_length=100)
    plot_name: Optional[str] = Field(None, max_length=100)
    area: float = Field(..., gt=0, description="Area planted must be greater than zero")
    area_unit: str = Field(default="Acre", max_length=20)
    sowing_date: date
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    soil_type: Optional[str] = Field(None, max_length=100)
    irrigation_method: Optional[str] = Field(None, max_length=100)
    growth_stage: str = Field(default="Sowing", max_length=50)
    status: str = Field(default="active", max_length=30)  # active, harvested, failed
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_harvest_dates(self):
        if self.expected_harvest_date is None:
            self.expected_harvest_date = self.sowing_date + timedelta(days=120)
        elif self.expected_harvest_date < self.sowing_date:
            raise ValueError("Expected harvest date cannot be earlier than sowing date.")
        if self.actual_harvest_date and self.actual_harvest_date < self.sowing_date:
            raise ValueError("Actual harvest date cannot be earlier than sowing date.")
        return self


class CropUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    variety: Optional[str] = Field(None, max_length=100)
    plot_name: Optional[str] = Field(None, max_length=100)
    area: Optional[float] = Field(None, gt=0)
    area_unit: Optional[str] = Field(None, max_length=20)
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    soil_type: Optional[str] = Field(None, max_length=100)
    irrigation_method: Optional[str] = Field(None, max_length=100)
    growth_stage: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=30)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.sowing_date and self.expected_harvest_date:
            if self.expected_harvest_date < self.sowing_date:
                raise ValueError("Expected harvest date cannot be earlier than sowing date.")
        return self


class CropResponse(BaseModel):
    id: str
    farmer_id: str
    name: str
    variety: Optional[str]
    plot_name: Optional[str]
    area: float
    area_unit: str
    sowing_date: date
    expected_harvest_date: date
    actual_harvest_date: Optional[date]
    soil_type: Optional[str]
    irrigation_method: Optional[str]
    growth_stage: str
    status: str
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)
