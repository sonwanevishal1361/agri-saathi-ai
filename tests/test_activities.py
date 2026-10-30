"""Tests for Farm Activities and Diary logging."""

from datetime import date
from schemas.activity import ActivityCreate
from services.activity_service import ActivityService


def test_activity_creation(db_session, farmer_a, crop_farmer_a):
    act = ActivityService.create_activity(
        db_session,
        farmer_a.id,
        ActivityCreate(
            crop_id=crop_farmer_a.id,
            activity_type="Fertilizer Application",
            activity_date=date.today(),
            description="Applied 1 bag of DAP along drip line",
            quantity=50.0,
            unit="Kg",
            product_name="DAP 18:46:0",
        ),
    )
    assert act.id is not None
    assert act.activity_type == "Fertilizer Application"
    assert act.quantity == 50.0
    assert act.unit == "Kg"
    assert act.product_name == "DAP 18:46:0"


def test_activity_listing_and_filtering(db_session, farmer_a, crop_farmer_a):
    ActivityService.create_activity(
        db_session,
        farmer_a.id,
        ActivityCreate(
            crop_id=crop_farmer_a.id,
            activity_type="Weeding",
            activity_date=date.today(),
            description="Manual weeding by farm labor",
        ),
    )
    ActivityService.create_activity(
        db_session,
        farmer_a.id,
        ActivityCreate(
            crop_id=None,
            activity_type="Ploughing",
            activity_date=date.today(),
            description="Field tractor ploughing before sowing",
        ),
    )

    all_acts = ActivityService.list_activities(db_session, farmer_a.id)
    assert len(all_acts) == 2

    crop_acts = ActivityService.list_activities(db_session, farmer_a.id, crop_id=crop_farmer_a.id)
    assert len(crop_acts) == 1
    assert crop_acts[0].activity_type == "Weeding"


def test_activity_deletion(db_session, farmer_a):
    act = ActivityService.create_activity(
        db_session,
        farmer_a.id,
        ActivityCreate(
            activity_type="Spraying",
            activity_date=date.today(),
            description="Sprayed neem oil 5ml/L",
        ),
    )
    res = ActivityService.delete_activity(db_session, farmer_a.id, act.id)
    assert res is True
    assert len(ActivityService.list_activities(db_session, farmer_a.id)) == 0
