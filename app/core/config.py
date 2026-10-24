# app/core/config.py

from pydantic_settings import BaseSettings
# pydantic_settings: an extension of Pydantic that reads
# values from your .env file automatically

from functools import lru_cache
# lru_cache: "Least Recently Used cache" — a decorator that
# makes a function run only ONCE and remember its result
# forever, instead of re-running every time it's called

class Settings(BaseSettings):
    """
    Single source of truth for all configuration.
    If a setting is missing from .env, the app refuses to start.
    That's intentional — silent misconfiguration is dangerous.
    """

    # --- AI Model Settings ---
    GEMINI_API_KEY: str               # Required, no default
    PRIMARY_MODEL: str = "gemini-2.0-flash"
    FALLBACK_MODEL: str = "claude-sonnet-4-6"  # For complex tasks later

    # --- App Settings ---
    APP_NAME: str = "AI Expense Tracker"
    DEBUG: bool = False               # Never True in production
    DEFAULT_CURRENCY: str = "PKR"    # Pakistan-specific default
    DEFAULT_TIMEZONE: str = "Asia/Karachi"

    # --- Extraction Settings ---
    MIN_CONFIDENCE_THRESHOLD: float = 0.70
    # Any extraction below 70% confidence gets flagged for human review

    MAX_INPUT_LENGTH: int = 2000
    # Prevents prompt injection attacks — explained in Milestone 6

    class Config:
        env_file = ".env"             # Read from this file
        case_sensitive = True         # GEMINI_API_KEY ≠ gemini_api_key


@lru_cache()
def get_settings() -> Settings:
    """
    Returns the same Settings instance every time.
    lru_cache ensures we read the .env file exactly once,
    not on every single API request.
    """
    return Settings()