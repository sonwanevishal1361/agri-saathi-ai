"""Test suite verifying farmer registration persistence, restart survival, and admin panel retrieval."""

import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base, init_db
from core.auth import AuthenticatedFarmer
from schemas.user import UserRegister
from services.user_service import UserService
from services.admin_service import AdminService
import models  # noqa: F401


def test_farmer_persistence_across_app_restarts(tmp_path):
    """Verify that a registered farmer persists across database engine reboots and is visible in Admin Panel."""
    test_db_file = tmp_path / "persistence_test.db"
    test_db_url = f"sqlite:///{test_db_file.as_posix()}"

    # Engine 1: Initial app startup & registration
    engine1 = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine1)
    init_db(bind_engine=engine1)

    Session1 = sessionmaker(bind=engine1)
    unique_suffix = uuid.uuid4().hex[:6]
    test_phone = f"9876{int(uuid.uuid4().int % 1000000):06d}"
    test_email = f"farmer_{unique_suffix}@synthetic-test.local"

    with Session1() as session:
        # Register synthetic test farmer
        reg_input = UserRegister(
            full_name=f"Automated Test Farmer {unique_suffix}",
            phone=test_phone,
            email=test_email,
            password="TestPassword@123",
            confirm_password="TestPassword@123",
            preferred_language="en",
            state="Maharashtra",
            district="Pune",
            village="Sample Village",
            farm_size=3.5,
        )
        new_farmer = UserService.register_farmer(session, reg_input)
        assert new_farmer.id is not None
        assert new_farmer.role == "farmer"
        assert new_farmer.is_active is True
        farmer_id = new_farmer.id

    # Simulate App Shutdown / Container Restart
    engine1.dispose()

    # Engine 2: Rebooted app instance reconnecting to persistent storage
    engine2 = create_engine(test_db_url, connect_args={"check_same_thread": False})
    init_db(bind_engine=engine2)
    Session2 = sessionmaker(bind=engine2)

    admin_session_identity = AuthenticatedFarmer(
        id=str(uuid.uuid4()),
        full_name="Lead System Administrator",
        email="admin@agrisaathi.local",
        phone="9999999999",
        preferred_language="en",
        state="Maharashtra",
        district="Pune",
        village="Headquarters",
        is_active=True,
        role="admin",
    )

    with Session2() as session:
        # Verify farmer persisted across restart
        recovered_farmer = UserService.get_farmer_by_id(session, farmer_id)
        assert recovered_farmer is not None
        assert recovered_farmer.phone == test_phone
        assert recovered_farmer.email == test_email
        assert recovered_farmer.full_name == f"Automated Test Farmer {unique_suffix}"

        # Verify Admin Panel retrieves the farmer
        farmers_list, total_count = AdminService.list_farmers(
            db=session,
            admin=admin_session_identity,
            search=unique_suffix,
        )
        assert total_count == 1
        assert len(farmers_list) == 1
        assert farmers_list[0]["id"] == farmer_id
        assert farmers_list[0]["phone"] == test_phone

        # Verify System Overview KPI reflects the farmer
        overview = AdminService.get_system_overview(session, admin_session_identity)
        assert overview["total_farmers"] >= 1
        assert overview["active_farmers"] >= 1

    engine2.dispose()
