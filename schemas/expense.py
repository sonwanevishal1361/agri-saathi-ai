"""Pydantic schemas for Farm Expenses."""

from datetime import date
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class ExpenseCreate(BaseModel):
    crop_id: Optional[str] = None
    category: str = Field(..., min_length=2, max_length=50)
    amount: float = Field(..., ge=0, description="Amount must be non-negative")
    currency: str = Field(default="INR", max_length=10)
    expense_date: date
    description: str = Field(default="Farm Expense", min_length=1)
    vendor: Optional[str] = Field(None, max_length=100)
    payee: Optional[str] = None
    notes: Optional[str] = None
    payment_method: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # If description missing but notes provided, use notes or fallback
            desc = data.get("description") or data.get("notes")
            if not desc or not str(desc).strip():
                cat = data.get("category", "Farm")
                desc = f"{cat} expense"
            data["description"] = str(desc).strip()

            # If vendor missing but payee provided, use payee
            if not data.get("vendor") and data.get("payee"):
                data["vendor"] = str(data.get("payee")).strip()
        return data


class ExpenseUpdate(BaseModel):
    crop_id: Optional[str] = None
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    amount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    expense_date: Optional[date] = None
    description: Optional[str] = Field(None, min_length=1)
    vendor: Optional[str] = Field(None, max_length=100)


class ExpenseResponse(BaseModel):
    id: str
    farmer_id: str
    crop_id: Optional[str]
    category: str
    amount: float
    currency: str
    expense_date: date
    description: str
    vendor: Optional[str]

    model_config = ConfigDict(from_attributes=True)
