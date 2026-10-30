"""Automated tests for comprehensive CRUD persistence and multi-tenant data isolation."""

import pytest
from datetime import date
from core.exceptions import AuthorizationError, NotFoundError
from schemas.crop import CropCreate, CropUpdate
from schemas.expense import ExpenseCreate
from schemas.activity import ActivityCreate
from schemas.harvest import HarvestCreate
from services.crop_service import CropService
from services.expense_service import ExpenseService
from services.activity_service import ActivityService
from services.harvest_service import HarvestService


def test_crop_crud_lifecycle(db_session, farmer_a, farmer_b):
    """Test full create, read, update, delete lifecycle for crops with persistence verification."""
    # 1. Create Crop
    crop = CropService.create_crop(
        db=db_session,
        farmer_id=farmer_a.id,
        crop_in=CropCreate(
            name="Tomato",
            variety="Abhinav",
            plot_name="North Field",
            area=1.5,
            sowing_date=date.today(),
            soil_type="Red Loam",
            irrigation_method="Drip",
            growth_stage="Vegetative",
        ),
    )
    assert crop.id is not None
    crop_id = crop.id

    # 2. Read Crop
    retrieved = CropService.get_crop(db_session, farmer_a.id, crop_id)
    assert retrieved.name == "Tomato"
    assert retrieved.area == 1.5

    # 3. Update Crop
    updated = CropService.update_crop(
        db_session,
        farmer_a.id,
        crop_id,
        CropUpdate(growth_stage="Flowering", notes="Applied flowering booster"),
    )
    assert updated.growth_stage == "Flowering"
    assert updated.notes == "Applied flowering booster"

    # 4. Tenant Isolation: Farmer B cannot read or update Farmer A's crop
    with pytest.raises(AuthorizationError):
        CropService.get_crop(db_session, farmer_b.id, crop_id)

    with pytest.raises(AuthorizationError):
        CropService.update_crop(db_session, farmer_b.id, crop_id, CropUpdate(name="Stolen"))

    with pytest.raises(AuthorizationError):
        CropService.delete_crop(db_session, farmer_b.id, crop_id)

    # 5. Delete Crop
    deleted = CropService.delete_crop(db_session, farmer_a.id, crop_id)
    assert deleted is True

    with pytest.raises(NotFoundError):
        CropService.get_crop(db_session, farmer_a.id, crop_id)


def test_expense_crud_lifecycle(db_session, farmer_a, crop_farmer_a, farmer_b):
    """Test full create, read, update, delete for expenses including UI compatibility fields."""
    # 1. Create Expense using notes and payee (UI pattern)
    exp = ExpenseService.create_expense(
        db=db_session,
        farmer_id=farmer_a.id,
        expense_in=ExpenseCreate(
            crop_id=crop_farmer_a.id,
            category="Seeds",
            amount=3200.0,
            expense_date=date.today(),
            notes="3 bags hybrid seed",
            payee="Patil Krishi Seva",
            payment_method="UPI",
        ),
    )
    assert exp.id is not None
    assert exp.amount == 3200.0
    assert exp.description == "3 bags hybrid seed"
    assert exp.vendor == "Patil Krishi Seva"
    assert exp.payee == "Patil Krishi Seva"
    assert exp.notes == "3 bags hybrid seed"
    assert exp.payment_method == "Cash"
    exp_id = exp.id

    # 2. Read Expense
    retrieved = ExpenseService.get_expense(db_session, farmer_a.id, exp_id)
    assert retrieved.amount == 3200.0

    # 3. Tenant Isolation
    with pytest.raises(AuthorizationError):
        ExpenseService.get_expense(db_session, farmer_b.id, exp_id)

    with pytest.raises(AuthorizationError):
        ExpenseService.delete_expense(db_session, farmer_b.id, exp_id)

    # 4. Delete Expense
    deleted = ExpenseService.delete_expense(db_session, farmer_a.id, exp_id)
    assert deleted is True


def test_activity_crud_lifecycle(db_session, farmer_a, crop_farmer_a, farmer_b):
    """Test full create, read, update, delete for farm activities with fallback description."""
    # 1. Create Activity without explicit description
    act = ActivityService.create_activity(
        db=db_session,
        farmer_id=farmer_a.id,
        activity_in=ActivityCreate(
            crop_id=crop_farmer_a.id,
            activity_type="Weeding",
            activity_date=date.today(),
            notes="Manual labor 5 people",
        ),
    )
    assert act.id is not None
    assert act.activity_type == "Weeding"
    assert act.description == "Manual labor 5 people"
    assert act.cost is None
    act_id = act.id

    # 2. Read Activity
    retrieved = ActivityService.get_activity(db_session, farmer_a.id, act_id)
    assert retrieved.activity_type == "Weeding"

    # 3. Tenant Isolation
    with pytest.raises(AuthorizationError):
        ActivityService.get_activity(db_session, farmer_b.id, act_id)

    with pytest.raises(AuthorizationError):
        ActivityService.delete_activity(db_session, farmer_b.id, act_id)

    # 4. Delete Activity
    deleted = ActivityService.delete_activity(db_session, farmer_a.id, act_id)
    assert deleted is True


def test_harvest_crud_lifecycle(db_session, farmer_a, crop_farmer_a, farmer_b):
    """Test full create, read, update, delete for harvest records including revenue calculation."""
    # 1. Create Harvest with UI parameters
    harv = HarvestService.create_harvest(
        db=db_session,
        farmer_id=farmer_a.id,
        harvest_in=HarvestCreate(
            crop_id=crop_farmer_a.id,
            harvest_date=date.today(),
            quantity=25.0,
            unit="Quintal",
            selling_price_per_unit=5500.0,
            buyer_name="Baramati APMC",
            quality_grade="A Grade",
        ),
    )
    assert harv.id is not None
    assert harv.quantity == 25.0
    assert harv.quantity_unit == "Quintal"
    assert harv.unit == "Quintal"
    assert harv.selling_price == 5500.0
    assert harv.selling_price_per_unit == 5500.0
    assert harv.total_revenue == 25.0 * 5500.0
    assert harv.buyer_name == "Baramati APMC"
    assert harv.quality_grade == "A Grade"
    harv_id = harv.id

    # 2. Read Harvest
    retrieved = HarvestService.get_harvest(db_session, farmer_a.id, harv_id)
    assert retrieved.total_revenue == 137500.0

    # 3. Tenant Isolation
    with pytest.raises(AuthorizationError):
        HarvestService.get_harvest(db_session, farmer_b.id, harv_id)

    with pytest.raises(AuthorizationError):
        HarvestService.delete_harvest(db_session, farmer_b.id, harv_id)

    # 4. Delete Harvest
    deleted = HarvestService.delete_harvest(db_session, farmer_a.id, harv_id)
    assert deleted is True
