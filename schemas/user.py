"""Pydantic schemas for Farmer accounts and authentication."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)
    preferred_language: str = Field(default="en", max_length=10)
    state: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    village: Optional[str] = Field(None, max_length=100)
    farm_size: Optional[float] = Field(None, ge=0)
    farm_area_unit: str = Field(default="Acre", max_length=20)
    soil_type: Optional[str] = Field(None, max_length=100)
    irrigation_method: Optional[str] = Field(None, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip().lower()
            if "@" not in v:
                raise ValueError("Invalid email format.")
        return v or None

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        if v:
            cleaned = "".join(ch for ch in v if ch.isdigit() or ch == "+")
            if len(cleaned) < 10:
                raise ValueError("Phone number must contain at least 10 digits.")
            return cleaned
        return None

    @model_validator(mode="after")
    def validate_identity_and_passwords(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone number must be provided for registration.")
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    identifier: str = Field(..., min_length=3, description="Email or Phone Number")
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    preferred_language: Optional[str] = Field(None, max_length=10)
    state: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    village: Optional[str] = Field(None, max_length=100)
    farm_size: Optional[float] = Field(None, ge=0)
    farm_area_unit: Optional[str] = Field(None, max_length=20)
    soil_type: Optional[str] = Field(None, max_length=100)
    irrigation_method: Optional[str] = Field(None, max_length=100)


class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)
    confirm_new_password: str = Field(..., min_length=6, max_length=128)

    @model_validator(mode="after")
    def validate_matching_passwords(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match.")
        if self.old_password == self.new_password:
            raise ValueError("New password must be different from current password.")
        return self


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    preferred_language: str
    state: Optional[str]
    district: Optional[str]
    village: Optional[str]
    farm_size: Optional[float]
    farm_area_unit: str
    soil_type: Optional[str]
    irrigation_method: Optional[str]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
