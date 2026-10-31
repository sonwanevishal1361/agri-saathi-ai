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


def test_activity_listing_empty_state_for_new_farmer(db_session, farmer_b):
    """Verify farmer with zero activities receives an empty list cleanly without error."""
    acts = ActivityService.list_activities(db_session, farmer_b.id, limit=3)
    assert isinstance(acts, list)
    assert len(acts) == 0


def test_activity_listing_tenant_isolation(db_session, farmer_a, farmer_b):
    """Verify tenant isolation: Farmer A cannot view Farmer B's activities."""
    # Create an activity for Farmer A
    act_a = ActivityService.create_activity(
        db_session,
        farmer_a.id,
        ActivityCreate(
            activity_type="Irrigation",
            activity_date=date.today(),
            description="Drip irrigation 2 hours",
        ),
    )
    # Create an activity for Farmer B
    act_b = ActivityService.create_activity(
        db_session,
        farmer_b.id,
        ActivityCreate(
            activity_type="Spraying",
            activity_date=date.today(),
            description="Organic bio-fungicide spray",
        ),
    )

    acts_farmer_a = ActivityService.list_activities(db_session, farmer_a.id)
    acts_farmer_b = ActivityService.list_activities(db_session, farmer_b.id)

    # Farmer A only sees their own activity
    assert any(a.id == act_a.id for a in acts_farmer_a)
    assert not any(a.id == act_b.id for a in acts_farmer_a)

    # Farmer B only sees their own activity
    assert any(a.id == act_b.id for a in acts_farmer_b)
    assert not any(a.id == act_a.id for a in acts_farmer_b)


def test_list_activities_self_heals_missing_cost_column():
    """Regression test: verify list_activities self-heals when 'cost' column is missing from DB."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    eng = create_engine("sqlite:///:memory:")
    raw = eng.raw_connection()
    raw.execute(
        "CREATE TABLE farm_activities ("
        "id VARCHAR(36) PRIMARY KEY, "
        "farmer_id VARCHAR(36), "
        "crop_id VARCHAR(36), "
        "activity_type VARCHAR(50), "
        "activity_date DATE, "
        "description TEXT, "
        "quantity FLOAT, "
        "unit VARCHAR(30), "
        "product_name VARCHAR(100), "
        "notes TEXT, "
        "created_at DATETIME, "
        "updated_at DATETIME"
        ")"
    )
    raw.commit()

    Session = sessionmaker(bind=eng)
    session = Session()
    try:
        # Before self-healing, cost column is absent in DB table
        # list_activities detects missing column and applies ALTER TABLE on-the-fly
        results = ActivityService.list_activities(session, "test-farmer-id", limit=5)
        assert isinstance(results, list)
        assert len(results) == 0

        # Verify cost column now exists in the database
        from sqlalchemy import inspect
        cols = [c["name"] for c in inspect(eng).get_columns("farm_activities")]
        assert "cost" in cols
    finally:
        session.close()
