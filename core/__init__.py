"""Core module providing database, security, and authentication."""

from core.database import Base, get_db, init_db, drop_db, engine, SessionLocal
from core.security import hash_password, verify_password, validate_password_strength, generate_session_token
from core.auth import AuthenticatedFarmer, verify_farmer_ownership
from core.exceptions import (
    AgriSaathiError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    AIInferenceError,
    ServiceUnavailableError,
)

__all__ = [
    "Base",
    "get_db",
    "init_db",
    "drop_db",
    "engine",
    "SessionLocal",
    "hash_password",
    "verify_password",
    "validate_password_strength",
    "generate_session_token",
    "AuthenticatedFarmer",
    "verify_farmer_ownership",
    "AgriSaathiError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "AIInferenceError",
    "ServiceUnavailableError",
]
