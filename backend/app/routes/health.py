from fastapi import APIRouter

from app.config import settings
from app.database.connection import check_database_connection

router = APIRouter()


@router.get("/health")
def get_health() -> dict:
    database_ready = check_database_connection()
    return {
        "status": "ok",
        "database": "connected" if database_ready else "unavailable",
        "ai_provider": settings.ai_provider,
        "ai_configured": bool(settings.ai_api_key),
    }
