"""Test database initialization and automatic schema verification for Streamlit deployment."""

import uuid
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from core.database import init_db
from models.user import User
from schemas.user import UserRegister
from services.user_service import UserService


def test_init_db_creates_users_table(tmp_path: Path):
    """Verify that init_db creates the users table and all application tables on a blank database."""
    db_file = tmp_path / "test_agrisaathi.db"
    test_db_url = f"sqlite:///{db_file.as_posix()}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    # Before initialization, no tables should exist
    inspector_before = inspect(test_engine)
    assert len(inspector_before.get_table_names()) == 0

    # Initialize database
    init_db(bind_engine=test_engine)

    # Inspect after initialization
    inspector_after = inspect(test_engine)
    created_tables = inspector_after.get_table_names()

    # Verify critical users table is created
    assert "users" in created_tables

    # Verify all expected domain tables exist
    expected_tables = [
        "users",
        "crops",
        "farm_activities",
        "expenses",
        "harvest_records",
        "conversations",
        "messages",
        "crop_knowledge",
        "knowledge_documents",
        "health_observations",
        "mandi_price_history",
        "mandi_price_cache",
    ]
    for table_name in expected_tables:
        assert table_name in created_tables, f"Expected table '{table_name}' was not created!"


def test_init_db_is_idempotent(tmp_path: Path):
    """Verify that calling init_db repeatedly does not raise errors or alter existing tables."""
    db_file = tmp_path / "test_idempotent.db"
    test_db_url = f"sqlite:///{db_file.as_posix()}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    # First call
    init_db(bind_engine=test_engine)
    tables_run1 = inspect(test_engine).get_table_names()

    # Second call (idempotency check)
    init_db(bind_engine=test_engine)
    tables_run2 = inspect(test_engine).get_table_names()

    assert tables_run1 == tables_run2
    assert "users" in tables_run2


def test_user_registration_on_fresh_database(tmp_path: Path):
    """Verify farmer registration executes cleanly on a freshly initialized database without table errors."""
    db_file = tmp_path / "test_reg.db"
    test_db_url = f"sqlite:///{db_file.as_posix()}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    # Initialize tables
    init_db(bind_engine=test_engine)

    # Create Session factory bound to test engine
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSession()

    try:
        unique_phone = f"98{uuid.uuid4().int % 100000000:08d}"
        reg_data = UserRegister(
            full_name="Ramesh Patil",
            email=f"ramesh_{uuid.uuid4().hex[:6]}@example.com",
            phone=unique_phone,
            password="SecurePassword@123",
            confirm_password="SecurePassword@123",
            preferred_language="mr",
            state="Maharashtra",
            district="Nagpur",
            village="Katol",
            farm_size=5.5,
            farm_area_unit="Acre",
            soil_type="Black Cotton",
            irrigation_method="Drip",
        )

        user = UserService.register_farmer(session, reg_data)
        session.commit()

        assert user.id is not None
        assert user.full_name == "Ramesh Patil"
        assert user.phone == unique_phone

        # Query user back from database
        persisted = session.query(User).filter(User.phone == unique_phone).first()
        assert persisted is not None
        assert persisted.district == "Nagpur"
        assert persisted.preferred_language == "mr"
    finally:
        session.close()


def test_bootstrap_database_function():
    """Verify that the bootstrap_database function executes cleanly without throwing."""
    from core.database import bootstrap_database

    res = bootstrap_database()
    assert res is True
