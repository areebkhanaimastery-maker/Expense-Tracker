"""
Expense Pydantic Schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators import CATEGORIES


class ExpenseBase(BaseModel):
    amount: float = Field(..., description="Expense amount", gt=0)
    category: str = Field(..., description="Expense category")
    description: str = Field(..., description="Expense description", min_length=1)
    date: str = Field(..., description="Expense date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)")

    @field_validator("category")
    def validate_category(cls, v: str) -> str:
        formatted = v.strip().capitalize()
        if formatted not in CATEGORIES:
            raise ValueError(f"Invalid category '{v}'. Must be one of: {', '.join(CATEGORIES)}")
        return formatted

    @field_validator("description")
    def validate_description(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Description cannot be empty or whitespace only.")
        if len(stripped) > 200:
            raise ValueError("Description must not exceed 200 characters.")
        return stripped


class CreateExpenseRequest(ExpenseBase):
    pass


class UpdateExpenseRequest(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

    @field_validator("category")
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        formatted = v.strip().capitalize()
        if formatted not in CATEGORIES:
            raise ValueError(f"Invalid category '{v}'. Must be one of: {', '.join(CATEGORIES)}")
        return formatted

    @field_validator("description")
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("Description cannot be empty or whitespace only.")
        if len(stripped) > 200:
            raise ValueError("Description must not exceed 200 characters.")
        return stripped


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: str
    date: str


class ExpenseFilterParams(BaseModel):
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
