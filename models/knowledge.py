"""Knowledge library and RAG knowledge documents models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text
from core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class CropKnowledge(Base):
    __tablename__ = "crop_knowledge"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_name = Column(String(100), unique=True, nullable=False, index=True)
    scientific_name = Column(String(150), nullable=True)
    description = Column(Text, nullable=False)
    soil_requirements = Column(Text, nullable=False)
    climate_requirements = Column(Text, nullable=False)
    sowing_information = Column(Text, nullable=False)
    irrigation_information = Column(Text, nullable=False)
    nutrient_management = Column(Text, nullable=False)
    pest_disease_information = Column(Text, nullable=False)
    harvesting_information = Column(Text, nullable=False)
    source_name = Column(String(150), nullable=False)
    source_url = Column(String(255), nullable=True)
    verification_status = Column(String(50), default="Verified", nullable=False)
    last_verified_at = Column(DateTime, default=utc_now, nullable=False)

    def __repr__(self):
        return f"<CropKnowledge {self.crop_name}>"


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source_name = Column(String(150), nullable=False)
    source_url = Column(String(255), nullable=True)
    language = Column(String(10), default="en", nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)  # pest_control, soil_health, government_schemes, etc.
    verification_status = Column(String(50), default="Verified", nullable=False)
    last_verified_at = Column(DateTime, default=utc_now, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    def __repr__(self):
        return f"<KnowledgeDocument {self.title}>"
