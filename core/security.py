"""Security module providing Argon2id password hashing and session utilities."""

import re
import secrets
from typing import Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from core.exceptions import ValidationError

# Argon2id password hasher with standard secure parameters
_ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,  # 64 MB
    parallelism=1,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    if not plain_password:
        raise ValidationError("Password cannot be empty.")
    return _ph.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2id hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return _ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def validate_password_strength(password: str) -> None:
    """Validate minimum password requirements for standard users."""
    if not password or len(password.strip()) < 6:
        raise ValidationError("Password must be at least 6 characters long.")


def validate_password_policy(password: str, min_length: int = 8) -> Tuple[bool, str]:
    """Validate strict enterprise password policy for administrator accounts.

    Requirements:
    - Minimum length (default 8 characters)
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one number (0-9)
    - At least one special character (!@#$%^&*...)
    """
    if not password or len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit (0-9)."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character (!@#$%^&*...)."
    return True, ""


def generate_session_token() -> str:
    """Generate a secure cryptographic session token."""
    return secrets.token_urlsafe(32)
