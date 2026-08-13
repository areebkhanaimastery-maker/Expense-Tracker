"""
FastAPI Application Entry Point.
"""

import sys
from pathlib import Path

# Add project root to sys.path if not present
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import ExpenseTrackerError, ExpenseNotFoundError, ValidationError
from backend.app.api.router import api_router
from backend.app.schemas.common import APIResponse, APIError

app = FastAPI(
    title=f"{settings.app_name} API",
    version=settings.app_version,
    description="Full-Stack Expense Intelligence Platform Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ExpenseNotFoundError)
async def expense_not_found_handler(request: Request, exc: ExpenseNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=APIResponse(
            success=False,
            error=APIError(code="EXPENSE_NOT_FOUND", message=str(exc)),
        ).model_dump(),
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=APIResponse(
            success=False,
            error=APIError(code="VALIDATION_ERROR", message=str(exc)),
        ).model_dump(),
    )


@app.exception_handler(ExpenseTrackerError)
async def expense_tracker_error_handler(request: Request, exc: ExpenseTrackerError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            error=APIError(code="INTERNAL_ERROR", message=str(exc)),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            error=APIError(code="SERVER_ERROR", message=f"Internal server error: {exc}"),
        ).model_dump(),
    )


# Mount API Router
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
    }
