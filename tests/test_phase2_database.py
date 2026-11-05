"""Tests for Phase 2 Production Database Readiness:
- PostgreSQL URL normalization (postgres:// -> postgresql+psycopg://)
- Connection pooling and pool_pre_ping configuration
- SQLite to PostgreSQL / secondary database migration tool
- Alembic migration graph consistency
"""

from core.database import normalize_db_url, create_engine
from scripts.migrate_sqlite_to_postgres import run_migration, MIGRATION_TABLE_ORDER
from alembic.config import Config
from alembic.script import ScriptDirectory


def test_normalize_db_url():
    """Verify DATABASE_URL normalization for Postgres and Supabase / Neon URLs."""
    # Supabase / Heroku legacy postgres:// scheme
    legacy_url = "postgres://postgres:password123@db.supabase.co:5432/postgres"
    norm = normalize_db_url(legacy_url)
    assert norm.startswith("postgresql")
    assert "postgres://" not in norm

    # Standard postgresql:// scheme
    standard_url = "postgresql://user:secret@localhost:5432/agrisaathi"
    norm_standard = normalize_db_url(standard_url)
    assert norm_standard.startswith("postgresql")

    # SQLite URLs left unchanged
    sqlite_url = "sqlite:///data/agrisaathi.db"
    assert normalize_db_url(sqlite_url) == sqlite_url


def test_engine_pooling_configuration(monkeypatch):
    """Verify PostgreSQL connections configure connection pooling and pre_ping."""
    # Test SQLite engine configuration
    sqlite_eng = create_engine("sqlite:///:memory:", pool_pre_ping=True)
    assert sqlite_eng.pool is not None

    # Verify parameters expected for Postgres engine
    pg_url = "postgresql+psycopg://test:test@localhost:5432/testdb"
    # Create engine without connecting (engine creation is lazy)
    pg_eng = create_engine(
        pg_url,
        pool_size=10,
        max_overflow=20,
        pool_recycle=300,
        pool_pre_ping=True,
    )
    assert pg_eng.pool.size() == 10
    assert pg_eng.pool._max_overflow == 20
    assert pg_eng.pool._recycle == 300


def test_migration_script_dry_run(tmp_path):
    """Verify SQLite to PostgreSQL migration script runs dry-run mode and inspects all tables."""
    # Create a dummy source SQLite database with tables
    source_db = tmp_path / "source.db"
    src_url = f"sqlite:///{source_db.as_posix()}"

    from core.database import Base
    import models  # noqa: F401
    engine_src = create_engine(src_url)
    Base.metadata.create_all(bind=engine_src)

    report = run_migration(
        sqlite_url=src_url,
        postgres_url="postgresql://user:pass@localhost:5432/agrisaathi_test",
        dry_run=True,
    )

    assert report["status"] == "success"
    assert report["dry_run"] is True
    # Verify core tables are covered in migration order
    for t in ["users", "crops", "farm_activities", "expenses", "conversations"]:
        assert t in report["tables"]
        assert report["tables"][t]["status"] == "READY"


def test_migration_table_topological_ordering():
    """Verify migration table order satisfies foreign key dependencies."""
    assert MIGRATION_TABLE_ORDER[0] == "users"  # Users must be migrated first
    assert MIGRATION_TABLE_ORDER.index("users") < MIGRATION_TABLE_ORDER.index("crops")
    assert MIGRATION_TABLE_ORDER.index("users") < MIGRATION_TABLE_ORDER.index("farm_activities")
    assert MIGRATION_TABLE_ORDER.index("users") < MIGRATION_TABLE_ORDER.index("expenses")
    assert MIGRATION_TABLE_ORDER.index("conversations") < MIGRATION_TABLE_ORDER.index("messages")


def test_alembic_migration_chain_unbroken():
    """Verify Alembic migration revision graph is valid with a single distinct head."""
    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)
    heads = script.get_heads()
    assert len(heads) == 1, f"Expected exactly 1 migration head, got: {heads}"
    assert heads[0] == "2026_10_31_user_security"
