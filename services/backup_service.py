"""Database Backup and Restore Service for AgriSaathi AI.

Provides atomic SQLite snapshots, integrity validation, pre-restore safety backups,
and audit trail logging. Restricted to verified platform administrators.
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from datetime import datetime, date
import sqlite3
import shutil
import json
import uuid
from sqlalchemy import MetaData, select
from sqlalchemy.orm import Session

from config import settings, BASE_DIR
from core.auth import AuthenticatedFarmer, require_admin
from core.database import get_db, engine
from services.admin_service import AdminService
from utils.logging_config import logger

BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

BACKUP_TABLE_ORDER: List[str] = [
    "users",
    "crops",
    "farm_activities",
    "expenses",
    "harvest_records",
    "conversations",
    "messages",
    "health_observations",
    "crop_knowledge",
    "knowledge_documents",
    "mandi_price_history",
    "mandi_price_cache",
    "admin_audit_logs",
]


class BackupService:
    """Manages secure database backups, verification, and restoration across SQLite & PostgreSQL."""

    @classmethod
    def get_sqlite_db_path(cls) -> Path:
        """Resolve current active SQLite database path."""
        db_url = settings.DATABASE_URL
        if not db_url.startswith("sqlite"):
            raise ValueError("Direct file backup is only applicable for SQLite. For PostgreSQL, use portable JSON snapshot or pg_dump.")

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
        """Create a database backup: atomic SQLite snapshot if SQLite, or portable JSON snapshot if PostgreSQL."""
        require_admin(admin)
        if settings.DATABASE_URL.startswith("sqlite"):
            return cls.create_sqlite_backup(admin, backup_dir=backup_dir, db=db)
        return cls.create_portable_snapshot(admin, backup_dir=backup_dir, db=db)

    @classmethod
    def create_sqlite_backup(
        cls,
        admin: AuthenticatedFarmer,
        backup_dir: Optional[Path] = None,
        db: Optional[Session] = None,
        src_db_path: Optional[Path] = None,
    ) -> Tuple[Path, str, int]:
        """Create an atomic SQLite database backup using the online backup API.

        Validates database integrity and logs the event to the Admin Audit Log.
        """
        require_admin(admin)
        src_path = src_db_path or cls.get_sqlite_db_path()
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
            "format": "sqlite3",
            "path": str(dest_path),
        }
        cls._log_backup_action(admin, backup_filename, log_details, db=db)
        return dest_path, backup_filename, file_size

    @classmethod
    def create_portable_snapshot(
        cls,
        admin: AuthenticatedFarmer,
        backup_dir: Optional[Path] = None,
        db: Optional[Session] = None,
    ) -> Tuple[Path, str, int]:
        """Export all tables into an atomic, portable JSON snapshot."""
        require_admin(admin)
        target_dir = backup_dir or BACKUP_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        engine_prefix = "pg" if not settings.DATABASE_URL.startswith("sqlite") else "sqlite"
        backup_filename = f"agrisaathi_backup_{engine_prefix}_{timestamp_str}.json"
        dest_path = target_dir / backup_filename

        metadata = MetaData()
        metadata.reflect(bind=engine)

        snapshot_data: Dict[str, Any] = {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "timestamp": datetime.now().isoformat(),
            "engine": engine.dialect.name,
            "tables": {},
            "record_counts": {},
        }

        with engine.connect() as conn:
            for tbl_name in BACKUP_TABLE_ORDER:
                if tbl_name not in metadata.tables:
                    continue
                tbl = metadata.tables[tbl_name]
                rows = conn.execute(select(tbl)).fetchall()
                cols = [c.name for c in tbl.columns]
                serialized_rows = []
                for r in rows:
                    row_dict = dict(zip(cols, r))
                    for k, v in row_dict.items():
                        if isinstance(v, (datetime, date)):
                            row_dict[k] = v.isoformat()
                        elif isinstance(v, uuid.UUID):
                            row_dict[k] = str(v)
                    serialized_rows.append(row_dict)
                snapshot_data["tables"][tbl_name] = serialized_rows
                snapshot_data["record_counts"][tbl_name] = len(serialized_rows)

        # Write to JSON file
        json_content = json.dumps(snapshot_data, indent=2, ensure_ascii=False)
        dest_path.write_text(json_content, encoding="utf-8")
        file_size = dest_path.stat().st_size

        log_details = {
            "backup_filename": backup_filename,
            "file_size_bytes": file_size,
            "format": "portable_json",
            "record_counts": snapshot_data["record_counts"],
            "path": str(dest_path),
        }
        cls._log_backup_action(admin, backup_filename, log_details, db=db)
        return dest_path, backup_filename, file_size

    @classmethod
    def _log_backup_action(
        cls,
        admin: AuthenticatedFarmer,
        filename: str,
        details: dict,
        db: Optional[Session] = None,
    ) -> None:
        """Internal helper to log backup creation."""
        if db is not None:
            AdminService.log_action(
                db=db,
                admin=admin,
                action="BACKUP_DB",
                resource_type="backup",
                resource_id=filename,
                details=details,
            )
        else:
            with get_db() as db_session:
                AdminService.log_action(
                    db=db_session,
                    admin=admin,
                    action="BACKUP_DB",
                    resource_type="backup",
                    resource_id=filename,
                    details=details,
                )

    @classmethod
    def list_backups(
        cls,
        admin: AuthenticatedFarmer,
        backup_dir: Optional[Path] = None,
    ) -> List[Dict[str, Any]]:
        """List all available database backup files (SQLite .db and Portable JSON)."""
        require_admin(admin)
        target_dir = backup_dir or BACKUP_DIR
        if not target_dir.exists():
            return []

        backups = []
        for f in target_dir.glob("agrisaathi_backup_*.*"):
            if f.suffix not in (".db", ".json"):
                continue
            try:
                stat = f.stat()
                backups.append({
                    "filename": f.name,
                    "format": "SQLite (.db)" if f.suffix == ".db" else "Portable JSON (.json)",
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
        """Safely restore database from uploaded backup file (SQLite .db or Portable JSON).

        Creates an automatic pre-restore safety snapshot before replacing or updating active records.
        """
        require_admin(admin)
        if not backup_bytes or len(backup_bytes) < 50:
            raise ValueError("Uploaded backup file is empty or invalid.")

        # Determine backup format
        is_sqlite_file = backup_bytes.startswith(b"SQLite format 3")
        is_json_file = False
        try:
            if not is_sqlite_file:
                first_chars = backup_bytes[:20].decode("utf-8", errors="ignore").strip()
                if first_chars.startswith("{"):
                    is_json_file = True
        except Exception:
            pass

        if not is_sqlite_file and not is_json_file:
            raise ValueError("Unsupported backup format. File must be a SQLite .db file or a portable .json backup snapshot.")

        # Create automatic safety backup before restoring
        safety_path = None
        try:
            safety_res = cls.create_backup(admin)
            safety_path = str(safety_res[0])
        except Exception as e:
            logger.warning(f"Could not create automatic pre-restore safety snapshot: {e}")

        if is_sqlite_file:
            if not settings.DATABASE_URL.startswith("sqlite"):
                raise ValueError("Direct SQLite file restoration cannot be applied to an active PostgreSQL database. Use a Portable JSON backup snapshot or the migration tool.")
            return cls._restore_sqlite_file(admin, backup_bytes, safety_path)
        else:
            return cls._restore_json_snapshot(admin, backup_bytes, safety_path)

    @classmethod
    def _restore_sqlite_file(
        cls,
        admin: AuthenticatedFarmer,
        backup_bytes: bytes,
        safety_snapshot_path: Optional[str],
    ) -> Dict[str, Any]:
        """Restore active SQLite database file."""
        active_path = cls.get_sqlite_db_path()
        temp_verify_path = BACKUP_DIR / f"temp_verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            with open(temp_verify_path, "wb") as f:
                f.write(backup_bytes)

            conn = sqlite3.connect(str(temp_verify_path))
            try:
                cur = conn.cursor()
                cur.execute("PRAGMA integrity_check")
                res = cur.fetchone()
                if not res or res[0] != "ok":
                    raise ValueError(f"Uploaded database backup corrupted or invalid: {res}")
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cur.fetchall()]
                if "users" not in tables:
                    raise ValueError("Uploaded database does not contain AgriSaathi 'users' table.")
            finally:
                conn.close()

            shutil.copy2(temp_verify_path, active_path)
            logger.info(f"Database successfully restored from SQLite backup to {active_path}")

            with get_db() as db:
                AdminService.log_action(
                    db=db,
                    admin=admin,
                    action="RESTORE_DB",
                    resource_type="backup",
                    details={
                        "restored_size_bytes": len(backup_bytes),
                        "format": "sqlite3",
                        "safety_snapshot": safety_snapshot_path,
                    },
                )

            return {
                "status": "success",
                "message": "SQLite database successfully restored and verified.",
                "restored_size_bytes": len(backup_bytes),
                "safety_snapshot": safety_snapshot_path,
            }
        finally:
            temp_verify_path.unlink(missing_ok=True)

    @classmethod
    def _restore_json_snapshot(
        cls,
        admin: AuthenticatedFarmer,
        backup_bytes: bytes,
        safety_snapshot_path: Optional[str],
    ) -> Dict[str, Any]:
        """Restore records topologically from portable JSON snapshot into active database."""
        snapshot = json.loads(backup_bytes.decode("utf-8"))
        tables_data = snapshot.get("tables", {})
        if "users" not in tables_data:
            raise ValueError("Uploaded JSON backup snapshot is missing the 'users' table.")

        metadata = MetaData()
        metadata.reflect(bind=engine)

        restored_records_count = 0
        with get_db() as db:
            for tbl_name in BACKUP_TABLE_ORDER:
                if tbl_name not in tables_data or tbl_name not in metadata.tables:
                    continue

                tbl = metadata.tables[tbl_name]
                rows = tables_data[tbl_name]
                if not rows:
                    continue

                pk_col = tbl.primary_key.columns.keys()[0] if tbl.primary_key.columns else None
                existing_pks = set()
                if pk_col and pk_col in tbl.c:
                    existing_pks = {
                        r[0] for r in db.execute(select(tbl.c[pk_col])).fetchall()
                    }

                # Filter out rows already existing to ensure idempotency
                rows_to_insert = [r for r in rows if pk_col is None or r.get(pk_col) not in existing_pks]

                # Convert date/datetime strings back to python date/datetime
                for r in rows_to_insert:
                    for col in tbl.columns:
                        col_type = col.type
                        val = r.get(col.name)
                        if val is not None and isinstance(val, str):
                            if "DateTime" in str(col_type) or "TIMESTAMP" in str(col_type):
                                try:
                                    r[col.name] = datetime.fromisoformat(val)
                                except Exception:
                                    pass
                            elif "Date" in str(col_type):
                                try:
                                    r[col.name] = date.fromisoformat(val)
                                except Exception:
                                    pass
                        if hasattr(col_type, "python_type") and col_type.python_type is bool:
                            if val is not None:
                                r[col.name] = bool(val)

                if rows_to_insert:
                    db.execute(tbl.insert(), rows_to_insert)
                    restored_records_count += len(rows_to_insert)

            db.commit()

        with get_db() as db:
            AdminService.log_action(
                db=db,
                admin=admin,
                action="RESTORE_DB",
                resource_type="backup",
                details={
                    "restored_records_count": restored_records_count,
                    "format": "portable_json",
                    "safety_snapshot": safety_snapshot_path,
                },
            )

        return {
            "status": "success",
            "message": f"Successfully restored {restored_records_count} records from portable JSON snapshot.",
            "restored_size_bytes": len(backup_bytes),
            "safety_snapshot": safety_snapshot_path,
        }

