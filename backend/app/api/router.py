"""
Central API Router aggregation.
"""

from fastapi import APIRouter

from backend.app.api.health import router as health_router
from backend.app.api.expenses import router as expenses_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.intelligence import router as intelligence_router
from backend.app.api.ml import router as ml_router
from backend.app.api.ai import router as ai_router
from backend.app.api.settings_api import router as settings_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(expenses_router)
api_router.include_router(analytics_router)
api_router.include_router(intelligence_router)
api_router.include_router(ml_router)
api_router.include_router(ai_router)
api_router.include_router(settings_router)
