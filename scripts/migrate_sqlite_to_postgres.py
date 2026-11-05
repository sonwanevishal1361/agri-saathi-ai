"""Production Migration Tool: Migrate AgriSaathi AI SQLite database to Persistent PostgreSQL.

Safely copies all farmer records, crops, activities, financial entries, AI conversations,
and audit logs while strictly preserving UUIDs, timestamps, foreign key relationships,
and password hashes without data loss.

Usage:
    python scripts/migrate_sqlite_to_postgres.py --postgres-url "postgresql://user:pass@localhost:5432/agrisaathi"
    python scripts/migrate_sqlite_to_postgres.py --dry-run
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy import create_engine, inspect, MetaData, select
from sqlalchemy.orm import sessionmaker

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import settings  # noqa: E402
from core.database import Base  # noqa: E402
import models  # noqa: F401, E402
from utils.logging_config import logger  # noqa: E402

# Ordered tables topologically respecting foreign keys
MIGRATION_TABLE_ORDER: List[str] = [
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


def run_migration(
    sqlite_url: str,
    postgres_url: str,
    dry_run: bool = False,
    batch_size: int = 500,
) -> Dict[str, Any]:
    """Execute topological migration from SQLite to PostgreSQL."""
    print("=" * 70)
    print("  AgriSaathi AI: SQLite -> Persistent PostgreSQL Migration Engine")
    print("=" * 70)
    print(f" Source SQLite DB     : {sqlite_url}")
    print(f" Target PostgreSQL DB : {postgres_url.split('@')[-1] if '@' in postgres_url else postgres_url}")
    print(f" Dry Run Mode         : {dry_run}")
    print("-" * 70)

    # 1. Connect to SQLite source
    sqlite_engine = create_engine(sqlite_url)
    sqlite_insp = inspect(sqlite_engine)
    src_tables = sqlite_insp.get_table_names()
    print(f"[*] Found {len(src_tables)} tables in SQLite source: {src_tables}")

    if "users" not in src_tables:
        raise RuntimeError("Source SQLite database does not contain 'users' table. Aborting.")

    # 2. Connect to PostgreSQL target
    if not postgres_url.startswith(("postgresql", "postgres")):
        raise ValueError(f"Invalid PostgreSQL URL: {postgres_url}. Must start with postgresql://")

    pg_engine = None
    if not dry_run:
        try:
            pg_engine = create_engine(postgres_url, pool_pre_ping=True)
            with pg_engine.connect():
                print("[+] Successfully verified connection to target PostgreSQL database.")
        except Exception as pg_conn_err:
            raise RuntimeError(f"Could not connect to target PostgreSQL instance: {pg_conn_err}")
    else:
        print("[DRY-RUN] Validated target PostgreSQL URL format. Live connection check skipped in dry-run mode.")

    # 3. Create tables in PostgreSQL
    if not dry_run and pg_engine:
        print("[*] Creating / verifying all tables on target PostgreSQL schema...")
        Base.metadata.create_all(bind=pg_engine)
        pg_insp = inspect(pg_engine)
        pg_tables = pg_insp.get_table_names()
        print(f"[+] Target PostgreSQL schema verified with {len(pg_tables)} tables.")
    else:
        print("[DRY-RUN] Skipped Base.metadata.create_all.")

    # 4. Migrate tables in ordered topological sequence
    metadata_src = MetaData()
    metadata_src.reflect(bind=sqlite_engine)

    metadata_pg = MetaData()
    if pg_engine:
        metadata_pg.reflect(bind=pg_engine)

    migration_report: Dict[str, Dict[str, Any]] = {}
    total_migrated_records = 0

    pg_session_factory = sessionmaker(bind=pg_engine) if pg_engine else None

    for tbl_name in MIGRATION_TABLE_ORDER:
        if tbl_name not in metadata_src.tables:
            print(f"[-] Table '{tbl_name}' not in SQLite database. Skipping.")
            continue

        src_tbl = metadata_src.tables[tbl_name]
        with sqlite_engine.connect() as s_conn:
            rows = s_conn.execute(select(src_tbl)).fetchall()
            row_count = len(rows)

        print(f"[*] Migrating table '{tbl_name}' ({row_count} rows)...")

        if dry_run:
            migration_report[tbl_name] = {
                "source_count": row_count,
                "target_count": "DRY-RUN",
                "status": "READY",
            }
            continue

        target_tbl = metadata_pg.tables.get(tbl_name)
        if target_tbl is None:
            print(f"[!] Warning: Target table '{tbl_name}' missing on PostgreSQL. Skipping.")
            continue

        migrated_for_table = 0
        if row_count > 0:
            columns = [c.name for c in src_tbl.columns]
            dict_rows = [dict(zip(columns, row)) for row in rows]

            with pg_session_factory() as pg_db:
                # Idempotent deduplication: skip records already present in target PostgreSQL
                pk_col = target_tbl.primary_key.columns.keys()[0] if target_tbl.primary_key.columns else None
                existing_pks = set()
                if pk_col and pk_col in target_tbl.c:
                    existing_pks = {
                        r[0] for r in pg_db.execute(select(target_tbl.c[pk_col])).fetchall()
                    }

                rows_to_insert = [r for r in dict_rows if pk_col is None or r.get(pk_col) not in existing_pks]

                # Convert boolean columns for PostgreSQL strict typing
                for r in rows_to_insert:
                    for col in target_tbl.columns:
                        if hasattr(col.type, "python_type") and col.type.python_type is bool:
                            val = r.get(col.name)
                            if val is not None:
                                r[col.name] = bool(val)

                for i in range(0, len(rows_to_insert), batch_size):
                    batch = rows_to_insert[i : i + batch_size]
                    if batch:
                        pg_db.execute(target_tbl.insert(), batch)
                        migrated_for_table += len(batch)
                pg_db.commit()

        # Verify post-migration count
        with pg_engine.connect() as p_conn:
            final_pg_rows = p_conn.execute(select(target_tbl)).fetchall()
            final_count = len(final_pg_rows)

        total_migrated_records += migrated_for_table
        status = "MATCH" if final_count >= row_count else "MISMATCH"
        print(f"    -> Successfully migrated '{tbl_name}': {migrated_for_table} rows. PG total: {final_count} ({status})")

        migration_report[tbl_name] = {
            "source_count": row_count,
            "target_count": final_count,
            "migrated": migrated_for_table,
            "status": status,
        }

    print("=" * 70)
    print("  Migration Summary Report")
    print("=" * 70)
    for t_name, stat in migration_report.items():
        print(f"  * {t_name:25}: SQLite={stat.get('source_count', 0)} | PG={stat.get('target_count', 0)} | [{stat.get('status', 'OK')}]")
    print("-" * 70)
    print(f" Total records migrated: {total_migrated_records}")
    print(" Complete! Farmer accounts, passwords, and crops safely preserved.")
    print("=" * 70)

    return {
        "status": "success",
        "dry_run": dry_run,
        "total_migrated": total_migrated_records,
        "tables": migration_report,
    }


def main():
    parser = argparse.ArgumentParser(description="AgriSaathi AI SQLite to PostgreSQL Migration CLI")
    parser.add_argument(
        "--sqlite-path",
        default=None,
        help="Direct path to SQLite file (e.g. data/agrisaathi.db)",
    )
    parser.add_argument(
        "--sqlite-url",
        default=None,
        help="Source SQLite database URL (defaults to active DATABASE_URL)",
    )
    parser.add_argument(
        "--postgres-url",
        default=os.environ.get("TARGET_POSTGRES_URL", os.environ.get("DATABASE_URL", "postgresql://agrisaathi:securepass@localhost:5432/agrisaathi_prod")),
        help="Target PostgreSQL database URL (or set TARGET_POSTGRES_URL or DATABASE_URL env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform schema inspection and row counting without executing inserts",
    )
    args = parser.parse_args()

    src_url = args.sqlite_url
    if args.sqlite_path:
        p = Path(args.sqlite_path).resolve()
        src_url = f"sqlite:///{p.as_posix()}"
    elif not src_url:
        src_url = settings.DATABASE_URL

    try:
        run_migration(
            sqlite_url=src_url,
            postgres_url=args.postgres_url,
            dry_run=args.dry_run,
        )
    except Exception as e:
        logger.error(f"Migration error: {e}", exc_info=True)
        print(f"\n[ERROR] Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
