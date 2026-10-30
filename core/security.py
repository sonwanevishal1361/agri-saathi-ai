"""Security module providing Argon2id password hashing and session utilities."""

import secrets
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
    """Validate minimum password requirements."""
    if not password or len(password.strip()) < 6:
        raise ValidationError("Password must be at least 6 characters long.")


def generate_session_token() -> str:
    """Generate a secure cryptographic session token."""
    return secrets.token_urlsafe(32)
