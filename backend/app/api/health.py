"""
Health Endpoint Router.
"""

from fastapi import APIRouter
from app.config import settings
from backend.app.schemas.common import APIResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=APIResponse[dict])
def health_check():
    """System Health Endpoint."""
    return APIResponse(
        success=True,
        data={
            "status": "HEALTHY",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "currency": settings.currency,
        },
    )
