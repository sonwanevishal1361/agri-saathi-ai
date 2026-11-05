"""Core configuration bridge for AgriSaathi AI.

Re-exports application settings, key resolution functions, and security redaction utilities.
"""

from config import (
    Settings,
    settings,
    get_data_gov_api_key,
    is_mandi_api_configured,
    redact,
    BASE_DIR,
)

__all__ = [
    "Settings",
    "settings",
    "get_data_gov_api_key",
    "is_mandi_api_configured",
    "redact",
    "BASE_DIR",
]
