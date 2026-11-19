# app/core/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Single source of truth for configuration, loaded from .env.
    Only GEMINI_API_KEY and DATABASE_URL are required. Everything else
    has a sensible default so the app starts from a minimal .env.
    A missing required value makes the app refuse to start, which is
    intentional: silent misconfiguration is worse than a loud failure.
    """

    # AI model settings
    GEMINI_API_KEY: str                       # required
    PRIMARY_MODEL: str = "gemini-3.5-flash"
    OPEN_ROUTER_KEY: str = ""                 # only needed for the OpenRouter client
    SECONDARY_MODEL: str = ""                 # reserved for a future fallback chain
    FALLBACK_MODEL: str = ""                  # reserved for a future fallback chain

    # Database
    DATABASE_URL: str                         # required, e.g. postgresql+asyncpg://user:pass@host/db

    # App settings
    APP_NAME: str = "AI Expense Tracker"
    DEBUG: bool = False
    DEFAULT_CURRENCY: str = "PKR"
    DEFAULT_TIMEZONE: str = "Asia/Karachi"

    # Extraction settings
    MIN_CONFIDENCE_THRESHOLD: float = 0.70    # below this, a record is flagged for review
    MAX_INPUT_LENGTH: int = 2000

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Read and cache the settings once, not on every request."""
    return Settings()