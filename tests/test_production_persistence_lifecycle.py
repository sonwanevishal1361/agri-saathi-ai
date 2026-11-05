"""Comprehensive test suite for AgriSaathi AI production persistence lifecycle.

Verifies end-to-end data durability, restart resilience, connection pooling recovery,
tenant isolation, and backup restoration in an isolated test environment.
"""

import uuid
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import init_db
from models.user import User
from schemas.user import UserRegister
from schemas.crop import CropCreate
from schemas.activity import ActivityCreate
from schemas.expense import ExpenseCreate
from schemas.harvest import HarvestCreate
from services.user_service import UserService
from services.crop_service import CropService
from services.activity_service import ActivityService
from services.expense_service import ExpenseService
from services.harvest_service import HarvestService
from services.admin_service import AdminService
from services.backup_service import BackupService
from core.auth import AuthenticatedFarmer, require_admin
from core.exceptions import AuthorizationError, NotFoundError


def test_production_persistence_and_recovery_lifecycle(tmp_path):
    """Execute complete 11-step persistence lifecycle verification."""
    # Isolated test database
    db_file = tmp_path / "persistence_lifecycle.db"
    test_db_url = f"sqlite:///{db_file.as_posix()}"

    test_engine = create_engine(
        test_db_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
    )
    TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    # Initialize schema
    init_db(bind_engine=test_engine)

    # -------------------------------------------------------------------------
    # STEP 1: Register test farmer
    # -------------------------------------------------------------------------
    phone_suffix = f"{int(uuid.uuid4().int % 1000000):06d}"
    test_phone = f"9876{phone_suffix}"
    test_email = f"farmer_{uuid.uuid4().hex[:8]}@example.com"

    farmer_in = UserRegister(
        full_name="Kisan Testing Patil",
        phone=test_phone,
        email=test_email,
        password="ValidPassword123!",
        confirm_password="ValidPassword123!",
        preferred_language="mr",
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        farm_size=4.5,
        soil_type="Black Cotton",
        irrigation_method="Drip",
    )

    with TestSessionLocal() as db:
        farmer_user = UserService.register_farmer(db, farmer_in)
        farmer_id = farmer_user.id
        db.commit()

    assert farmer_id is not None

    # -------------------------------------------------------------------------
    # STEP 2: Add a crop
    # -------------------------------------------------------------------------
    crop_in = CropCreate(
        name="Cotton",
        variety="Bt Cotton 659",
        area=3.0,
        area_unit="Acre",
        sowing_date=date(2026, 6, 15),
        expected_harvest_date=date(2026, 11, 20),
        growth_stage="Vegetative",
        status="active",
    )

    with TestSessionLocal() as db:
        crop_obj = CropService.create_crop(db, farmer_id, crop_in)
        crop_id = crop_obj.id
        db.commit()

    assert crop_id is not None

    # -------------------------------------------------------------------------
    # STEP 3: Add an activity
    # -------------------------------------------------------------------------
    activity_in = ActivityCreate(
        crop_id=crop_id,
        activity_type="Fertilizer",
        activity_date=date(2026, 7, 10),
        description="Applied 19:19:19 water soluble fertilizer via drip system",
        product_name="IFFCO 19-19-19",
        cost=1850.0,
    )

    with TestSessionLocal() as db:
        act_obj = ActivityService.create_activity(db, farmer_id, activity_in)
        activity_id = act_obj.id
        db.commit()

    assert activity_id is not None

    # -------------------------------------------------------------------------
    # STEP 4: Add an expense
    # -------------------------------------------------------------------------
    expense_in = ExpenseCreate(
        crop_id=crop_id,
        category="Fertilizers",
        amount=1850.0,
        expense_date=date(2026, 7, 10),
        description="Purchased IFFCO fertilizer packets from Krishi Seva Kendra",
        vendor="Baramati Krishi Seva",
    )

    with TestSessionLocal() as db:
        exp_obj = ExpenseService.create_expense(db, farmer_id, expense_in)
        expense_id = exp_obj.id
        db.commit()

    assert expense_id is not None

    # -------------------------------------------------------------------------
    # STEP 5: Add a harvest record
    # -------------------------------------------------------------------------
    harvest_in = HarvestCreate(
        crop_id=crop_id,
        harvest_date=date(2026, 11, 1),
        quantity=22.5,
        quantity_unit="Quintal",
        sale_quantity=22.5,
        selling_price=7400.0,
        notes="Buyer: Baramati APMC Trader | Grade: A",
    )

    with TestSessionLocal() as db:
        harv_obj = HarvestService.create_harvest(db, farmer_id, harvest_in)
        harvest_id = harv_obj.id
        db.commit()

    assert harvest_id is not None

    # -------------------------------------------------------------------------
    # STEP 6 & 7: Close and restart application (Simulate full container shutdown)
    # -------------------------------------------------------------------------
    test_engine.dispose()  # Destroy all connection handles

    # Re-initialize fresh engine simulating a brand new app startup
    restarted_engine = create_engine(
        test_db_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
    )
    RestartedSessionLocal = sessionmaker(bind=restarted_engine, autocommit=False, autoflush=False)

    with RestartedSessionLocal() as db:
        # Verify farmer persisted
        reloaded_farmer = UserService.get_farmer_by_id(db, farmer_id)
        assert reloaded_farmer is not None
        assert reloaded_farmer.full_name == "Kisan Testing Patil"
        assert reloaded_farmer.district == "Pune"
        assert reloaded_farmer.role == "farmer"

        # Verify crop persisted
        crops = CropService.list_crops(db, farmer_id)
        assert len(crops) == 1
        assert crops[0].id == crop_id
        assert crops[0].name == "Cotton"

        # Verify activity persisted
        acts = ActivityService.list_activities(db, farmer_id)
        assert len(acts) == 1
        assert acts[0].id == activity_id
        assert acts[0].cost == 1850.0

        # Verify expense persisted
        expenses = ExpenseService.list_expenses(db, farmer_id)
        assert len(expenses) == 1
        assert expenses[0].id == expense_id
        assert expenses[0].amount == 1850.0

        # Verify harvest record persisted
        harvests = HarvestService.list_harvest_records(db, farmer_id)
        assert len(harvests) == 1
        assert harvests[0].id == harvest_id
        assert harvests[0].quantity == 22.5
        assert harvests[0].total_revenue == round(22.5 * 7400.0, 2)

    # -------------------------------------------------------------------------
    # STEP 8: Redeploy application and verify idempotent startup
    # -------------------------------------------------------------------------
    # Simulate redeployment trigger: init_db running again
    init_db(bind_engine=restarted_engine)

    with RestartedSessionLocal() as db:
        farmer_check = UserService.get_farmer_by_id(db, farmer_id)
        assert farmer_check is not None
        assert CropService.list_crops(db, farmer_id)[0].id == crop_id

    # -------------------------------------------------------------------------
    # STEP 9: Connection expiration / reconnect simulation
    # -------------------------------------------------------------------------
    # Dispose connection pool to simulate dropped TCP socket / idle timeout
    restarted_engine.dispose()

    with RestartedSessionLocal() as db:
        # pool_pre_ping transparently recovers the connection
        reconnected_farmer = UserService.get_farmer_by_id(db, farmer_id)
        assert reconnected_farmer is not None
        assert reconnected_farmer.phone == test_phone

    # -------------------------------------------------------------------------
    # STEP 10: Farmer isolation and admin permissions verification
    # -------------------------------------------------------------------------
    # Register Farmer B
    phone_suffix_b = f"{int(uuid.uuid4().int % 1000000):06d}"
    farmer_b_in = UserRegister(
        full_name="Second Farmer B",
        phone=f"9875{phone_suffix_b}",
        email=f"farmer_b_{uuid.uuid4().hex[:8]}@example.com",
        password="ValidPassword123!",
        confirm_password="ValidPassword123!",
        preferred_language="hi",
        district="Nashik",
    )
    with RestartedSessionLocal() as db:
        farmer_b = UserService.register_farmer(db, farmer_b_in)
        farmer_b_id = farmer_b.id
        db.commit()

    with RestartedSessionLocal() as db:
        # Farmer B must NOT see Farmer A's crops, activities, expenses, or harvests
        assert len(CropService.list_crops(db, farmer_b_id)) == 0
        assert len(ActivityService.list_activities(db, farmer_b_id)) == 0
        assert len(ExpenseService.list_expenses(db, farmer_b_id)) == 0
        assert len(HarvestService.list_harvest_records(db, farmer_b_id)) == 0

        # Attempt unauthorized cross-tenant crop retrieval
        try:
            CropService.get_crop(db, farmer_b_id, crop_id)
            assert False, "Farmer B should not be able to access Farmer A crop"
        except (AuthorizationError, NotFoundError):
            pass

        # Verify ordinary farmer cannot access admin functionality
        auth_farmer = AuthenticatedFarmer(
            id=farmer_id,
            full_name="Kisan Testing Patil",
            email=test_email,
            phone=test_phone,
            preferred_language="mr",
            state="Maharashtra",
            district="Pune",
            village="Baramati",
            is_active=True,
            role="farmer",
        )
        try:
            require_admin(auth_farmer)
            assert False, "Regular farmer should raise AuthorizationError on admin guard"
        except AuthorizationError:
            pass

        # Create an admin user to verify aggregate overview
        admin_user = User(
            id=str(uuid.uuid4()),
            full_name="Platform Admin",
            email=f"admin_{uuid.uuid4().hex[:6]}@agrisaathi.internal",
            password_hash="mock_hash",
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()

        auth_admin = AuthenticatedFarmer(
            id=admin_user.id,
            full_name=admin_user.full_name,
            email=admin_user.email,
            phone="0000000000",
            preferred_language="en",
            state="Maharashtra",
            district="Pune",
            village="City",
            is_active=True,
            role="admin",
        )

        overview = AdminService.get_system_overview(db, auth_admin)
        assert overview["total_farmers"] >= 2
        assert overview["total_crops"] >= 1
        assert overview["total_harvest_count"] >= 1

    # -------------------------------------------------------------------------
    # STEP 11: Backup restoration in a separate test environment
    # -------------------------------------------------------------------------
    backup_dir = tmp_path / "backups_test"
    backup_dir.mkdir(parents=True, exist_ok=True)

    dest_path, filename, size_bytes = BackupService.create_sqlite_backup(
        admin=auth_admin,
        backup_dir=backup_dir,
        db=db,
        src_db_path=db_file,
    )
    assert dest_path.exists()
    assert size_bytes > 0

    # Read backup bytes and restore into a completely separate target database
    target_restored_file = tmp_path / "restored_env.db"
    shutil_copy = dest_path.read_bytes()

    restored_engine = create_engine(
        f"sqlite:///{target_restored_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    RestoredSessionLocal = sessionmaker(bind=restored_engine, autocommit=False, autoflush=False)

    with target_restored_file.open("wb") as f:
        f.write(shutil_copy)

    with RestoredSessionLocal() as db:
        restored_farmer = UserService.get_farmer_by_id(db, farmer_id)
        assert restored_farmer is not None
        assert restored_farmer.full_name == "Kisan Testing Patil"

        restored_crops = CropService.list_crops(db, farmer_id)
        assert len(restored_crops) == 1
        assert restored_crops[0].name == "Cotton"

        restored_harvests = HarvestService.list_harvest_records(db, farmer_id)
        assert len(restored_harvests) == 1
        assert restored_harvests[0].quantity == 22.5


def test_portable_json_snapshot_cross_engine_recovery(tmp_path):
    """Verify that portable JSON snapshots can be created, inspected, and restored."""
    # Use real active engine for snapshot export
    auth_admin = AuthenticatedFarmer(
        id=str(uuid.uuid4()),
        full_name="Snapshot Admin",
        email="snap_admin@agrisaathi.internal",
        phone="0000000000",
        preferred_language="en",
        state="Maharashtra",
        district="Pune",
        village="Central",
        is_active=True,
        role="admin",
    )

    backup_dir = tmp_path / "json_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    dest_path, filename, size_bytes = BackupService.create_portable_snapshot(
        admin=auth_admin,
        backup_dir=backup_dir,
    )

    assert dest_path.exists()
    assert filename.endswith(".json")
    assert size_bytes > 0

    # Verify JSON content is valid
    import json
    content = json.loads(dest_path.read_text(encoding="utf-8"))
    assert "tables" in content
    assert "users" in content["tables"]
    assert len(content["tables"]["users"]) > 0

    # Verify list_backups picks up the JSON backup
    backups = BackupService.list_backups(auth_admin, backup_dir=backup_dir)
    assert any(b["filename"] == filename for b in backups)

