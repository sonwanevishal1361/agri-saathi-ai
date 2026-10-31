"""Central authentication and authorization enforcement service."""

from typing import Optional
from dataclasses import dataclass
from core.exceptions import AuthorizationError


@dataclass
class AuthenticatedFarmer:
    """Authenticated user/farmer session identity."""
    id: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    preferred_language: str
    state: Optional[str]
    district: Optional[str]
    village: Optional[str]
    is_active: bool
    role: str = "farmer"  # "farmer" or "admin"

    @property
    def is_admin(self) -> bool:
        """Return True if user possesses administrator role."""
        return self.role == "admin"


# Alias for general user session
AuthenticatedUser = AuthenticatedFarmer


def require_admin(user: Optional[AuthenticatedFarmer]) -> None:
    """Enforce administrator role for protected developer/admin operations.

    Raises AuthorizationError if the user is unauthenticated or not an administrator.
    """
    if not user:
        raise AuthorizationError("Authentication required. Please log in as an administrator.")
    if user.role != "admin":
        raise AuthorizationError("Access denied. Developer / Administrator privileges required.")


def verify_farmer_ownership(current_farmer_id: str, resource_farmer_id: str, resource_name: str = "Record") -> None:
    """Enforce strict per-user authorization boundaries.

    Raises AuthorizationError if the resource owner does not match the current farmer.
    """
    if not current_farmer_id or not resource_farmer_id:
        raise AuthorizationError(f"Unauthorized access to {resource_name}: Invalid credentials.")
    if str(current_farmer_id) != str(resource_farmer_id):
        raise AuthorizationError(f"Access denied: You do not own this {resource_name}.")
