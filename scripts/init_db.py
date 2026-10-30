"""Database initialization script for AgriSaathi AI."""

import sys
from pathlib import Path
from sqlalchemy import inspect

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import init_db, engine, get_db
from utils.logging_config import logger


def main():
    logger.info("Initializing AgriSaathi AI SQLite database tables...")
    init_db()

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Database tables successfully initialized: {tables}")
    print(f"Database tables initialized successfully ({len(tables)} tables): {', '.join(tables)}")

    if "users" in tables:
        print("✓ Critical table 'users' verified present.")
    else:
        print("✗ ERROR: 'users' table missing!")
        sys.exit(1)

    # Seed baseline knowledge if empty
    try:
        from models.knowledge import CropKnowledge
        from scripts.seed_knowledge import seed_database
        with get_db() as db:
            if db.query(CropKnowledge).count() == 0:
                print("Seeding initial crop knowledge...")
                seed_database()
                print("Crop knowledge seeded.")
    except Exception as e:
        logger.warning(f"Knowledge seed in init_db skipped: {e}")


if __name__ == "__main__":
    main()
