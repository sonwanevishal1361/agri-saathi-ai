"""Database configuration and session management using SQLAlchemy 2.x."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from config import settings, BASE_DIR
from utils.logging_config import logger


def mask_database_url(url: Optional[str]) -> str:
    """Mask credentials in database URL to prevent sensitive password exposure in logs."""
    if not url:
        return ""
    raw = str(url).strip()
    if "@" in raw and "://" in raw:
        try:
            scheme_creds, host_part = raw.split("@", 1)
            scheme, creds = scheme_creds.split("://", 1)
            if ":" in creds:
                user = creds.split(":", 1)[0]
                return f"{scheme}://{user}:***@{host_part}"
            return f"{scheme}://***@{host_part}"
        except Exception:
            return raw.split("@")[-1]
    return raw


def normalize_database_url(url: Optional[str] = None) -> str:
    """Normalize database URL for SQLAlchemy 2.x and driver compatibility.

    - Converts 'postgres://' -> 'postgresql+psycopg://'
    - Converts 'postgresql://' -> 'postgresql+psycopg://'
    - Converts 'postgresql+psycopg2://' -> 'postgresql+psycopg://'
    - Enforces 'sslmode=require' for Neon and Supabase serverless hosts if omitted
    - Resolves relative SQLite paths to absolute paths
    """
    raw = (url or settings.DATABASE_URL or "").strip()
    if not raw:
        raw = f"sqlite:///{(BASE_DIR / 'data' / 'agrisaathi.db').as_posix()}"

    # Handle SQLite - preserve as-is
    if raw.startswith("sqlite"):
        return raw

    # Convert Postgres dialect prefixes to psycopg 3 driver
    if raw.startswith("postgres://"):
        raw = "postgresql+psycopg://" + raw[len("postgres://"):]
    elif raw.startswith("postgresql+psycopg2://"):
        raw = "postgresql+psycopg://" + raw[len("postgresql+psycopg2://"):]
    elif raw.startswith("postgresql://"):
        raw = "postgresql+psycopg://" + raw[len("postgresql://"):]

    # Enforce sslmode=require for serverless cloud providers (Neon, Supabase)
    lower = raw.lower()
    if any(h in lower for h in ("neon.tech", "supabase.co", "supabase.com", "pooler.supabase")):
        if "sslmode=" not in lower:
            sep = "&" if "?" in raw else "?"
            raw = f"{raw}{sep}sslmode=require"

    return raw


# Backward-compatibility alias
normalize_db_url = normalize_database_url


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
            logger.warning(f"Could not verify database directory for {mask_database_url(target_url)}: {e}")


def _get_active_language() -> str:
    """Safely get current language for localized error presentation."""
    try:
        import streamlit as st
        if hasattr(st, "session_state") and "language" in st.session_state:
            return st.session_state.language
    except Exception:
        pass
    return getattr(settings, "DEFAULT_LANGUAGE", "en")


def display_db_error(exc: Exception, masked_url: str = "") -> None:
    """Display user-friendly localized error in Streamlit without exposing raw traceback or credentials."""
    from utils.language import t
    lang = _get_active_language()
    clean_err = mask_database_url(str(exc).splitlines()[0] if str(exc) else type(exc).__name__)
    target_masked = masked_url or mask_database_url(normalized_url)

    # Log clean error without raw traceback or plain passwords
    logger.error(f"Database connection error ({type(exc).__name__}) on {target_masked}: {clean_err}")

    try:
        import streamlit as st
        is_missing_driver = (
            isinstance(exc, (ImportError, ModuleNotFoundError))
            or "psycopg" in str(exc).lower()
            or "no module named" in str(exc).lower()
        )
        title = t("db_connection_error_title", lang)
        if is_missing_driver:
            desc = t("db_driver_error_desc", lang)
            hint = "Streamlit Cloud: App Settings → Advanced Settings → Python version: 3.12, and ensure `psycopg[binary]>=3.2.10` in requirements.txt."
        else:
            desc = t("db_connection_error_desc", lang)
            hint = f"Verify `DATABASE_URL` in Streamlit Cloud Secrets ({target_masked}) and ensure your cloud database server is running."

        st.error(f"### ⚠️ {title}\n\n{desc}\n\n**Action Required:** {hint}\n\n*Diagnostics:* `{type(exc).__name__}: {clean_err}`")
    except Exception:
        pass


# Ensure directory exists before creating engine
ensure_db_dir_exists()

# Create SQLAlchemy engine with connection pooling and driver compatibility
normalized_url = normalize_database_url(settings.DATABASE_URL)
is_sqlite = normalized_url.startswith("sqlite")

engine_kwargs: dict = {
    "pool_pre_ping": True,
}

if is_sqlite:
    # SQLite requires check_same_thread: False for Streamlit concurrency
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production PostgreSQL connection pooling (Neon / Supabase / AWS RDS / Cloud SQL)
    # Small pool size suitable for serverless / containerized deployment
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_recycle"] = 300  # Recycle after 5 mins to handle serverless idle timeouts
    engine_kwargs["pool_timeout"] = 30   # Wait up to 30s for pool checkout during wake-ups
    engine_kwargs["connect_args"] = {
        "connect_timeout": 15,           # Prevent hanging on initial socket connection
    }

_engine_init_error: Optional[Exception] = None
engine: Optional[Engine] = None

try:
    engine = create_engine(
        normalized_url,
        **engine_kwargs,
    )
except Exception as _e:
    _engine_init_error = _e
    logger.error(f"Failed to create database engine for {mask_database_url(normalized_url)}: {_e}")


# Enforce foreign key constraints on SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if normalized_url.startswith("sqlite"):
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

    if target_engine is None:
        if _engine_init_error:
            display_db_error(_engine_init_error)
            raise _engine_init_error
        raise RuntimeError("Database engine is not initialized")

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
        if "must_change_password" not in user_cols:
            with target_engine.begin() as conn:
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT FALSE NOT NULL"))
            logger.info("Successfully added 'must_change_password' column to 'users' table.")
        if "failed_login_attempts" not in user_cols:
            with target_engine.begin() as conn:
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0 NOT NULL"))
            logger.info("Successfully added 'failed_login_attempts' column to 'users' table.")
        if "locked_until" not in user_cols:
            with target_engine.begin() as conn:
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE users ADD COLUMN locked_until TIMESTAMP"))
            logger.info("Successfully added 'locked_until' column to 'users' table.")

        # Idempotently heal any NULL or empty roles/active statuses
        with target_engine.begin() as conn:
            from sqlalchemy import text
            conn.execute(text("UPDATE users SET role = 'farmer' WHERE role IS NULL OR role = ''"))
            conn.execute(text("UPDATE users SET is_active = TRUE WHERE is_active IS NULL"))
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
    if _engine_init_error is not None or engine is None:
        display_db_error(_engine_init_error or RuntimeError("Database engine is not initialized"))
        raise _engine_init_error or RuntimeError("Database engine is not initialized")

    if not _db_initialized:
        try:
            init_db()
        except Exception as e:
            display_db_error(e)
            raise

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
    """Drop all tables (strictly restricted to isolated test environments)."""
    target_engine = bind_engine or engine
    if target_engine is None:
        return
    url_str = str(target_engine.url)
    if settings.APP_ENV == "production" or not (url_str.startswith("sqlite") or ":memory:" in url_str):
        raise PermissionError(
            "drop_db is strictly prohibited against production, cloud, or persistent databases."
        )
    global _db_initialized
    import models  # noqa: F401
    Base.metadata.drop_all(bind=target_engine)
    _db_initialized = False


def get_database_info() -> dict:
    """Return diagnostic metadata about the active database engine and persistence layer."""
    if engine is None:
        return {
            "engine": "unknown",
            "dialect": "uninitialized",
            "is_persistent": False,
            "storage_mode": "Uninitialized Engine",
            "sanitized_url": mask_database_url(normalized_url),
            "error": str(_engine_init_error) if _engine_init_error else "Engine not created",
        }

    url_str = str(engine.url)
    is_pg = not url_str.startswith("sqlite")
    sanitized_url = mask_database_url(url_str)

    return {
        "engine": "postgresql" if is_pg else "sqlite",
        "dialect": engine.dialect.name,
        "is_persistent": is_pg,
        "storage_mode": "Durable Cloud PostgreSQL (Permanent Storage)" if is_pg else "Local SQLite (Ephemeral on Cloud)",
        "sanitized_url": sanitized_url,
        "pool_pre_ping": True,
        "pool_recycle_seconds": 300 if is_pg else None,
        "pool_size": 5 if is_pg else None,
        "max_overflow": 10 if is_pg else None,
    }


def bootstrap_database() -> bool:
    """Ensure database schema and baseline records exist before handling any user interaction."""
    global _db_initialized

    if _engine_init_error is not None or engine is None:
        err = _engine_init_error or RuntimeError("Database engine not initialized")
        display_db_error(err)
        if not is_sqlite or settings.APP_ENV == "production":
            logger.error("Production database connection failed. Refusing silent fallback to SQLite.")
            return False

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
        clean_msg = mask_database_url(str(exc).splitlines()[0] if str(exc) else type(exc).__name__)
        logger.error(f"Critical error during database bootstrap: {clean_msg}")
        display_db_error(exc)
        # NEVER silently fall back to SQLite in production!
        if not is_sqlite or settings.APP_ENV == "production":
            logger.error("Production database bootstrap failed. Will NOT fall back to ephemeral SQLite.")
            return False
        # In local development only with SQLite, attempt direct fallback creation
        try:
            import models  # noqa: F401
            if engine is not None:
                Base.metadata.create_all(bind=engine)
                return True
        except Exception:
            pass
        return False
