"""Structured logging configuration and Sentry integration for AgriSaathi AI."""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from config import BASE_DIR

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "agrisaathi.log"


class JsonLogFormatter(logging.Formatter):
    """Structured JSON formatter for production and cloud environments."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def init_sentry() -> bool:
    """Initialize Sentry error tracking if SENTRY_DSN is configured in environment."""
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if not dsn:
        try:
            from config import settings
            dsn = getattr(settings, "SENTRY_DSN", "").strip()
        except Exception:
            pass

    if not dsn:
        return False

    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", 0.2)),
            environment=os.environ.get("APP_ENV", "production"),
            release="agrisaathi@1.0.0",
        )
        logging.getLogger("agrisaathi").info("Sentry error monitoring successfully initialized.")
        return True
    except ImportError:
        logging.getLogger("agrisaathi").warning("sentry-sdk not installed; skipping Sentry initialization.")
        return False
    except Exception as e:
        logging.getLogger("agrisaathi").warning(f"Could not initialize Sentry: {e}")
        return False


def setup_logger(name: str = "agrisaathi") -> logging.Logger:
    """Configure and return application logger with structured formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level_str, logging.INFO))

        use_json = os.environ.get("LOG_FORMAT", "").lower() == "json"
        if use_json:
            formatter = JsonLogFormatter()
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        # Console handler with safe UTF-8 / replacement handling for Windows consoles
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


logger = setup_logger()
init_sentry()
