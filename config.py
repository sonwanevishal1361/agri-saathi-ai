"""Configuration module for AgriSaathi AI.

Loads application settings with validation and environment variable overrides.
"""

from pathlib import Path
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """AgriSaathi application configuration."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "AgriSaathi AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key-agrisaathi-farmer-companion-2026"
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "mr", "hi"]

    # Developer / Admin Credentials (Configurable via .env)
    ADMIN_DEFAULT_EMAIL: str = "admin@agrisaathi.com"
    ADMIN_DEFAULT_PHONE: str = "9999999999"
    ADMIN_DEFAULT_PASSWORD: str = "Admin@Agri2026!"

    # Database
    DATABASE_URL: str = Field(
        default=f"sqlite:///{(BASE_DIR / 'data' / 'agrisaathi.db').as_posix()}",
        description="SQLAlchemy database URL",
    )

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Ensure SQLite database URLs resolve to an absolute, normalized path."""
        if v.startswith("sqlite:///"):
            raw_path = v[len("sqlite:///"):]
            # Check if relative
            p = Path(raw_path)
            if not p.is_absolute():
                abs_path = (BASE_DIR / p).resolve()
                return f"sqlite:///{abs_path.as_posix()}"
        return v

    # AI Provider Settings
    AI_PROVIDER: str = "gemini"  # "gemini" (recommended) or "ollama"
    ENABLE_OLLAMA_FALLBACK: bool = False  # Avoid slow Ollama fallback unless explicitly enabled

    # Google Gemini API
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_OUTPUT_TOKENS: int = 1000
    GEMINI_TIMEOUT_SECONDS: int = 30

    # Local Ollama (Secondary / Offline Fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    OLLAMA_TIMEOUT_SECONDS: int = 180
    OLLAMA_TEMPERATURE: float = 0.3
    OLLAMA_NUM_CTX: int = 2048
    OLLAMA_NUM_PREDICT: int = 350
    OLLAMA_TOP_K: int = 20
    OLLAMA_TOP_P: float = 0.8
    MAX_CHAT_HISTORY: int = 4

    # Uploads
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg"]
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"

    # External APIs (Optional)
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    WEATHER_API_KEY: str = ""
    DATA_GOV_API_KEY: str = ""
    DATA_GOV_IN_API_KEY: str = ""  # Backward compatibility alias
    MANDI_CACHE_TTL_MINUTES: int = 60
    MANDI_MAX_RECORDS: int = 100

    @property
    def data_gov_key(self) -> str:
        """Return active data.gov.in API key from either setting."""
        return self.DATA_GOV_API_KEY or self.DATA_GOV_IN_API_KEY

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()

# Ensure application and database directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)

if settings.DATABASE_URL.startswith("sqlite"):
    try:
        raw_db_path = settings.DATABASE_URL.replace("sqlite:///", "", 1)
        if raw_db_path.startswith("/") and len(raw_db_path) > 2 and raw_db_path[2] == ":":
            raw_db_path = raw_db_path[1:]
        Path(raw_db_path).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
