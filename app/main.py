"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware, SecurityHeadersMiddleware, SimpleRateLimitMiddleware
from app.db.init_db import init_db
from app.routers import analyses, analytics, campaigns, health, projects
from app.routers.api_v1 import router as api_v1_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize app-wide resources."""
    setup_logging()
    init_db()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SimpleRateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)
register_exception_handlers(app)

# Legacy routes kept for backward compatibility.
app.include_router(health.router)
app.include_router(campaigns.router)
app.include_router(campaigns.history_router)
app.include_router(projects.router)
app.include_router(analytics.router)
app.include_router(analyses.router)

# New versioned market-ready API.
app.include_router(api_v1_router)
