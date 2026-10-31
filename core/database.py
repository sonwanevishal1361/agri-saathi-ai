"""Database configuration and session management using SQLAlchemy 2.x."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from config import settings, BASE_DIR
from utils.logging_config import logger


def ensure_db_dir_exists(db_url: Optional[str] = None) -> None:
    """Ensure parent directory exists for SQLite database before connecting."""
    target_url = db_url or settings.DATABASE_URL
    if target_url.startswith("sqlite"):
        try:
            raw_path = target_url.replace("sqlite:///", "", 1)
            # Remove leading slash on Windows (e.g. /C:/...)
            if raw_path.startswith("/") and len(raw_path) > 2 and raw_path[2] == ":":
                raw_path = raw_path[1:]
            db_path = Path(raw_path)
            if not db_path.is_absolute():
                db_path = BASE_DIR / db_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not verify database directory for {target_url}: {e}")


# Ensure directory exists before creating engine
ensure_db_dir_exists()

# Create SQLAlchemy engine
# SQLite requires check_same_thread=False for multi-threaded access (like Streamlit)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


# Enforce foreign key constraints on SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()

_db_initialized = False


def init_db(bind_engine=None) -> None:
    """Create all tables defined on Base idempotently and verify presence."""
    global _db_initialized
    target_engine = bind_engine or engine

    ensure_db_dir_exists(str(target_engine.url))

    # Import all models to ensure they register on Base metadata
    import models  # noqa: F401

    logger.info("Initializing AgriSaathi database schema via Base.metadata.create_all...")
    Base.metadata.create_all(bind=target_engine)

    # Verify critical tables exist
    inspector = inspect(target_engine)
    existing_tables = inspector.get_table_names()
    logger.info(f"Database schema verified. Active tables ({len(existing_tables)}): {existing_tables}")

    if "users" not in existing_tables:
        logger.error("CRITICAL: 'users' table missing after Base.metadata.create_all!")
        raise RuntimeError("Database initialization failed: 'users' table was not created.")

    # Idempotently migrate schema if role column is missing from users table
    try:
        user_cols = [c["name"] for c in inspector.get_columns("users")]
        if "role" not in user_cols:
            logger.info("Migrating schema: adding 'role' column to 'users' table...")
            with target_engine.begin() as conn:
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'farmer' NOT NULL"))
                conn.execute(text("UPDATE users SET role = 'farmer' WHERE role IS NULL OR role = ''"))
            logger.info("Successfully added 'role' column to 'users' table.")
    except Exception as col_exc:
        logger.warning(f"Note during column migration on users: {col_exc}")

    # Idempotently migrate schema if cost column is missing from farm_activities table
    try:
        if "farm_activities" in existing_tables:
            act_cols = [c["name"] for c in inspector.get_columns("farm_activities")]
            if "cost" not in act_cols:
                logger.info("Migrating schema: adding 'cost' column to 'farm_activities' table...")
                with target_engine.begin() as conn:
                    from sqlalchemy import text
                    conn.execute(text("ALTER TABLE farm_activities ADD COLUMN cost FLOAT DEFAULT 0.0"))
                    conn.execute(text("UPDATE farm_activities SET cost = 0.0 WHERE cost IS NULL"))
                logger.info("Successfully added 'cost' column to 'farm_activities' table.")
    except Exception as act_exc:
        logger.warning(f"Note during column migration on farm_activities: {act_exc}")

    _db_initialized = True


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session scope with automatic schema check."""
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
        except Exception as e:
            logger.warning(f"Error during init_db in get_db: {e}")
            _db_initialized = True

    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def drop_db(bind_engine=None) -> None:
    """Drop all tables (used for testing)."""
    global _db_initialized
    target_engine = bind_engine or engine
    import models  # noqa: F401
    Base.metadata.drop_all(bind=target_engine)
    _db_initialized = False


def bootstrap_database() -> bool:
    """Ensure database schema and baseline records exist before handling any user interaction."""
    try:
        logger.info("Bootstrapping AgriSaathi database schema...")
        init_db()

        # Seed crop knowledge library if empty on first deployment
        try:
            from models.knowledge import CropKnowledge
            from scripts.seed_knowledge import seed_database
            with get_db() as db:
                if db.query(CropKnowledge).count() == 0:
                    logger.info("First run detected: seeding initial crop knowledge library...")
                    seed_database()
                    logger.info("Initial crop knowledge library seeded successfully.")
        except Exception as seed_exc:
            logger.warning(f"Initial knowledge seeding skipped/failed: {seed_exc}")

        # Seed default admin user if missing
        try:
            from services.user_service import UserService
            with get_db() as db:
                UserService.seed_admin_if_missing(db)
        except Exception as admin_exc:
            logger.warning(f"Admin seeding check skipped: {admin_exc}")

        return True
    except Exception as exc:
        logger.critical(f"Critical error during database bootstrap: {exc}", exc_info=True)
        # Attempt direct fallback creation
        import models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        return True
