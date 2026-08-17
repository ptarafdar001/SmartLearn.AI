from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "SmartLearn.AI API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Backend API for SmartLearn.AI – an adaptive learning platform"
    DEBUG: bool = False

    # ── Server ────────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./smartlearn.db"

    # ── External APIs (add keys as needed) ───────────────────────────────────
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env once at startup)."""
    return Settings()
