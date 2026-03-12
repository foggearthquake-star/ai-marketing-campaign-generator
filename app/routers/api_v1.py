"""API v1 aggregate router."""

from fastapi import APIRouter

from app.routers.v1 import analyses, auth, campaigns, jobs, projects, usage, users, workspaces

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(workspaces.router)
router.include_router(projects.router)
router.include_router(analyses.router)
router.include_router(campaigns.router)
router.include_router(jobs.router)
router.include_router(usage.router)
router.include_router(users.router)
