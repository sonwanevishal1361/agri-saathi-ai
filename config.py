"""Configuration module for AgriSaathi AI.

Loads application settings with validation and environment variable overrides.
"""

import os
import re
from pathlib import Path
from typing import List, Any, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent


def _clean_key(val: Any) -> str:
    """Trim whitespace and surrounding quotes; return empty string if whitespace-only."""
    if val is None:
        return ""
    s = str(val).strip()
    # Strip matched surrounding single or double quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    return s


def get_data_gov_api_key() -> str:
    """Resolve Data.gov.in API key in strict resolution order:
    1. st.secrets["DATA_GOV_API_KEY"]
    2. env DATA_GOV_API_KEY
    3. st.secrets["DATA_GOV_IN_API_KEY"]
    4. env DATA_GOV_IN_API_KEY
    First non-empty wins. Whitespace and surrounding quotes are trimmed.
    Whitespace-only values count as empty.
    """
    # 1. st.secrets["DATA_GOV_API_KEY"]
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets is not None:
            if "DATA_GOV_API_KEY" in st.secrets:
                k1 = _clean_key(st.secrets["DATA_GOV_API_KEY"])
                if k1:
                    return k1
    except Exception:
        pass

    # 2. env DATA_GOV_API_KEY
    env_k1 = _clean_key(os.environ.get("DATA_GOV_API_KEY"))
    if env_k1:
        return env_k1

    # 3. st.secrets["DATA_GOV_IN_API_KEY"]
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets is not None:
            if "DATA_GOV_IN_API_KEY" in st.secrets:
                k2 = _clean_key(st.secrets["DATA_GOV_IN_API_KEY"])
                if k2:
                    return k2
    except Exception:
        pass

    # 4. env DATA_GOV_IN_API_KEY
    env_k2 = _clean_key(os.environ.get("DATA_GOV_IN_API_KEY"))
    if env_k2:
        return env_k2

    # 5. Fallback to settings object attribute if loaded/patched
    try:
        if "settings" in globals():
            s_obj = globals()["settings"]
            k_set = _clean_key(getattr(s_obj, "DATA_GOV_API_KEY", "")) or _clean_key(getattr(s_obj, "DATA_GOV_IN_API_KEY", ""))
            if k_set:
                return k_set
    except Exception:
        pass

    return ""


def is_mandi_api_configured() -> bool:
    """Return True if a non-empty Data.gov.in API key is configured."""
    return bool(get_data_gov_api_key())


def redact(text: Optional[str]) -> str:
    """Redact Data.gov.in API key and any api-key=... query parameters in text, logs, or URLs."""
    if not text:
        return ""
    s = str(text)
    active_key = get_data_gov_api_key()
    if active_key and active_key in s:
        s = s.replace(active_key, "***")

    # Also redact any api-key query param pattern: api-key=<anything>& or api_key=<anything>
    s = re.sub(r"(api[-_]key=)[^& \t\r\n\'\"]+", r"\1***", s, flags=re.IGNORECASE)
    return s


def _load_streamlit_secrets_into_env() -> None:
    """Safely populate os.environ from Streamlit Cloud Secrets (st.secrets) if present.

    Priority order:
    1. Streamlit Secrets (st.secrets) - takes highest precedence in cloud deployment
    2. Environment variables / .env file
    3. SQLite default for local development
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets is not None:
            # 1. DATABASE_URL priority from st.secrets
            secrets_db_url = None
            for key in ("DATABASE_URL", "database_url"):
                if key in st.secrets and str(st.secrets[key]).strip():
                    secrets_db_url = str(st.secrets[key]).strip()
                    break

            if not secrets_db_url:
                # Check nested sections like [postgres], [postgresql], [database], [db]
                for section in ("postgres", "postgresql", "database", "db"):
                    if section in st.secrets and isinstance(st.secrets[section], dict):
                        sec = st.secrets[section]
                        for sub in ("url", "database_url", "DATABASE_URL"):
                            if sub in sec and str(sec[sub]).strip():
                                secrets_db_url = str(sec[sub]).strip()
                                break
                        if secrets_db_url:
                            break

            if not secrets_db_url and "connections" in st.secrets and isinstance(st.secrets["connections"], dict):
                conns = st.secrets["connections"]
                for sub_sec in ("postgresql", "postgres"):
                    if sub_sec in conns and isinstance(conns[sub_sec], dict):
                        if "url" in conns[sub_sec] and str(conns[sub_sec]["url"]).strip():
                            secrets_db_url = str(conns[sub_sec]["url"]).strip()
                            break

            if secrets_db_url:
                os.environ["DATABASE_URL"] = secrets_db_url

            # Bridge DATA_GOV_API_KEY from st.secrets if non-empty
            if "DATA_GOV_API_KEY" in st.secrets:
                dg_val = _clean_key(st.secrets["DATA_GOV_API_KEY"])
                if dg_val:
                    os.environ["DATA_GOV_API_KEY"] = dg_val
            elif "DATA_GOV_IN_API_KEY" in st.secrets:
                dg_in_val = _clean_key(st.secrets["DATA_GOV_IN_API_KEY"])
                if dg_in_val:
                    os.environ["DATA_GOV_IN_API_KEY"] = dg_in_val

            # 2. Bridge other scalar secrets if not already in os.environ
            for key, val in st.secrets.items():
                if isinstance(val, (str, int, float, bool)) and key not in os.environ:
                    os.environ[key] = str(val)
                elif isinstance(val, dict):
                    for sub_key, sub_val in val.items():
                        env_key = f"{key.upper()}_{sub_key.upper()}"
                        if env_key not in os.environ and isinstance(sub_val, (str, int, float, bool)):
                            os.environ[env_key] = str(sub_val)
    except Exception:
        pass


# Ensure Streamlit Cloud secrets are bridged to environment variables before Settings loads
_load_streamlit_secrets_into_env()


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

    # Developer / Admin Credentials (Configurable via .env or scripts/create_admin.py)
    ADMIN_EMAIL: str = Field(default="sonwanevishal1361@gmail.com", description="Admin email for initial provisioning")
    ADMIN_PHONE: str = Field(default="1234567890", description="Admin phone for initial provisioning")
    ADMIN_PASSWORD: str = Field(default="vishal1361", description="Admin password for initial provisioning")

    # Security & Rate Limiting
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15
    AI_DAILY_REQUEST_LIMIT: int = Field(default=25, description="Daily limit for AI chat queries per farmer")

    # Database
    DATABASE_URL: str = Field(
        default=f"sqlite:///{(BASE_DIR / 'data' / 'agrisaathi.db').as_posix()}",
        description="SQLAlchemy database URL",
    )

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Ensure database URLs are normalized for SQLAlchemy 2.x and driver compatibility."""
        if not v:
            return f"sqlite:///{(BASE_DIR / 'data' / 'agrisaathi.db').as_posix()}"
        trimmed = v.strip()
        if trimmed.startswith("sqlite:///"):
            raw_path = trimmed[len("sqlite:///"):]
            if ":memory:" not in raw_path:
                p = Path(raw_path)
                if not p.is_absolute():
                    abs_path = (BASE_DIR / p).resolve()
                    return f"sqlite:///{abs_path.as_posix()}"
            return trimmed
        if trimmed.startswith("postgres://"):
            trimmed = "postgresql+psycopg://" + trimmed[len("postgres://"):]
        elif trimmed.startswith("postgresql+psycopg2://"):
            trimmed = "postgresql+psycopg://" + trimmed[len("postgresql+psycopg2://"):]
        elif trimmed.startswith("postgresql://"):
            trimmed = "postgresql+psycopg://" + trimmed[len("postgresql://"):]
        lower = trimmed.lower()
        if any(h in lower for h in ("neon.tech", "supabase.co", "supabase.com", "pooler.supabase")):
            if "sslmode=" not in lower:
                sep = "&" if "?" in trimmed else "?"
                trimmed = f"{trimmed}{sep}sslmode=require"
        return trimmed

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

    # Reliability, Observability & Error Monitoring
    SENTRY_DSN: str = Field(default="", description="Optional Sentry DSN for error monitoring")
    SENTRY_TRACES_SAMPLE_RATE: float = 0.2
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # "text" or "json"

    # External APIs (Optional)
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    WEATHER_API_KEY: str = ""
    DATA_GOV_API_KEY: str = ""
    DATA_GOV_IN_API_KEY: str = ""  # Backward compatibility alias
    MANDI_CACHE_TTL_MINUTES: int = 60
    MANDI_MAX_RECORDS: int = 100

    @property
    def data_gov_key(self) -> str:
        """Return active data.gov.in API key from unified resolution order."""
        resolved = get_data_gov_api_key()
        return resolved or self.DATA_GOV_API_KEY or self.DATA_GOV_IN_API_KEY

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
