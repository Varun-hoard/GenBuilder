"""
GenBuilder — Application Configuration

Centralizes all application settings using pydantic-settings.
Values are loaded from environment variables or an .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application-wide configuration sourced from environment variables."""

    # ── Application ───────────────────────────────────
    APP_NAME: str = "GenBuilder"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── OpenAI / LLM ─────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "gpt-4o"

    # ── AWS ───────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "genbuilder-outputs"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton per process)."""
    return Settings()
