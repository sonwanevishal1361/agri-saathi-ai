"""Central authentication and authorization enforcement service."""

from typing import Optional
from dataclasses import dataclass
from core.exceptions import AuthorizationError


@dataclass
class AuthenticatedFarmer:
    """Authenticated farmer session identity."""
    id: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    preferred_language: str
    state: Optional[str]
    district: Optional[str]
    village: Optional[str]
    is_active: bool


def verify_farmer_ownership(current_farmer_id: str, resource_farmer_id: str, resource_name: str = "Record") -> None:
    """Enforce strict per-user authorization boundaries.

    Raises AuthorizationError if the resource owner does not match the current farmer.
    """
    if not current_farmer_id or not resource_farmer_id:
        raise AuthorizationError(f"Unauthorized access to {resource_name}: Invalid credentials.")
    if str(current_farmer_id) != str(resource_farmer_id):
        raise AuthorizationError(f"Access denied: You do not own this {resource_name}.")
