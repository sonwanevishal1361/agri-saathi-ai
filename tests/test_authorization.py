"""Tests for multi-farmer authorization boundaries and tenant isolation."""

import pytest
from core.exceptions import AuthorizationError
from services.crop_service import CropService
from services.activity_service import ActivityService
from services.expense_service import ExpenseService
from services.harvest_service import HarvestService
from services.chat_service import ChatService
from schemas.crop import CropUpdate
from schemas.activity import ActivityCreate, ActivityUpdate
from schemas.expense import ExpenseCreate, ExpenseUpdate
from schemas.harvest import HarvestCreate
from datetime import date


def test_cross_farmer_crop_access_denied(db_session, farmer_a, farmer_b, crop_farmer_a):
    # Farmer A can access own crop
    own_crop = CropService.get_crop(db_session, farmer_a.id, crop_farmer_a.id)
    assert own_crop.id == crop_farmer_a.id

    # Farmer B cannot read Farmer A's crop
    with pytest.raises(AuthorizationError):
        CropService.get_crop(db_session, farmer_b.id, crop_farmer_a.id)

    # Farmer B cannot update Farmer A's crop
    with pytest.raises(AuthorizationError):
        CropService.update_crop(db_session, farmer_b.id, crop_farmer_a.id, CropUpdate(name="Hacked"))

    # Farmer B cannot delete Farmer A's crop
    with pytest.raises(AuthorizationError):
        CropService.delete_crop(db_session, farmer_b.id, crop_farmer_a.id)


def test_cross_farmer_activity_access_denied(db_session, farmer_a, farmer_b, crop_farmer_a):
    # Create activity for farmer A
    act = ActivityService.create_activity(
        db_session,
        farmer_a.id,
        ActivityCreate(
            crop_id=crop_farmer_a.id,
            activity_type="Weeding",
            activity_date=date.today(),
            description="Weeding work",
        ),
    )

    # Farmer B cannot get Farmer A's activity
    with pytest.raises(AuthorizationError):
        ActivityService.get_activity(db_session, farmer_b.id, act.id)

    # Farmer B cannot update Farmer A's activity
    with pytest.raises(AuthorizationError):
        ActivityService.update_activity(db_session, farmer_b.id, act.id, ActivityUpdate(description="Modified"))

    # Farmer B cannot delete Farmer A's activity
    with pytest.raises(AuthorizationError):
        ActivityService.delete_activity(db_session, farmer_b.id, act.id)


def test_cross_farmer_expense_access_denied(db_session, farmer_a, farmer_b, crop_farmer_a):
    # Create expense for farmer A
    exp = ExpenseService.create_expense(
        db_session,
        farmer_a.id,
        ExpenseCreate(
            crop_id=crop_farmer_a.id,
            category="Fertilizers",
            amount=1500.0,
            expense_date=date.today(),
            description="Fertilizer bag",
        ),
    )

    # Farmer B cannot get Farmer A's expense
    with pytest.raises(AuthorizationError):
        ExpenseService.get_expense(db_session, farmer_b.id, exp.id)

    # Farmer B cannot update Farmer A's expense
    with pytest.raises(AuthorizationError):
        ExpenseService.update_expense(db_session, farmer_b.id, exp.id, ExpenseUpdate(amount=2000.0))

    # Farmer B cannot delete Farmer A's expense
    with pytest.raises(AuthorizationError):
        ExpenseService.delete_expense(db_session, farmer_b.id, exp.id)


def test_cross_farmer_harvest_access_denied(db_session, farmer_a, farmer_b, crop_farmer_a):
    # Create harvest record for farmer A
    harv = HarvestService.create_harvest(
        db_session,
        farmer_a.id,
        HarvestCreate(
            crop_id=crop_farmer_a.id,
            harvest_date=date.today(),
            quantity=10.0,
            quantity_unit="Quintal",
            selling_price=7000.0,
        ),
    )

    # Farmer B cannot get Farmer A's harvest record
    with pytest.raises(AuthorizationError):
        HarvestService.get_harvest(db_session, farmer_b.id, harv.id)

    # Farmer B cannot delete Farmer A's harvest record
    with pytest.raises(AuthorizationError):
        HarvestService.delete_harvest(db_session, farmer_b.id, harv.id)


def test_cross_farmer_conversation_access_denied(db_session, farmer_a, farmer_b):
    # Create conversation for farmer A
    conv = ChatService.create_conversation(db_session, farmer_a.id, title="Farmer A Private Chat")

    # Farmer B cannot read Farmer A's conversation
    with pytest.raises(AuthorizationError):
        ChatService.get_conversation(db_session, farmer_b.id, conv.id)

    # Farmer B cannot delete Farmer A's conversation
    with pytest.raises(AuthorizationError):
        ChatService.delete_conversation(db_session, farmer_b.id, conv.id)
