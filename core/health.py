"""Health check module providing system component diagnostics and /health status."""

import shutil
import time
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import text
from config import settings
from core.database import get_db
from services.gemini_service import gemini_service
from services.ollama_service import ollama_service


def check_system_health() -> Dict[str, Any]:
    """Perform diagnostics across database, AI services, and disk storage."""
    health: Dict[str, Any] = {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {},
    }

    # 1. Database Connectivity Check
    t0 = time.perf_counter()
    try:
        with get_db() as db:
            result = db.execute(text("SELECT 1")).scalar()
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            db_status = "healthy" if result == 1 else "degraded"
            health["components"]["database"] = {
                "status": db_status,
                "latency_ms": latency_ms,
                "engine": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql",
            }
            if db_status != "healthy":
                health["status"] = "degraded"
    except Exception as db_err:
        health["status"] = "degraded"
        health["components"]["database"] = {
            "status": "unhealthy",
            "error": str(db_err),
        }

    # 2. AI Provider Status Check
    provider = settings.AI_PROVIDER
    if provider == "gemini":
        gemini_st = gemini_service.check_health()
        ai_healthy = bool(gemini_st.get("online"))
        health["components"]["ai_provider"] = {
            "provider": "gemini",
            "model": settings.GEMINI_MODEL,
            "status": "healthy" if ai_healthy else "degraded",
            "configured": gemini_st.get("configured", False),
            "message": gemini_st.get("message", ""),
        }
    else:
        ollama_st = ollama_service.check_health()
        ai_healthy = bool(ollama_st.get("online"))
        health["components"]["ai_provider"] = {
            "provider": "ollama",
            "model": settings.OLLAMA_MODEL,
            "status": "healthy" if ai_healthy else "degraded",
            "message": ollama_st.get("message", ""),
        }

    # 3. Disk Storage Check
    try:
        total, used, free = shutil.disk_usage(settings.BASE_DIR)
        free_gb = round(free / (1024**3), 2)
        total_gb = round(total / (1024**3), 2)
        disk_status = "healthy" if free_gb > 0.5 else "warning"
        health["components"]["disk"] = {
            "status": disk_status,
            "free_gb": free_gb,
            "total_gb": total_gb,
        }
        if disk_status == "warning":
            health["status"] = "degraded"
    except Exception as disk_err:
        health["components"]["disk"] = {
            "status": "unknown",
            "error": str(disk_err),
        }

    return health


if __name__ == "__main__":
    import json
    print(json.dumps(check_system_health(), indent=2))

