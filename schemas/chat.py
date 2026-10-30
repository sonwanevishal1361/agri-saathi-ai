"""Pydantic schemas for AI Assistant Chat."""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default="New Farming Query", max_length=200)
    preferred_language: str = Field(default="en", max_length=10)


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    crop_id: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []
    crop_context_used: Optional[str] = None
