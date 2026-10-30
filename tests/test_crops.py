"""Tests for Crop CRUD and validation."""

import pytest
from datetime import date
from schemas.crop import CropCreate, CropUpdate
from services.crop_service import CropService
from core.exceptions import NotFoundError


def test_crop_creation(db_session, farmer_a):
    crop = CropService.create_crop(
        db_session,
        farmer_a.id,
        CropCreate(
            name="Soybean",
            variety="JS-335",
            area=3.5,
            sowing_date=date(2026, 6, 25),
            expected_harvest_date=date(2026, 10, 15),
            growth_stage="Vegetative",
        ),
    )
    assert crop.id is not None
    assert crop.name == "Soybean"
    assert crop.area == 3.5
    assert crop.status == "active"


def test_invalid_harvest_date_rejected():
    with pytest.raises(ValueError, match="Expected harvest date cannot be earlier"):
        CropCreate(
            name="Wheat",
            area=1.0,
            sowing_date=date(2026, 11, 15),
            expected_harvest_date=date(2026, 11, 1),  # Earlier than sowing
        )


def test_invalid_area_rejected():
    with pytest.raises(ValueError):
        CropCreate(
            name="Tomato",
            area=0.0,  # Must be gt=0
            sowing_date=date.today(),
        )


def test_crop_update(db_session, farmer_a, crop_farmer_a):
    updated = CropService.update_crop(
        db_session,
        farmer_a.id,
        crop_farmer_a.id,
        CropUpdate(growth_stage="Boll Formation", status="active"),
    )
    assert updated.growth_stage == "Boll Formation"


def test_crop_delete(db_session, farmer_a, crop_farmer_a):
    res = CropService.delete_crop(db_session, farmer_a.id, crop_farmer_a.id)
    assert res is True
    with pytest.raises(NotFoundError):
        CropService.get_crop(db_session, farmer_a.id, crop_farmer_a.id)


def test_crop_filtering_by_status(db_session, farmer_a):
    # Active crop
    CropService.create_crop(
        db_session,
        farmer_a.id,
        CropCreate(name="Crop 1", area=1.0, sowing_date=date.today(), status="active"),
    )
    # Harvested crop
    CropService.create_crop(
        db_session,
        farmer_a.id,
        CropCreate(name="Crop 2", area=2.0, sowing_date=date.today(), status="harvested"),
    )

    active_list = CropService.list_crops(db_session, farmer_a.id, status="active")
    harvested_list = CropService.list_crops(db_session, farmer_a.id, status="harvested")

    assert len(active_list) == 1
    assert active_list[0].name == "Crop 1"
    assert len(harvested_list) == 1
    assert harvested_list[0].name == "Crop 2"
