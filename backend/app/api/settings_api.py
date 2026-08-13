"""
Settings API Router.
"""

from fastapi import APIRouter
from app.config import settings
from backend.app.schemas.common import APIResponse

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=APIResponse[dict])
def get_settings_info():
    """Retrieve system settings and environment parameters."""
    return APIResponse(
        success=True,
        data={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "currency": settings.currency,
            "database_path": str(settings.database_path),
            "log_level": settings.log_level,
            "llm_provider": settings.llm_provider,
            "llm_model": settings.llm_model,
            "ollama_base_url": settings.ollama_base_url,
            "ml_model_path": str(settings.ml_model_path),
            "anomaly_contamination": settings.anomaly_contamination,
        },
    )
