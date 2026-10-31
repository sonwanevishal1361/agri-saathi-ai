"""Automated test suite for Developer Admin Panel, RBAC, Data Exports, and Backups."""

import io
import json
import pytest
import pandas as pd
from sqlalchemy.orm import Session

from core.auth import AuthenticatedFarmer, require_admin
from core.exceptions import AuthorizationError
from models.user import User
from models.admin_log import AdminAuditLog
from services.admin_service import AdminService
from services.backup_service import BackupService
from services.user_service import UserService


@pytest.fixture
def admin_user(db_session: Session) -> AuthenticatedFarmer:
    """Fixture providing a verified admin user."""
    u = db_session.query(User).filter(User.role == "admin").first()
    if not u:
        u = UserService.seed_admin_if_missing(db_session)

    return AuthenticatedFarmer(
        id=u.id,
        full_name=u.full_name,
        email=u.email,
        phone=u.phone,
        preferred_language="en",
        state="Maharashtra",
        district="Pune",
        village="HQ",
        is_active=True,
        role="admin",
    )


@pytest.fixture
def regular_farmer(db_session: Session) -> AuthenticatedFarmer:
    """Fixture providing a regular farmer without admin privileges."""
    farmer_user = db_session.query(User).filter(User.role == "farmer").first()
    if not farmer_user:
        # Create a test farmer
        from core.security import hash_password
        farmer_user = User(
            full_name="Test Farmer RBAC",
            phone="9111122222",
            email="farmer_rbac@example.com",
            password_hash=hash_password("Farmer@123"),
            state="Maharashtra",
            district="Wardha",
            village="Seloo",
            role="farmer",
            is_active=True,
        )
        db_session.add(farmer_user)
        db_session.commit()
        db_session.refresh(farmer_user)

    return AuthenticatedFarmer(
        id=farmer_user.id,
        full_name=farmer_user.full_name,
        email=farmer_user.email,
        phone=farmer_user.phone,
        preferred_language="mr",
        state=farmer_user.state,
        district=farmer_user.district,
        village=farmer_user.village,
        is_active=True,
        role="farmer",
    )


def test_require_admin_guard():
    """Verify require_admin strictly permits admins and rejects regular farmers and unauthenticated callers."""
    admin = AuthenticatedFarmer(
        id="a1", full_name="Admin", email="a@t.com", phone="1",
        preferred_language="en", state="MH", district="Pune", village="V",
        is_active=True, role="admin",
    )
    assert admin.is_admin is True
    require_admin(admin)  # Must not raise

    farmer = AuthenticatedFarmer(
        id="f1", full_name="Farmer", email="f@t.com", phone="2",
        preferred_language="mr", state="MH", district="Wardha", village="V",
        is_active=True, role="farmer",
    )
    assert farmer.is_admin is False

    with pytest.raises(AuthorizationError) as exc_farmer:
        require_admin(farmer)
    assert "Administrator privileges required" in str(exc_farmer.value)

    with pytest.raises(AuthorizationError) as exc_none:
        require_admin(None)
    assert "Authentication required" in str(exc_none.value)


def test_regular_farmer_cannot_access_admin_service(db_session: Session, regular_farmer: AuthenticatedFarmer):
    """Verify regular farmers cannot access overview, farmer list, or export methods."""
    with pytest.raises(AuthorizationError):
        AdminService.get_system_overview(db_session, regular_farmer)

    with pytest.raises(AuthorizationError):
        AdminService.list_farmers(db_session, regular_farmer)

    with pytest.raises(AuthorizationError):
        AdminService.export_data(db_session, regular_farmer, "farmers", "csv")

    with pytest.raises(AuthorizationError):
        BackupService.create_backup(regular_farmer)


def test_admin_system_overview_metrics(db_session: Session, admin_user: AuthenticatedFarmer):
    """Verify overview contains required metric keys and non-negative counts."""
    overview = AdminService.get_system_overview(db_session, admin_user)

    assert "total_farmers" in overview
    assert "active_farmers" in overview
    assert "total_crops" in overview
    assert "total_cultivated_acres" in overview
    assert "total_activities" in overview
    assert "total_expenses_count" in overview
    assert "total_harvest_revenue" in overview
    assert "farmer_questions_asked" in overview
    assert "language_distribution" in overview

    assert overview["total_farmers"] >= 0
    assert overview["active_farmers"] <= overview["total_farmers"]
    assert overview["total_cultivated_acres"] >= 0.0


def test_farmer_management_search_and_privacy(db_session: Session, admin_user: AuthenticatedFarmer):
    """Verify farmer list filters correctly and never exposes passwords or secrets."""
    farmers, count = AdminService.list_farmers(db_session, admin_user, limit=50)

    assert count >= 0
    assert len(farmers) == count or len(farmers) <= 50

    for f in farmers:
        # Strict privacy checks:
        assert "password" not in f
        assert "password_hash" not in f
        assert "token" not in f
        assert "secret" not in f

        # Required fields present:
        assert "id" in f
        assert "full_name" in f
        assert "phone" in f
        assert "district" in f
        assert "is_active" in f


def test_farmer_status_toggle(db_session: Session, admin_user: AuthenticatedFarmer, regular_farmer: AuthenticatedFarmer):
    """Verify admin can toggle a farmer's active status with audit logging."""
    target_id = regular_farmer.id

    # Toggle to False
    updated = AdminService.toggle_farmer_status(db_session, admin_user, target_id, False)
    assert updated.is_active is False

    # Check audit log
    log = (
        db_session.query(AdminAuditLog)
        .filter(AdminAuditLog.action == "TOGGLE_STATUS", AdminAuditLog.resource_id == target_id)
        .order_by(AdminAuditLog.created_at.desc())
        .first()
    )
    assert log is not None
    assert log.admin_name == admin_user.full_name

    # Toggle back to True
    updated_back = AdminService.toggle_farmer_status(db_session, admin_user, target_id, True)
    assert updated_back.is_active is True


def test_crop_and_financial_analytics(db_session: Session, admin_user: AuthenticatedFarmer):
    """Verify crop and financial analytics methods aggregate without error."""
    crop_an = AdminService.get_crop_analytics(db_session, admin_user)
    assert "popular_crops" in crop_an
    assert "growth_stages" in crop_an
    assert "status_distribution" in crop_an

    fin_an = AdminService.get_financial_analytics(db_session, admin_user)
    assert "categories" in fin_an
    assert "revenue_by_crop" in fin_an
    assert "total_expense" in fin_an
    assert "total_revenue" in fin_an


def test_ai_usage_analytics_privacy(db_session: Session, admin_user: AuthenticatedFarmer):
    """Verify AI usage analytics returns aggregate trends without exposing private messages."""
    ai_an = AdminService.get_ai_usage_analytics(db_session, admin_user)
    assert "total_conversations" in ai_an
    assert "total_questions" in ai_an
    assert "language_distribution" in ai_an
    assert "popular_topics" in ai_an

    # Verify topics structure
    for t in ai_an["popular_topics"]:
        assert "topic" in t
        assert "count" in t


def test_data_exports_all_formats_and_sanitization(db_session: Session, admin_user: AuthenticatedFarmer):
    """Verify CSV, XLSX, and JSON exports are generated properly and strip all credentials."""
    for mod in ["farmers", "crops", "expenses", "harvest", "activities"]:
        # 1. CSV Export
        csv_bytes, csv_filename, csv_mime = AdminService.export_data(db_session, admin_user, mod, "csv")
        assert csv_filename.endswith(".csv")
        assert csv_mime == "text/csv"
        assert len(csv_bytes) > 0
        csv_text = csv_bytes.decode("utf-8-sig")
        assert "password_hash" not in csv_text
        assert "secret_key" not in csv_text

        # 2. Excel (XLSX) Export
        xlsx_bytes, xlsx_filename, xlsx_mime = AdminService.export_data(db_session, admin_user, mod, "xlsx")
        assert xlsx_filename.endswith(".xlsx")
        assert "openxmlformats" in xlsx_mime
        assert len(xlsx_bytes) > 0
        # Verify valid Excel by reading back with pandas
        df_read = pd.read_excel(io.BytesIO(xlsx_bytes))
        assert "password_hash" not in df_read.columns

        # 3. JSON Export
        json_bytes, json_filename, json_mime = AdminService.export_data(db_session, admin_user, mod, "json")
        assert json_filename.endswith(".json")
        assert json_mime == "application/json"
        parsed = json.loads(json_bytes.decode("utf-8"))
        assert isinstance(parsed, list)
        for item in parsed:
            assert "password_hash" not in item
            assert "token" not in item


def test_backup_and_audit_logging(db_session: Session, admin_user: AuthenticatedFarmer):
    """Verify database backup creation, listing, and audit trail recording."""
    dest_path, filename, size_bytes = BackupService.create_backup(admin_user, db=db_session)
    assert dest_path.exists()
    assert size_bytes > 0
    assert filename.startswith("agrisaathi_backup_")

    backups = BackupService.list_backups(admin_user)
    assert len(backups) >= 1
    found = any(b["filename"] == filename for b in backups)
    assert found is True

    # Verify audit log
    logs = AdminService.get_audit_logs(db_session, admin_user, limit=20, action_filter="BACKUP_DB")
    assert len(logs) >= 1
    assert logs[0]["action"] == "BACKUP_DB"
    assert logs[0]["resource_type"] == "backup"
