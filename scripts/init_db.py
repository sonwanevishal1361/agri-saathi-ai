"""Database initialization script for AgriSaathi AI."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import init_db
from utils.logging_config import logger


def main():
    logger.info("Initializing AgriSaathi AI SQLite database tables...")
    init_db()
    logger.info("Database tables successfully initialized.")
    print("Database tables initialized successfully.")


if __name__ == "__main__":
    main()

