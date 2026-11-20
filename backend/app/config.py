"""Environment-backed settings for the ROSE API."""
from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _read_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    database_host: str = os.getenv("DATABASE_HOST", "127.0.0.1")
    database_port: int = int(os.getenv("DATABASE_PORT", "3306"))
    database_name: str = os.getenv("DATABASE_NAME", "rose_db")
    database_user: str = os.getenv("DATABASE_USER", "root")
    database_password: str = os.getenv("DATABASE_PASSWORD", "")
    ai_provider: str = os.getenv("AI_PROVIDER", "gemini").strip().lower()
    ai_api_key: str = os.getenv("AI_API_KEY", "").strip()
    ai_model: str = os.getenv("AI_MODEL", "gemini-3.8-flash").strip()
    frontend_origins: tuple[str, ...] = tuple(
        _read_origins(os.getenv("FRONTEND_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500"))
    )
    max_context_messages: int = 30


settings = Settings()
