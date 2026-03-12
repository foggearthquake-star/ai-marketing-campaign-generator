"""Application configuration."""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load variables from .env into process environment.
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _default_openai_base_url(api_key: str | None) -> str:
    """Return provider base URL based on key prefix unless overridden by env."""
    if api_key and api_key.startswith("pza_"):
        return "https://polza.ai/api/v1"
    return "https://api.openai.com/v1"


OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", _default_openai_base_url(OPENAI_API_KEY))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseModel):
    """Runtime settings for MVP."""

    app_name: str = os.getenv("APP_NAME", "AI Campaign MVP")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    openai_api_key: str | None = OPENAI_API_KEY
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: _split_csv(os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"))
    )
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))


settings = Settings()
