"""Custom exception classes for AgriSaathi AI."""


class AgriSaathiError(Exception):
    """Base application exception."""

    def __init__(self, message: str = "An application error occurred"):
        super().__init__(message)
        self.message = message


class AuthenticationError(AgriSaathiError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(AgriSaathiError):
    """Raised when a farmer attempts to access another farmer's private data."""
    pass


class NotFoundError(AgriSaathiError):
    """Raised when a requested resource does not exist."""
    pass


class ValidationError(AgriSaathiError):
    """Raised when input validation fails."""
    pass


class DuplicateRecordError(AgriSaathiError):
    """Raised when attempting to create a duplicate record."""
    pass


class AIInferenceError(AgriSaathiError):
    """Raised when Ollama inference fails or is unavailable."""
    pass


class ServiceUnavailableError(AgriSaathiError):
    """Raised when an external service (weather, mandi) is unreachable."""
    pass


class ConfigurationError(AgriSaathiError):
    """Raised when required configuration or API credentials are missing."""
    pass
