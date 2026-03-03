"""Application configuration."""

import os

from dotenv import load_dotenv
from pydantic import BaseModel

# Load variables from .env into process environment.
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")


class Settings(BaseModel):
    """Runtime settings for MVP."""

    app_name: str = os.getenv("APP_NAME", "AI Campaign MVP")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    openai_api_key: str | None = OPENAI_API_KEY


settings = Settings()
