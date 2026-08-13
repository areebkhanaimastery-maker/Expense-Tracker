"""
Expenses API Router.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.validators import CATEGORIES
from app.exceptions import ExpenseNotFoundError, ValidationError
from backend.app.deps import get_expense_service
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.schemas.expense import (
    CreateExpenseRequest,
    UpdateExpenseRequest,
    ExpenseResponse,
)

router = APIRouter(prefix="", tags=["Expenses"])


def _to_expense_response(expense) -> ExpenseResponse:
    date_str = expense.date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(expense.date, "strftime") else str(expense.date)
    return ExpenseResponse(
        id=expense.id,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=date_str,
    )


@router.get("/expenses", response_model=APIResponse[PaginatedResponse[ExpenseResponse]])
def list_expenses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    service=Depends(get_expense_service),
):
    """Retrieve expenses with optional filtering, search, and pagination."""
    all_expenses = service.get_all_expenses()

    # Filtering
    filtered = all_expenses
    if category:
        filtered = [e for e in filtered if e.category.lower() == category.lower()]
    if search:
        search_lower = search.lower()
        filtered = [
            e for e in filtered
            if search_lower in e.description.lower() or search_lower in e.category.lower()
        ]
    if min_amount is not None:
        filtered = [e for e in filtered if e.amount >= min_amount]
    if max_amount is not None:
        filtered = [e for e in filtered if e.amount <= max_amount]
    if start_date:
        filtered = [e for e in filtered if str(e.date) >= start_date]
    if end_date:
        filtered = [e for e in filtered if str(e.date) <= end_date]

    # Sort descending by date/id
    filtered = sorted(filtered, key=lambda e: (str(e.date), e.id or 0), reverse=True)

    total = len(filtered)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = filtered[start_idx:end_idx]

    items = [_to_expense_response(e) for e in page_items]

    return APIResponse(
        success=True,
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get("/expenses/{expense_id}", response_model=APIResponse[ExpenseResponse])
def get_expense(expense_id: int, service=Depends(get_expense_service)):
    """Retrieve a single expense by ID."""
    try:
        expense = service.get_expense(expense_id)
        return APIResponse(success=True, data=_to_expense_response(expense))
    except ExpenseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EXPENSE_NOT_FOUND", "message": str(e)},
        )


@router.post("/expenses", response_model=APIResponse[ExpenseResponse], status_code=status.HTTP_201_CREATED)
def create_expense(req: CreateExpenseRequest, service=Depends(get_expense_service)):
    """Create a new expense transaction."""
    try:
        expense = service.add_expense(
            amount=req.amount,
            category=req.category,
            description=req.description,
            date_str=req.date,
        )
        return APIResponse(success=True, data=_to_expense_response(expense))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(e)},
        )


@router.put("/expenses/{expense_id}", response_model=APIResponse[ExpenseResponse])
def update_expense(
    expense_id: int, req: UpdateExpenseRequest, service=Depends(get_expense_service)
):
    """Update an existing expense transaction."""
    try:
        expense = service.edit_expense(
            expense_id=expense_id,
            amount=req.amount,
            category=req.category,
            description=req.description,
            date_str=req.date,
        )
        return APIResponse(success=True, data=_to_expense_response(expense))
    except ExpenseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EXPENSE_NOT_FOUND", "message": str(e)},
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(e)},
        )


@router.delete("/expenses/{expense_id}", response_model=APIResponse[dict])
def delete_expense(expense_id: int, service=Depends(get_expense_service)):
    """Delete an expense transaction."""
    try:
        service.delete_expense(expense_id)
        return APIResponse(success=True, data={"message": f"Expense {expense_id} deleted successfully."})
    except ExpenseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EXPENSE_NOT_FOUND", "message": str(e)},
        )


@router.get("/categories", response_model=APIResponse[list[str]])
def get_categories():
    """Retrieve list of all valid expense categories."""
    return APIResponse(success=True, data=CATEGORIES)


@router.get("/search", response_model=APIResponse[list[ExpenseResponse]])
def search_expenses(query: str = Query(..., min_length=1), service=Depends(get_expense_service)):
    """Search expenses by keyword in description or category."""
    results = service.search(query)
    return APIResponse(success=True, data=[_to_expense_response(e) for e in results])


@router.get("/filter", response_model=APIResponse[list[ExpenseResponse]])
def filter_expenses(
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    service=Depends(get_expense_service),
):
    """Filter expenses by category or amount range."""
    filtered = service.get_all_expenses()
    if category:
        filtered = [e for e in filtered if e.category.lower() == category.lower()]
    if min_amount is not None:
        filtered = [e for e in filtered if e.amount >= min_amount]
    if max_amount is not None:
        filtered = [e for e in filtered if e.amount <= max_amount]

    return APIResponse(success=True, data=[_to_expense_response(e) for e in filtered])
