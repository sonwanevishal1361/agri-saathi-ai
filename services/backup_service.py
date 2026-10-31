"""Database Backup and Restore Service for AgriSaathi AI.

Provides atomic SQLite snapshots, integrity validation, pre-restore safety backups,
and audit trail logging. Restricted to verified platform administrators.
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from datetime import datetime
import sqlite3
import shutil
from sqlalchemy.orm import Session

from config import settings, BASE_DIR
from core.auth import AuthenticatedFarmer, require_admin
from core.database import get_db
from services.admin_service import AdminService
from utils.logging_config import logger

BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


class BackupService:
    """Manages secure database backups, verification, and restoration."""

    @classmethod
    def get_sqlite_db_path(cls) -> Path:
        """Resolve current active SQLite database path."""
        db_url = settings.DATABASE_URL
        if not db_url.startswith("sqlite"):
            raise ValueError("Direct file backup is only applicable for SQLite. For PostgreSQL, use pg_dump.")

        raw_path = db_url.replace("sqlite:///", "", 1)
        if raw_path.startswith("/") and len(raw_path) > 2 and raw_path[2] == ":":
            raw_path = raw_path[1:]
        p = Path(raw_path)
        if not p.is_absolute():
            p = BASE_DIR / p
        return p

    @classmethod
    def create_backup(
        cls,
        admin: AuthenticatedFarmer,
        backup_dir: Optional[Path] = None,
        db: Optional[Session] = None,
    ) -> Tuple[Path, str, int]:
        """Create an atomic SQLite database backup using the online backup API.

        Validates database integrity and logs the event to the Admin Audit Log.
        """
        require_admin(admin)
        src_path = cls.get_sqlite_db_path()
        if not src_path.exists():
            raise FileNotFoundError(f"Active database file not found at: {src_path}")

        target_dir = backup_dir or BACKUP_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"agrisaathi_backup_{timestamp_str}.db"
        dest_path = target_dir / backup_filename

        logger.info(f"Initiating online database backup from {src_path} to {dest_path}...")

        # Use SQLite Online Backup API for atomic, lock-free snapshot
        src_conn = sqlite3.connect(str(src_path))
        dest_conn = sqlite3.connect(str(dest_path))
        try:
            with dest_conn:
                src_conn.backup(dest_conn, pages=100)
        finally:
            dest_conn.close()
            src_conn.close()

        # Verify integrity of newly created backup
        verify_conn = sqlite3.connect(str(dest_path))
        try:
            cur = verify_conn.cursor()
            cur.execute("PRAGMA integrity_check")
            integrity_result = cur.fetchone()
            if not integrity_result or integrity_result[0] != "ok":
                dest_path.unlink(missing_ok=True)
                raise RuntimeError(f"Backup failed integrity check: {integrity_result}")
        finally:
            verify_conn.close()

        file_size = dest_path.stat().st_size
        logger.info(f"Database backup created successfully: {dest_path} ({file_size} bytes)")

        # Log audit trail
        log_details = {
            "backup_filename": backup_filename,
            "file_size_bytes": file_size,
            "path": str(dest_path),
        }
        if db is not None:
            AdminService.log_action(
                db=db,
                admin=admin,
                action="BACKUP_DB",
                resource_type="backup",
                resource_id=backup_filename,
                details=log_details,
            )
        else:
            with get_db() as db_session:
                AdminService.log_action(
                    db=db_session,
                    admin=admin,
                    action="BACKUP_DB",
                    resource_type="backup",
                    resource_id=backup_filename,
                    details=log_details,
                )

        return dest_path, backup_filename, file_size

    @classmethod
    def list_backups(cls, admin: AuthenticatedFarmer) -> List[Dict[str, Any]]:
        """List all available database backup files with size and creation dates."""
        require_admin(admin)
        target_dir = BACKUP_DIR
        if not target_dir.exists():
            return []

        backups = []
        for f in target_dir.glob("agrisaathi_backup_*.db"):
            try:
                stat = f.stat()
                backups.append({
                    "filename": f.name,
                    "path": str(f),
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })
            except Exception as e:
                logger.warning(f"Error reading backup file {f}: {e}")

        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups

    @classmethod
    def restore_backup(
        cls,
        admin: AuthenticatedFarmer,
        backup_bytes: bytes,
    ) -> Dict[str, Any]:
        """Safely restore database from uploaded backup file.

        Creates an automatic pre-restore safety snapshot before replacing active database.
        """
        require_admin(admin)
        if not backup_bytes or len(backup_bytes) < 100:
            raise ValueError("Uploaded backup file is empty or invalid.")

        active_path = cls.get_sqlite_db_path()

        # Step 1: Write uploaded bytes to temporary validation file
        temp_verify_path = BACKUP_DIR / f"temp_verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            with open(temp_verify_path, "wb") as f:
                f.write(backup_bytes)

            # Step 2: Test integrity check on uploaded backup
            conn = sqlite3.connect(str(temp_verify_path))
            try:
                cur = conn.cursor()
                cur.execute("PRAGMA integrity_check")
                res = cur.fetchone()
                if not res or res[0] != "ok":
                    raise ValueError(f"Uploaded database backup corrupted or invalid: {res}")

                # Verify critical tables exist in the uploaded backup
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cur.fetchall()]
                if "users" not in tables:
                    raise ValueError("Uploaded database does not contain AgriSaathi 'users' table.")
            finally:
                conn.close()

            # Step 3: Create automatic pre-restore safety snapshot of the active database
            safety_snapshot_path = None
            if active_path.exists():
                safety_snapshot_name = f"agrisaathi_pre_restore_safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                safety_snapshot_path = BACKUP_DIR / safety_snapshot_name
                shutil.copy2(active_path, safety_snapshot_path)
                logger.info(f"Pre-restore safety snapshot created at {safety_snapshot_path}")

            # Step 4: Overwrite active database file
            shutil.copy2(temp_verify_path, active_path)
            logger.info(f"Database successfully restored from uploaded backup to {active_path}")

            # Step 5: Log audit trail
            with get_db() as db:
                AdminService.log_action(
                    db=db,
                    admin=admin,
                    action="RESTORE_DB",
                    resource_type="backup",
                    details={
                        "restored_size_bytes": len(backup_bytes),
                        "safety_snapshot": str(safety_snapshot_path) if safety_snapshot_path else None,
                    },
                )

            return {
                "status": "success",
                "message": "Database successfully restored and verified.",
                "restored_size_bytes": len(backup_bytes),
                "safety_snapshot": str(safety_snapshot_path) if safety_snapshot_path else None,
            }

        finally:
            temp_verify_path.unlink(missing_ok=True)
