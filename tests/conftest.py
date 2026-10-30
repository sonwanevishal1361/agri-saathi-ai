"""Pytest fixtures for AgriSaathi AI test suite."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from schemas.user import UserRegister
from schemas.crop import CropCreate
from services.user_service import UserService
from services.crop_service import CropService
from datetime import date, timedelta


@pytest.fixture(scope="function")
def db_session():
    """Create a pristine in-memory SQLite database session for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def farmer_a(db_session):
    """Create test farmer account A."""
    user = UserService.register_farmer(
        db_session,
        UserRegister(
            full_name="Tukaram Shinde",
            phone="9822001122",
            email="tukaram@example.com",
            password="StrongPassword123",
            confirm_password="StrongPassword123",
            preferred_language="mr",
            state="Maharashtra",
            district="Pune",
            village="Baramati",
            farm_size=4.5,
        ),
    )
    return user


@pytest.fixture(scope="function")
def farmer_b(db_session):
    """Create test farmer account B."""
    user = UserService.register_farmer(
        db_session,
        UserRegister(
            full_name="Harpreet Singh",
            phone="9811002233",
            email="harpreet@example.com",
            password="StrongPassword456",
            confirm_password="StrongPassword456",
            preferred_language="hi",
            state="Punjab",
            district="Ludhiana",
            village="Khanna",
            farm_size=8.0,
        ),
    )
    return user


@pytest.fixture(scope="function")
def crop_farmer_a(db_session, farmer_a):
    """Create test crop owned by Farmer A."""
    crop = CropService.create_crop(
        db_session,
        farmer_a.id,
        CropCreate(
            name="Cotton",
            variety="Ajit 155 Bt",
            area=2.0,
            sowing_date=date.today() - timedelta(days=60),
            expected_harvest_date=date.today() + timedelta(days=60),
            growth_stage="Flowering",
            soil_type="Black Clay",
            irrigation_method="Drip",
        ),
    )
    return crop

