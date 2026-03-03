"""Campaign endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/")
def list_campaigns() -> dict[str, str]:
    """Placeholder endpoint for campaigns."""
    return {"message": "Campaign endpoints are not implemented yet."}
