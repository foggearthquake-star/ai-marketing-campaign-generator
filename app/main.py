"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.init_db import init_db
from app.routers import analytics, campaigns, health, projects

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize app-wide resources."""
    setup_logging()
    init_db()


app.include_router(health.router)
app.include_router(campaigns.router)
app.include_router(projects.router)
app.include_router(analytics.router)
