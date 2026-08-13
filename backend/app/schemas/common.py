"""
Common Pydantic Schemas.
"""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[APIError] = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
