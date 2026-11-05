"""Script to provision an administrator account securely.

Creates an admin account from environment variables (ADMIN_EMAIL, ADMIN_PASSWORD)
or CLI arguments, enforcing a strict password policy and mandatory password change on first login.
"""

import argparse
import getpass
import os
import sys
from pathlib import Path

# Ensure root workspace directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy.orm import Session  # noqa: E402
from core.database import get_db, init_db  # noqa: E402
from core.security import hash_password, validate_password_policy  # noqa: E402
from models.user import User  # noqa: E402


def provision_admin(
    email: str,
    password: str,
    full_name: str = "AgriSaathi Administrator",
    phone: str = None,
    db: Session = None,
) -> User:
    """Create or promote a user to administrator with forced password change on first login."""
    email_clean = (email or "").strip().lower()
    if not email_clean:
        raise ValueError("Admin email cannot be empty.")

    is_valid, policy_err = validate_password_policy(password)
    if not is_valid:
        raise ValueError(f"Password does not satisfy security policy: {policy_err}")

    def _execute(session: Session) -> User:
        user = session.query(User).filter(User.email == email_clean).first()
        if user:
            print(f"[*] Found existing account for {email_clean} (ID: {user.id}). Promoting to administrator...")
            user.role = "admin"
            user.password_hash = hash_password(password)
            user.must_change_password = True
            user.failed_login_attempts = 0
            user.locked_until = None
            if full_name:
                user.full_name = full_name
            if phone:
                user.phone = phone
            session.commit()
            session.refresh(user)
            print(f"[+] Administrator account successfully updated for {email_clean} (forced password change enabled).")
            return user

        # Create new admin user
        admin = User(
            full_name=full_name or "AgriSaathi Administrator",
            email=email_clean,
            phone=phone,
            password_hash=hash_password(password),
            role="admin",
            must_change_password=True,
            is_active=True,
            preferred_language="en",
            state="Maharashtra",
            district="Pune",
            village="Headquarters",
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        print(f"[+] Administrator account successfully created: {admin.email} (ID: {admin.id})")
        print("[+] Policy enforced: Administrator must change password upon first login.")
        return admin

    if db is not None:
        return _execute(db)

    init_db()
    with get_db() as session:
        return _execute(session)


def main():
    parser = argparse.ArgumentParser(description="Create or provision an AgriSaathi AI Administrator.")
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL"), help="Admin email (or via ADMIN_EMAIL env var)")
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD"), help="Admin password (or via ADMIN_PASSWORD env var)")
    parser.add_argument("--name", default=os.getenv("ADMIN_NAME", "Platform Administrator"), help="Admin full name")
    parser.add_argument("--phone", default=os.getenv("ADMIN_PHONE"), help="Admin contact phone")

    args = parser.parse_args()

    email = args.email
    password = args.password

    if not email:
        if sys.stdin.isatty():
            email = input("Enter admin email: ").strip()
        else:
            print("Error: Admin email must be provided via --email flag or ADMIN_EMAIL environment variable.", file=sys.stderr)
            sys.exit(1)

    if not password:
        if sys.stdin.isatty():
            password = getpass.getpass("Enter admin password: ").strip()
        else:
            print("Error: Admin password must be provided via --password flag or ADMIN_PASSWORD environment variable.", file=sys.stderr)
            sys.exit(1)

    try:
        provision_admin(
            email=email,
            password=password,
            full_name=args.name,
            phone=args.phone,
        )
    except Exception as exc:
        print(f"Error provisioning administrator: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
